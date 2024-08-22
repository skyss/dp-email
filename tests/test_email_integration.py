import base64
import os
from dataclasses import asdict
from pathlib import Path

import pytest
from loguru import logger

import dp_email.email_integration
from dp_email.email_integration import SetEitherHtmlOrPlainTextError


def test_that_message_converts_to_dict():
    expected_message = {
        "attachments": None,
        "content": {
            "html": None,
            "subject": "This is the subject",
            "plainText": "This is the body",
        },
        "recipients": {
            "to": [
                {
                    "address": "test@vlfk.no",
                    "displayName": "Test Testesen",
                },
            ],
        },
        "senderAddress": "DoNotReply@longguid.azurecomm.net",
    }

    message = dp_email.email_integration.Message(
        content=dp_email.email_integration.Content(
            subject="This is the subject",
            plainText="This is the body",
        ),
        recipients=dp_email.email_integration.Recipients(
            to=[dp_email.email_integration.Recipient(address="test@vlfk.no", displayName="Test Testesen")],
        ),
        senderAddress="DoNotReply@longguid.azurecomm.net",
        attachments=None,
    )

    assert expected_message == asdict(message)


def test_that_build_message_returns_message():
    message = dp_email.email_integration.build_message(
        subject="This is the subject",
        html="<html><h1>This is the body</h1></html>",
        to_address="test@vlfk.no",
        sender_address="DoNotReply@longguid.azurecomm.net",
    )

    assert isinstance(message, dp_email.email_integration.Message)
    assert message.content.subject == "This is the subject"
    assert message.content.html == "<html><h1>This is the body</h1></html>"


def test_that_build_message_with_attachments_returns_message():
    content_bytes_base64str = base64.b64encode(b"this is a test").decode("utf-8")
    message = dp_email.email_integration.Message(
        content=dp_email.email_integration.Content(
            subject="This is the subject",
            plainText="This is the body",
        ),
        recipients=dp_email.email_integration.Recipients(
            to=[dp_email.email_integration.Recipient(address="test@vlfk.no", displayName="Anders Rørvik")],
        ),
        senderAddress="DoNotReply@73a8fc69-ef8f-4d6a-ae4a-e46be871dce9.azurecomm.net",
        attachments=[
            dp_email.email_integration.Attachment(
                name="test.pdf",
                contentType="application/pdf",
                contentInBase64=content_bytes_base64str,
            ),
        ],
    )

    assert isinstance(message, dp_email.email_integration.Message)
    assert message.content.subject == "This is the subject"
    assert message.content.plainText == "This is the body"
    assert message.attachments == [
        dp_email.email_integration.Attachment(
            name="test.pdf",
            contentType="application/pdf",
            contentInBase64=content_bytes_base64str,
        ),
    ]


def test_that_both_emailbody_and_plaintext_is_not_valid():
    with pytest.raises(SetEitherHtmlOrPlainTextError):
        dp_email.email_integration.Message(
            content=dp_email.email_integration.Content(
                subject="This is the subject",
                plainText="This is the body",
                html="<html><h1>This is the body</h1></html>",
            ),
            recipients=dp_email.email_integration.Recipients(
                to=[dp_email.email_integration.Recipient(address="test@test.no", displayName="Test tes")],
            ),
            senderAddress="DoNotReply@73a8fc69-ef8f-4d6a-ae4a-e46be871dce9.azurecomm.net",
        )


@pytest.mark.slow(reason="Depends on VPN, an ENV, and manual modification of the test case, ie. add a recipient")
def test_email_with_attachment():
    """An integration test that actually sends a pdf to the recipient required.

    You need to add the required ENV / Hardcode the connection string, as well as adding a valid recipient +
    be connected to the Skyss Azure VPN, in order to access the keyvault.
    """

    def read_file_as_base64(path: str) -> str:
        with Path(path).open("rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    content_bytes_base64str = read_file_as_base64("test.pdf")
    message = dp_email.email_integration.Message(
        content=dp_email.email_integration.Content(
            subject="This is the subject",
            plainText="This is the body",
        ),
        recipients=dp_email.email_integration.Recipients(
            to=[dp_email.email_integration.Recipient(address="anders.rorvik@gmail.com", displayName="Anders Rørvik")],
        ),
        senderAddress="DoNotReply@73a8fc69-ef8f-4d6a-ae4a-e46be871dce9.azurecomm.net",
        attachments=[
            dp_email.email_integration.Attachment(
                name="test.pdf",
                contentType="application/pdf",
                contentInBase64=content_bytes_base64str,
            ),
        ],
    )

    email_client = dp_email.email_integration.get_email_client(
        os.environ.get("AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING"),
    )
    result = dp_email.email_integration.send_email(email_client, message)
    logger.info(f"Email sending result: {result}")
    assert result["status"] == "Succeeded"
    assert result["id"] is not None
    assert result["error"] is None
