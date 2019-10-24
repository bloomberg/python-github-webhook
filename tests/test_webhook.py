"""Tests for github_webhook.webhook"""

from __future__ import print_function

import pytest
import werkzeug
from flask import Flask

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


def test_run_push_hook(webhook, handler, push_request):
    # WHEN
    webhook._postreceive()

    # THEN
    handler.assert_called_once_with(push_request.get_json.return_value)


def test_do_not_run_push_hook_on_ping(webhook, handler, mock_request):
    # GIVEN
    mock_request.headers["X-Github-Event"] = "ping"

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


# From https://developer.github.com/v3/activity/events/types/#pushevent
example_push_event = {
    "ref": "refs/tags/simple-tag",
    "before": "a10867b14bb761a232cd80139fbd4c0d33264240",
    "after": "0000000000000000000000000000000000000000",
    "created": False,
    "deleted": True,
    "forced": False,
    "base_ref": None,
    "compare": "https://github.com/Codertocat/Hello-World/compare/a10867b14bb7...000000000000",
    "commits": [],
    "head_commit": None,
    "repository": {
        "id": 135493233,
        "node_id": "MDEwOlJlcG9zaXRvcnkxMzU0OTMyMzM=",
        "name": "Hello-World",
        "full_name": "Codertocat/Hello-World",
        "owner": {
            "name": "Codertocat",
            "email": "21031067+Codertocat@users.noreply.github.com",
            "login": "Codertocat",
            "id": 21031067,
            "node_id": "MDQ6VXNlcjIxMDMxMDY3",
            "avatar_url": "https://avatars1.githubusercontent.com/u/21031067?v=4",
            "gravatar_id": "",
            "url": "https://api.github.com/users/Codertocat",
            "html_url": "https://github.com/Codertocat",
            "followers_url": "https://api.github.com/users/Codertocat/followers",
            "following_url": "https://api.github.com/users/Codertocat/following{/other_user}",
            "gists_url": "https://api.github.com/users/Codertocat/gists{/gist_id}",
            "starred_url": "https://api.github.com/users/Codertocat/starred{/owner}{/repo}",
            "subscriptions_url": "https://api.github.com/users/Codertocat/subscriptions",
            "organizations_url": "https://api.github.com/users/Codertocat/orgs",
            "repos_url": "https://api.github.com/users/Codertocat/repos",
            "events_url": "https://api.github.com/users/Codertocat/events{/privacy}",
            "received_events_url": "https://api.github.com/users/Codertocat/received_events",
            "type": "User",
            "site_admin": False,
        },
        "private": False,
        "html_url": "https://github.com/Codertocat/Hello-World",
        "description": None,
        "fork": False,
        "url": "https://github.com/Codertocat/Hello-World",
        "forks_url": "https://api.github.com/repos/Codertocat/Hello-World/forks",
        "keys_url": "https://api.github.com/repos/Codertocat/Hello-World/keys{/key_id}",
        "collaborators_url": "https://api.github.com/repos/Codertocat/Hello-World/collaborators{/collaborator}",
        "teams_url": "https://api.github.com/repos/Codertocat/Hello-World/teams",
        "hooks_url": "https://api.github.com/repos/Codertocat/Hello-World/hooks",
        "issue_events_url": "https://api.github.com/repos/Codertocat/Hello-World/issues/events{/number}",
        "events_url": "https://api.github.com/repos/Codertocat/Hello-World/events",
        "assignees_url": "https://api.github.com/repos/Codertocat/Hello-World/assignees{/user}",
        "branches_url": "https://api.github.com/repos/Codertocat/Hello-World/branches{/branch}",
        "tags_url": "https://api.github.com/repos/Codertocat/Hello-World/tags",
        "blobs_url": "https://api.github.com/repos/Codertocat/Hello-World/git/blobs{/sha}",
        "git_tags_url": "https://api.github.com/repos/Codertocat/Hello-World/git/tags{/sha}",
        "git_refs_url": "https://api.github.com/repos/Codertocat/Hello-World/git/refs{/sha}",
        "trees_url": "https://api.github.com/repos/Codertocat/Hello-World/git/trees{/sha}",
        "statuses_url": "https://api.github.com/repos/Codertocat/Hello-World/statuses/{sha}",
        "languages_url": "https://api.github.com/repos/Codertocat/Hello-World/languages",
        "stargazers_url": "https://api.github.com/repos/Codertocat/Hello-World/stargazers",
        "contributors_url": "https://api.github.com/repos/Codertocat/Hello-World/contributors",
        "subscribers_url": "https://api.github.com/repos/Codertocat/Hello-World/subscribers",
        "subscription_url": "https://api.github.com/repos/Codertocat/Hello-World/subscription",
        "commits_url": "https://api.github.com/repos/Codertocat/Hello-World/commits{/sha}",
        "git_commits_url": "https://api.github.com/repos/Codertocat/Hello-World/git/commits{/sha}",
        "comments_url": "https://api.github.com/repos/Codertocat/Hello-World/comments{/number}",
        "issue_comment_url": "https://api.github.com/repos/Codertocat/Hello-World/issues/comments{/number}",
        "contents_url": "https://api.github.com/repos/Codertocat/Hello-World/contents/{+path}",
        "compare_url": "https://api.github.com/repos/Codertocat/Hello-World/compare/{base}...{head}",
        "merges_url": "https://api.github.com/repos/Codertocat/Hello-World/merges",
        "archive_url": "https://api.github.com/repos/Codertocat/Hello-World/{archive_format}{/ref}",
        "downloads_url": "https://api.github.com/repos/Codertocat/Hello-World/downloads",
        "issues_url": "https://api.github.com/repos/Codertocat/Hello-World/issues{/number}",
        "pulls_url": "https://api.github.com/repos/Codertocat/Hello-World/pulls{/number}",
        "milestones_url": "https://api.github.com/repos/Codertocat/Hello-World/milestones{/number}",
        "notifications_url": "https://api.github.com/repos/Codertocat/Hello-World/notifications{?since,all,participating}",
        "labels_url": "https://api.github.com/repos/Codertocat/Hello-World/labels{/name}",
        "releases_url": "https://api.github.com/repos/Codertocat/Hello-World/releases{/id}",
        "deployments_url": "https://api.github.com/repos/Codertocat/Hello-World/deployments",
        "created_at": 1527711484,
        "updated_at": "2018-05-30T20:18:35Z",
        "pushed_at": 1527711528,
        "git_url": "git://github.com/Codertocat/Hello-World.git",
        "ssh_url": "git@github.com:Codertocat/Hello-World.git",
        "clone_url": "https://github.com/Codertocat/Hello-World.git",
        "svn_url": "https://github.com/Codertocat/Hello-World",
        "homepage": None,
        "size": 0,
        "stargazers_count": 0,
        "watchers_count": 0,
        "language": None,
        "has_issues": True,
        "has_projects": True,
        "has_downloads": True,
        "has_wiki": True,
        "has_pages": True,
        "forks_count": 0,
        "mirror_url": None,
        "archived": False,
        "open_issues_count": 2,
        "license": None,
        "forks": 0,
        "open_issues": 2,
        "watchers": 0,
        "default_branch": "master",
        "stargazers": 0,
        "master_branch": "master",
    },
    "pusher": {"name": "Codertocat", "email": "21031067+Codertocat@users.noreply.github.com"},
    "sender": {
        "login": "Codertocat",
        "id": 21031067,
        "node_id": "MDQ6VXNlcjIxMDMxMDY3",
        "avatar_url": "https://avatars1.githubusercontent.com/u/21031067?v=4",
        "gravatar_id": "",
        "url": "https://api.github.com/users/Codertocat",
        "html_url": "https://github.com/Codertocat",
        "followers_url": "https://api.github.com/users/Codertocat/followers",
        "following_url": "https://api.github.com/users/Codertocat/following{/other_user}",
        "gists_url": "https://api.github.com/users/Codertocat/gists{/gist_id}",
        "starred_url": "https://api.github.com/users/Codertocat/starred{/owner}{/repo}",
        "subscriptions_url": "https://api.github.com/users/Codertocat/subscriptions",
        "organizations_url": "https://api.github.com/users/Codertocat/orgs",
        "repos_url": "https://api.github.com/users/Codertocat/repos",
        "events_url": "https://api.github.com/users/Codertocat/events{/privacy}",
        "received_events_url": "https://api.github.com/users/Codertocat/received_events",
        "type": "User",
        "site_admin": False,
    },
}


def test_push_request():
    """ Uses the example event defined in the GitHub documentation to ensure
    that our webhook app can receive the event.
    """

    # GIVEN
    app = Flask(__name__)  # Standard Flask app
    webhook = Webhook(app)  # Defines '/postreceive' endpoint

    @webhook.hook()  # Defines a handler for the 'push' event
    def on_push(data):
        flag = data["repository"]["full_name"] == "Codertocat/Hello-World"
        if not flag:
            return "Event data does not match expected data", 400

    # WHEN
    resp = None
    with app.test_client() as client:
        resp = client.post(
            "/postreceive", json=example_push_event, headers={"X-Github-Event": "push", "X-Github-Delivery": 0}
        )

    # THEN
    assert resp.status_code == 204


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
