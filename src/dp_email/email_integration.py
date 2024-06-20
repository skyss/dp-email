"""Integrations with Azure Email functionality."""

from collections.abc import MutableMapping
from dataclasses import asdict, dataclass
from typing import Any

from azure.communication.email import EmailClient
from azure.core.exceptions import HttpResponseError
from loguru import logger

from dp_email.secret_integration import get_secret

JSON = MutableMapping[str, Any]


@dataclass
class Content:
    """Content of an email."""

    subject: str
    plainText: str  # noqa: N815 - must match the API
    html: str


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
class Message:
    """Email message."""

    content: Content
    recipients: Recipients
    senderAddress: str  # noqa: N815 - must match the API


def get_email_client(connection_string: str) -> EmailClient:
    """Create an azure communication service email client."""
    if not connection_string:
        connection_string = get_secret(
            "https://kvsubdevndp.vault.azure.net/",
            "communication-service-endpoint",
        )
    return EmailClient.from_connection_string(connection_string)


def send_email(email_client: EmailClient, message: Message) -> str | JSON:
    """Send email via Azure Communication Service."""
    try:
        logger.info(f"Sending email via Azure Communication Service: {message=}")
        poller = email_client.begin_send(asdict(message))
        return poller.result()
    except HttpResponseError:
        logger.exception("Failed to send email via Azure Communication Service")
        return "Failed to send email via Azure Communication Service"
