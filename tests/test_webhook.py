"""Tests for github_webhook.webhook"""

from __future__ import print_function

import pytest
import werkzeug
import json

try:
    from unittest import mock
except ImportError:
    import mock

from github_webhook.webhook import Webhook


@pytest.fixture
def mock_request():
    with mock.patch("github_webhook.webhook.request") as req:
        req.headers = {"X-Github-Delivery": ""}
        yield req


@pytest.fixture
def push_request(mock_request):
    mock_request.headers["X-Github-Event"] = "push"
    mock_request.headers["content-type"] = "application/json"
    yield mock_request


@pytest.fixture
def push_request_encoded(mock_request):
    mock_request.headers["X-Github-Event"] = "push"
    mock_request.headers["content-type"] = "application/x-www-form-urlencoded"
    yield mock_request


@pytest.fixture
def app():
    yield mock.Mock()


@pytest.fixture
def webhook(app):
    yield Webhook(app)


@pytest.fixture
def handler(webhook):
    handler = mock.Mock()
    webhook.hook()(handler)
    yield handler


def test_constructor():
    # GIVEN
    app = mock.Mock()

    # WHEN
    webhook = Webhook(app)

    # THEN
    app.add_url_rule.assert_called_once_with(
        endpoint="/postreceive", rule="/postreceive", view_func=webhook._postreceive, methods=["POST"]
    )


def test_init_app_flow():
    # GIVEN
    app = mock.Mock()

    # WHEN
    webhook = Webhook()
    webhook.init_app(app)

    # THEN
    app.add_url_rule.assert_called_once_with(
        endpoint="/postreceive", rule="/postreceive", view_func=webhook._postreceive, methods=["POST"]
    )


def test_init_app_flow_should_not_accidentally_override_secrets():
    # GIVEN
    app = mock.Mock()

    # WHEN
    webhook = Webhook(secret="hello-world-of-secrecy")
    webhook.init_app(app)

    # THEN
    assert webhook.secret is not None


def test_init_app_flow_should_override_secrets():
    # GIVEN
    app = mock.Mock()

    # WHEN
    webhook = Webhook(secret="hello-world-of-secrecy")
    webhook.init_app(app, secret="a-new-world-of-secrecy")

    # THEN
    assert webhook.secret == "a-new-world-of-secrecy".encode("utf-8")


def test_run_push_hook(webhook, handler, push_request):
    # WHEN
    webhook._postreceive()

    # THEN
    handler.assert_called_once_with(push_request.get_json.return_value)


def test_run_push_hook_urlencoded(webhook, handler, push_request_encoded):
    github_mock_payload = {"payload": '{"key": "value"}'}
    push_request_encoded.form.to_dict.return_value = github_mock_payload
    payload = json.loads(github_mock_payload["payload"])

    # WHEN
    webhook._postreceive()

    # THEN
    handler.assert_called_once_with(payload)


def test_do_not_run_push_hook_on_ping(webhook, handler, mock_request):
    # GIVEN
    mock_request.headers["X-Github-Event"] = "ping"
    mock_request.headers["content-type"] = "application/json"

    # WHEN
    webhook._postreceive()

    # THEN
    handler.assert_not_called()


def test_do_not_run_push_hook_on_ping_urlencoded(webhook, handler, mock_request):
    # GIVEN
    mock_request.headers["X-Github-Event"] = "ping"
    mock_request.headers["content-type"] = "application/x-www-form-urlencoded"
    mock_request.form.to_dict.return_value = {"payload": '{"key": "value"}'}

    # WHEN
    webhook._postreceive()

    # THEN
    handler.assert_not_called()


def test_can_handle_zero_events(webhook, push_request):
    # WHEN, THEN
    webhook._postreceive()  # noop


@pytest.mark.parametrize("secret", [u"secret", b"secret"])
@mock.patch("github_webhook.webhook.hmac")
def test_calls_if_signature_is_correct(mock_hmac, app, push_request, secret):
    # GIVEN
    webhook = Webhook(app, secret=secret)
    push_request.headers["X-Hub-Signature"] = "sha1=hash_of_something"
    push_request.data = b"something"
    handler = mock.Mock()
    mock_hmac.compare_digest.return_value = True

    # WHEN
    webhook.hook()(handler)
    webhook._postreceive()

    # THEN
    handler.assert_called_once_with(push_request.get_json.return_value)


@mock.patch("github_webhook.webhook.hmac")
def test_does_not_call_if_signature_is_incorrect(mock_hmac, app, push_request):
    # GIVEN
    webhook = Webhook(app, secret="super_secret")
    push_request.headers["X-Hub-Signature"] = "sha1=hash_of_something"
    push_request.data = b"something"
    handler = mock.Mock()
    mock_hmac.compare_digest.return_value = False

    # WHEN, THEN
    webhook.hook()(handler)
    with pytest.raises(werkzeug.exceptions.BadRequest):
        webhook._postreceive()


def test_request_has_no_data(webhook, handler, push_request):
    # GIVEN
    push_request.get_json.return_value = None

    # WHEN, THEN
    with pytest.raises(werkzeug.exceptions.BadRequest):
        webhook._postreceive()


def test_request_had_headers(webhook, handler, mock_request):
    # WHEN, THEN
    with pytest.raises(werkzeug.exceptions.BadRequest):
        webhook._postreceive()


# -----------------------------------------------------------------------------
# Copyright 2015 Bloomberg Finance L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ----------------------------- END-OF-FILE -----------------------------------
