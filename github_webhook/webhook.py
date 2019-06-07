import collections
import hashlib
import hmac
import logging

import six
from flask import abort, request


class Webhook(object):
    """
    Construct a webhook on the given :code:`app`.

    :param app: Flask app that will host the webhook
    :param endpoint: the endpoint for the registered URL rule
    :param secret: Optional secret, used to authenticate the hook comes from Github
    """

    def __init__(self, app, endpoint="/postreceive", secret=None):
        app.add_url_rule(rule=endpoint, endpoint=endpoint, view_func=self._postreceive, methods=["POST"])

        self._hooks = collections.defaultdict(list)
        self._logger = logging.getLogger("webhook")
        if secret is not None and not isinstance(secret, six.binary_type):
            secret = secret.encode("utf-8")
        self._secret = secret

    def hook(self, event_type="push"):
        """
        Registers a function as a hook. Multiple hooks can be registered for a given type, but the
        order in which they are invoke is unspecified.

        :param event_type: The event type this hook will be invoked for.
        """

        def decorator(func):
            self._hooks[event_type].append(func)
            return func

        return decorator

    def _get_digest(self):
        """Return message digest if a secret key was provided"""

        return hmac.new(self._secret, request.data, hashlib.sha1).hexdigest() if self._secret else None

    def _postreceive(self):
        """Callback from Flask"""

        digest = self._get_digest()

        if digest is not None:
            sig_parts = _get_header("X-Hub-Signature").split("=", 1)
            if not isinstance(digest, six.text_type):
                digest = six.text_type(digest)

            if len(sig_parts) < 2 or sig_parts[0] != "sha1" or not hmac.compare_digest(sig_parts[1], digest):
                abort(400, "Invalid signature")

        event_type = _get_header("X-Github-Event")
        data = request.get_json()

        if data is None:
            abort(400, "Request body must contain json")

        self._logger.info("%s (%s)", _format_event(event_type, data), _get_header("X-Github-Delivery"))

        for hook in self._hooks.get(event_type, []):
            hook(data)

        return "", 204


def _get_header(key):
    """Return message header"""

    try:
        return request.headers[key]
    except KeyError:
        abort(400, "Missing header: " + key)


EVENT_DESCRIPTIONS = {
    "commit_comment": "{comment[user][login]} commented on " "{comment[commit_id]} in {repository[full_name]}",
    "create": "{sender[login]} created {ref_type} ({ref}) in " "{repository[full_name]}",
    "delete": "{sender[login]} deleted {ref_type} ({ref}) in " "{repository[full_name]}",
    "deployment": "{sender[login]} deployed {deployment[ref]} to "
    "{deployment[environment]} in {repository[full_name]}",
    "deployment_status": "deployment of {deployement[ref]} to "
    "{deployment[environment]} "
    "{deployment_status[state]} in "
    "{repository[full_name]}",
    "fork": "{forkee[owner][login]} forked {forkee[name]}",
    "gollum": "{sender[login]} edited wiki pages in {repository[full_name]}",
    "issue_comment": "{sender[login]} commented on issue #{issue[number]} " "in {repository[full_name]}",
    "issues": "{sender[login]} {action} issue #{issue[number]} in " "{repository[full_name]}",
    "member": "{sender[login]} {action} member {member[login]} in " "{repository[full_name]}",
    "membership": "{sender[login]} {action} member {member[login]} to team " "{team[name]} in {repository[full_name]}",
    "page_build": "{sender[login]} built pages in {repository[full_name]}",
    "ping": "ping from {sender[login]}",
    "public": "{sender[login]} publicized {repository[full_name]}",
    "pull_request": "{sender[login]} {action} pull #{pull_request[number]} in " "{repository[full_name]}",
    "pull_request_review": "{sender[login]} {action} {review[state]} "
    "review on pull #{pull_request[number]} in "
    "{repository[full_name]}",
    "pull_request_review_comment": "{comment[user][login]} {action} comment "
    "on pull #{pull_request[number]} in "
    "{repository[full_name]}",
    "push": "{pusher[name]} pushed {ref} in {repository[full_name]}",
    "release": "{release[author][login]} {action} {release[tag_name]} in " "{repository[full_name]}",
    "repository": "{sender[login]} {action} repository " "{repository[full_name]}",
    "status": "{sender[login]} set {sha} status to {state} in " "{repository[full_name]}",
    "team_add": "{sender[login]} added repository {repository[full_name]} to " "team {team[name]}",
    "watch": "{sender[login]} {action} watch in repository " "{repository[full_name]}",
}


def _format_event(event_type, data):
    try:
        return EVENT_DESCRIPTIONS[event_type].format(**data)
    except KeyError:
        return event_type


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
