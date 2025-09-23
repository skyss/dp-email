"""Integrations with Azure Email functionality."""

from collections.abc import MutableMapping
from dataclasses import asdict, dataclass
from typing import Any

from azure.communication.email import EmailClient
from azure.core.exceptions import HttpResponseError
from loguru import logger
from typing_extensions import Self  # noqa: UP035

from dp_email.secret_integration import get_secret

JSON = MutableMapping[str, Any]


@dataclass
class Content:
    """Content of an email."""

    def __post_init__(self: Self) -> None:  # noqa: D105
        if self.plainText is not None and self.html is not None:
            raise SetEitherHtmlOrPlainTextError

    subject: str
    plainText: str | None = None  # noqa: N815 - must match the API
    html: str | None = None


@dataclass
class Recipient:
    """Recipient of an email."""

    address: str
    displayName: str  # noqa: N815 - must match the API


@dataclass
class Recipients:
    """List of recipients of an email."""

    to: list[Recipient]


@dataclass
class Attachment:
    """Represents an email attachment structure, equal to what the API expects."""

    name: str
    contentInBase64: str  # noqa: N815 - must match the API
    contentType: str  # noqa: N815 - must match the API


@dataclass
class Message:
    """Email message.

    Note: The sender address must be a verified email address in the Azure Communication Service.
    """

    content: Content
    recipients: Recipients
    senderAddress: str  # noqa: N815 - must match the API
    attachments: list[Attachment] | None = None


def get_email_client(connection_string: str) -> EmailClient:
    """Create an azure communication service email client."""
    if not connection_string:
        connection_string = get_secret(
            "https://skyss-hub-keyvault.vault.azure.net/",
            "communication-service-endpoint",
        )
    return EmailClient.from_connection_string(connection_string)


def send_email(email_client: EmailClient, message: Message) -> str | JSON:
    """Send email via Azure Communication Service.

    See https://learn.microsoft.com/en-us/azure/communication-services/quickstarts/email/send-email-advanced/send-email-with-attachments?tabs=connection-string&pivots=programming-language-python.
    """
    try:
        logger.info(f"Sending email via Azure Communication Service: {message=}")
        # Remove any entries where the value of the Key is None
        filtered_message_dict = {k: v for k, v in asdict(message).items() if v is not None}
        poller = email_client.begin_send(filtered_message_dict)
        return poller.result()  # type: ignore [no-any-return]
    except HttpResponseError:
        logger.exception("Failed to send email via Azure Communication Service")
        return "Failed to send email via Azure Communication Service"


def build_message(
    subject: str,
    html: str,
    to_address: str,
    sender_address: str,
    plain_text: str | None = None,
) -> Message:
    """Build an email message.

    Helper function to build an email message.
    """
    return Message(
        content=Content(
            subject=subject,
            plainText=plain_text,
            html=html,
        ),
        recipients=Recipients(
            to=[Recipient(address=to_address, displayName=to_address)],
        ),
        senderAddress=sender_address,
    )


class SetEitherHtmlOrPlainTextError(Exception):
    """Represents an exception raised when an email has both plaintext and html set."""

    def __init__(  # noqa: D107
        self: Self,
        message: str = "Either plainText or html should be set, but not both.",
    ) -> None:
        super().__init__(message)
