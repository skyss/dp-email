from dataclasses import asdict

from dp_email.email_integration import Content, Message, Recipient, Recipients, build_message


def test_that_message_converts_to_dict():
    expected_message = {
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
