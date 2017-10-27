"""Tests for github_webhook.webhook"""

from __future__ import print_function

import unittest
from nose.tools import assert_equal

from github_webhook.event_type import EventType

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from github_webhook.webhook import Webhook


class TestWebhook(unittest.TestCase):

    def test_constructor(self):
        # GIVEN
        app = Mock()

        # WHEN
        webhook = Webhook(app)

        # THEN
        app.add_url_rule.assert_called_once_with(
            '/postreceive', view_func=webhook._postreceive, methods=['POST'])

    def test_hook(self):
        # GIVEN
        app = Mock()

        def test_handler():
            return "OK"

        # WHEN
        webhook = Webhook(app)

        webhook.hook()(test_handler)
        assert_equal(webhook._hooks['push'][0], test_handler)
        webhook.hook(EventType.CommitComment)(test_handler)
        assert_equal(webhook._hooks['commit_comment'][0], test_handler)
        webhook.hook('deployment')(test_handler)
        assert_equal(webhook._hooks['deployment'][0], test_handler)


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
