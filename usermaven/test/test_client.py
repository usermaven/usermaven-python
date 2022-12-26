import time
import unittest
from uuid import uuid4

import mock
import six

from usermaven.client import Client
from usermaven.test.test_utils import FAKE_TEST_SERVER_TOKEN


class TestClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # This ensures no real HTTP POST requests are made
        cls.client_post_patcher = mock.patch("usermaven.client.batch_post")
        cls.consumer_post_patcher = mock.patch("usermaven.consumer.batch_post")
        cls.client_post_patcher.start()
        cls.consumer_post_patcher.start()

    @classmethod
    def tearDownClass(cls):
        cls.client_post_patcher.stop()
        cls.consumer_post_patcher.stop()

    def set_fail(self, e, batch):
        """Mark the failure handler"""
        print("FAIL", e, batch)
        self.failed = True

    def setUp(self):
        self.failed = False
        self.client = Client(FAKE_TEST_SERVER_TOKEN, on_error=self.set_fail)
        self.user = {"id": "user_id", "email": "test_user@d4interactive.io", "created_at": "2022-12-12T19:11:49"}

    def test_requires_server_token(self):
        self.assertRaises(AssertionError, Client)

    def test_empty_flush(self):
        self.client.flush()

    def test_basic_track(self):
        client = self.client
        success, msg = client.track("api_key", self.user)
        client.flush()
        self.assertTrue(success)
        self.assertFalse(self.failed)

        self.assertEqual(msg["user"]["id"], "user_id")
        self.assertEqual(msg["user"]["email"], "test_user@d4interactive.io")
        self.assertEqual(msg["user"]["created_at"], "2022-12-12T19:11:49")
        self.assertEqual(msg["api_key"], "api_key")

    def test_basic_track_with_event_id(self):
        client = self.client
        event_id = str(uuid4())
        success, msg = client.track("api_key", self.user, event_id=event_id)
        client.flush()
        self.assertTrue(success)
        self.assertFalse(self.failed)

        self.assertEqual(msg["user"]["id"], "user_id")
        self.assertEqual(msg["user"]["email"], "test_user@d4interactive.io")
        self.assertEqual(msg["user"]["created_at"], "2022-12-12T19:11:49")
        self.assertEqual(msg["event_id"], event_id)
        self.assertEqual(msg["api_key"], "api_key")

    def test_stringifies_api_key(self):
        # A large number that loses precision in node:
        # node -e "console.log(157963456373623802 + 1)" > 157963456373623800
        client = self.client
        success, msg = client.track(api_key=157963456373623802, user=self.user)
        client.flush()
        self.assertTrue(success)
        self.assertFalse(self.failed)

        self.assertEqual(msg["api_key"], "157963456373623802")

    def test_advanced_track(self):
        client = self.client
        success, msg = client.track(
            "api_key",
            self.user,
            event_id="event_id",
            ids={},
            company={"id": "5", "name": "Usermaven", "created_at": "2022-12-12T19:11:49"},
            src="www.google.com",
            event_type="site_opened",
        )

        self.assertTrue(success)

        self.assertEqual(msg["company"]["name"], "Usermaven")
        self.assertEqual(msg["company"]["id"], "5")
        self.assertEqual(msg["src"], "www.google.com")
        self.assertEqual(msg["user"]["id"], "user_id")
        self.assertEqual(msg["user"]["email"], "test_user@d4interactive.io")
        self.assertEqual(msg["user"]["created_at"], "2022-12-12T19:11:49")
        self.assertEqual(msg["event_id"], "event_id")
        self.assertEqual(msg["api_key"], "api_key")
        self.assertEqual(msg["event_type"], "site_opened")

    def test_company_track(self):
        success, msg = self.client.track(
            "api_key",
            self.user,
            company={"id": "5", "name": "Usermaven", "created_at": "2022-12-12T19:11:49"},
        )

        self.assertTrue(success)
        self.assertEqual(msg["company"], {"id": "5", "name": "Usermaven", "created_at": "2022-12-12T19:11:49"})

    def test_basic_identify(self):
        client = self.client
        success, msg = client.identify("api_key", self.user)
        client.flush()
        self.assertTrue(success)
        self.assertFalse(self.failed)

        self.assertEqual(msg["user"]["id"], "user_id")
        self.assertEqual(msg["user"]["email"], "test_user@d4interactive.io")
        self.assertEqual(msg["user"]["created_at"], "2022-12-12T19:11:49")
        self.assertEqual(msg["api_key"], "api_key")

    def test_advanced_identify(self):
        client = self.client
        success, msg = client.identify(
            "api_key",
            self.user,
            event_id="event_id",
            ids={},
            company={"id": "5", "name": "Usermaven", "created_at": "2022-12-12T19:11:49"},
            src="www.google.com",
            event_type="site_opened",
        )

        self.assertTrue(success)

        self.assertEqual(msg["company"]["name"], "Usermaven")
        self.assertEqual(msg["company"]["id"], "5")
        self.assertEqual(msg["src"], "www.google.com")
        self.assertEqual(msg["user"]["id"], "user_id")
        self.assertEqual(msg["user"]["email"], "test_user@d4interactive.io")
        self.assertEqual(msg["user"]["created_at"], "2022-12-12T19:11:49")
        self.assertEqual(msg["event_id"], "event_id")
        self.assertEqual(msg["api_key"], "api_key")
        self.assertEqual(msg["event_type"], "site_opened")

    def test_flush(self):
        client = self.client
        # set up the consumer with more requests than a single batch will allow
        for i in range(1000):
            success, msg = client.identify("api_key", self.user)
        # We can't reliably assert that the queue is non-empty here; that's
        # a race condition. We do our best to load it up though.
        client.flush()
        # Make sure that the client queue is empty after flushing
        self.assertTrue(client.queue.empty())

    def test_shutdown(self):
        client = self.client
        # set up the consumer with more requests than a single batch will allow
        for i in range(1000):
            success, msg = client.identify("api_key", self.user)
        client.shutdown()
        # we expect two things after shutdown:
        # 1. client queue is empty
        # 2. consumer thread has stopped
        self.assertTrue(client.queue.empty())
        for consumer in client.consumers:
            self.assertFalse(consumer.is_alive())

    def test_synchronous(self):
        client = Client(FAKE_TEST_SERVER_TOKEN, sync_mode=True)

        success, message = client.identify("api_key", self.user)
        self.assertFalse(client.consumers)
        self.assertTrue(client.queue.empty())
        self.assertTrue(success)

    def test_overflow(self):
        client = Client(FAKE_TEST_SERVER_TOKEN, max_queue_size=1)
        # Ensure consumer thread is no longer uploading
        client.join()

        for i in range(10):
            client.identify("api_key", self.user)

        success, msg = client.identify("api_key", self.user)
        # Make sure we are informed that the queue is at capacity
        self.assertFalse(success)

    def test_unicode(self):
        Client(six.u("unicode_key"))

    def test_numeric_api_key(self):
        self.client.track(1234, self.user)
        self.client.flush()
        self.assertFalse(self.failed)

    def test_debug(self):
        Client("bad_key", debug=True)

    def test_user_defined_flush_at(self):
        client = Client(FAKE_TEST_SERVER_TOKEN, on_error=self.fail, flush_at=10, flush_interval=3)

        def mock_post_fn(*args, **kwargs):
            self.assertEqual(len(kwargs["batch"]), 10)

        # the post function should be called 2 times, with a batch size of 10
        # each time.
        with mock.patch("usermaven.consumer.batch_post", side_effect=mock_post_fn) as mock_post:
            for _ in range(20):
                client.identify("api_key", self.user)
            time.sleep(1)
            self.assertEqual(mock_post.call_count, 2)

    def test_user_defined_timeout(self):
        client = Client(FAKE_TEST_SERVER_TOKEN, timeout=10)
        for consumer in client.consumers:
            self.assertEqual(consumer.timeout, 10)

    def test_default_timeout_15(self):
        client = Client(FAKE_TEST_SERVER_TOKEN)
        for consumer in client.consumers:
            self.assertEqual(consumer.timeout, 15)
