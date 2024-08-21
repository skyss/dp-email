import base64
import os
from dataclasses import asdict
import pytest
from dp_email.email_integration import Content, Message, Recipient, Recipients, Attachment, build_message, \
    get_email_client, send_email


def test_that_message_converts_to_dict():
    expected_message = {
        "attachments": None,
        "content": {
            "subject": "This is the subject",
            "plainText": "This is the body",
            "html": "<html><h1>This is the body</h1></html>",
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

    message = Message(
        content=Content(
            subject="This is the subject",
            plainText="This is the body",
            html="<html><h1>This is the body</h1></html>",
        ),
        recipients=Recipients(
            to=[Recipient(address="test@vlfk.no", displayName="Test Testesen")],
        ),
        senderAddress="DoNotReply@longguid.azurecomm.net",
    )

    assert expected_message == asdict(message)


def test_that_build_message_returns_message():
    message = build_message(
        subject="This is the subject",
        html="<html><h1>This is the body</h1></html>",
        to_address="test@vlfk.no",
        sender_address="DoNotReply@longguid.azurecomm.net",
    )

    assert isinstance(message, Message)
    assert message.content.subject == "This is the subject"
    assert message.content.plainText == "<html><h1>This is the body</h1></html>"
    assert message.content.html == "<html><h1>This is the body</h1></html>"


def test_that_build_message_with_attachments_returns_message():
    contentBytesBase64str = base64.b64encode("this is a test".encode("utf-8")).decode("utf-8")
    message = Message(
        content=Content(
            subject="This is the subject",
            plainText="This is the body",
            html="<html><h1>This is the body</h1></html>",
        ),
        recipients=Recipients(
            to=[Recipient(address="test@vlfk.no", displayName="Anders Rørvik")],
        ),
        senderAddress="DoNotReply@73a8fc69-ef8f-4d6a-ae4a-e46be871dce9.azurecomm.net",
        attachments=[Attachment(name="test.pdf", contentType="application/pdf",
                                contentInBase64=contentBytesBase64str)]
    )

    assert isinstance(message, Message)
    assert message.content.subject == "This is the subject"
    assert message.content.plainText == "This is the bodyl>"
    assert message.content.html == "<html><h1>This is the body</h1></html>"
    assert message.attachments == [
        Attachment(name="test.pdf", contentType="application/pdf", contentInBase64=contentBytesBase64str)]


@pytest.mark.manual_trigger
def test_email_with_attachment():
    """This is an integration test that actually sends a pdf to the recipient required. You need to add the required ENV / Hardcode the connection string, as well as adding a valid recipient"""

    def read_file_as_base64(path: str):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    contentBytesBase64str = read_file_as_base64("test.pdf")
    message = Message(
        content=Content(
            subject="This is the subject",
            plainText="This is the body",
            html="<html><h1>This is the body</h1></html>",
        ),
        recipients=Recipients(
            to=[Recipient(address="anders.rorvik@knowit.no", displayName="Anders Rørvik")],
        ),
        senderAddress="DoNotReply@73a8fc69-ef8f-4d6a-ae4a-e46be871dce9.azurecomm.net",
        attachments=[Attachment(name="test.pdf", contentType="application/pdf",
                                contentInBase64=contentBytesBase64str)]
    )

    email_client = get_email_client(os.environ.get("AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING"))
    result = send_email(email_client, message)
    print("Email sending result:" + result)
