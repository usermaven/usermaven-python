import time
import unittest

import mock
import six

from usermaven.client import Client
from usermaven.test.test_utils import FAKE_TEST_SERVER_TOKEN, FAKE_TEST_API_KEY


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
        self.client = Client(FAKE_TEST_API_KEY, FAKE_TEST_SERVER_TOKEN, on_error=self.set_fail)
        self.user = {"id": "user_id", "email": "test_user@d4interactive.io", "created_at": "2022-12-12T19:11:49"}
        self.user_id = "user_id"

    def test_requires_api_key(self):
        with self.assertRaises(AssertionError):
            Client(server_token=FAKE_TEST_SERVER_TOKEN)

    def test_requires_server_token(self):
        with self.assertRaises(AssertionError):
            Client(api_key=FAKE_TEST_API_KEY)

    def test_empty_flush(self):
        self.client.flush()

    def test_basic_track(self):
        client = self.client
        success, msg = client.track(self.user_id, "goal_created")
        client.flush()
        self.assertTrue(success)
        self.assertFalse(self.failed)

        self.assertEqual(msg["user"]["id"], "user_id")
        self.assertEqual(msg["api_key"], "random_api_key_for_testing")
        self.assertEqual(msg["event_type"], "goal_created")

    def test_basic_track_without_event_type(self):
        # Test that track method raises a TypeError when called without event_type argument
        with self.assertRaises(TypeError):
            self.client.track(self.user_id)  # missing event_type argument

    def test_advanced_track(self):
        client = self.client
        success, msg = client.track(
            self.user_id,
            "goal_created",
            {"id": "5", "name": "Usermaven", "created_at": "2022-12-12T19:11:49"},
            {"goal_name": "signup", "goal_value": 100},
        )

        self.assertTrue(success)

        self.assertEqual(msg["company"]["name"], "Usermaven")
        self.assertEqual(msg["company"]["id"], "5")
        self.assertEqual(msg["company"]["created_at"], "2022-12-12T19:11:49")
        self.assertEqual(msg["user"]["id"], "user_id")
        self.assertEqual(msg["api_key"], "random_api_key_for_testing")
        self.assertEqual(msg["event_type"], "goal_created")
        self.assertEqual(msg["event_attributes"]["goal_name"], "signup")
        self.assertEqual(msg["event_attributes"]["goal_value"], 100)

    def test_company_track_without_name(self):
        # Test that track method raises a ValueError when called with company dictionary missing name key
        with self.assertRaises(ValueError):
            self.client.track(self.user_id, "goal_created", company={"id": "5", "created_at": "2022-12-12T19:11:49"})

    def test_company_track_with_custom(self):
        client = self.client
        success, msg = client.track(
            self.user_id,
            "goal_created",
            {"id": "5", "name": "Usermaven", "created_at": "2022-12-12T19:11:49",
             "custom": {"custom_key": "custom_value"}},
        )

        self.assertTrue(success)
        self.assertEqual(msg["company"]["custom"]["custom_key"], "custom_value")

    def test_basic_identify(self):
        client = self.client
        success, msg = client.identify(self.user)
        client.flush()
        self.assertTrue(success)
        self.assertFalse(self.failed)

        self.assertEqual(msg["user"]["id"], "user_id")
        self.assertEqual(msg["user"]["email"], "test_user@d4interactive.io")
        self.assertEqual(msg["user"]["created_at"], "2022-12-12T19:11:49")
        self.assertEqual(msg["api_key"], "random_api_key_for_testing")
        self.assertEqual(msg["event_type"], "user_identify")
        self.assertEqual(msg["src"], "usermaven-python")

    def test_advanced_identify(self):
        client = self.client
        success, msg = client.identify(
            self.user,
            company={"id": "5", "name": "Usermaven", "created_at": "2022-12-12T19:11:49"}
        )

        self.assertTrue(success)

        self.assertEqual(msg["company"]["name"], "Usermaven")
        self.assertEqual(msg["company"]["id"], "5")
        self.assertEqual(msg["company"]["created_at"], "2022-12-12T19:11:49")
        self.assertEqual(msg["src"], "usermaven-python")
        self.assertEqual(msg["user"]["id"], "user_id")
        self.assertEqual(msg["user"]["email"], "test_user@d4interactive.io")
        self.assertEqual(msg["user"]["created_at"], "2022-12-12T19:11:49")
        self.assertEqual(msg["event_id"], "")
        self.assertEqual(msg["api_key"], "random_api_key_for_testing")
        self.assertEqual(msg["event_type"], "user_identify")

    def test_user_identify_without_email(self):
        # Test that identify method raises a ValueError when called with dictionary missing email key
        with self.assertRaises(ValueError):
            self.client.identify({"id": "user_id", "created_at": "2022-12-12T19:11:49"})

    def test_company_identify_without_id(self):
        # Test that identify method raises a ValueError when called with company dictionary missing id key
        with self.assertRaises(ValueError):
            self.client.identify(self.user, company={"name": "Usermaven"})

    def test_advanced_identify_with_custom(self):
        client = self.client
        success, msg = client.identify(
            {"id": "user_id", "email": "test_user@d4interactive.io", "created_at": "2022-12-12T19:11:49",
             "custom": {"custom_key": "custom_value"}},
            {"id": "5", "name": "Usermaven", "created_at": "2022-12-12T19:11:49",
             "custom": {"custom_key": "custom_value"}},
        )

        self.assertTrue(success)
        self.assertEqual(msg["company"]["custom"]["custom_key"], "custom_value")
        self.assertEqual(msg["user"]["custom"]["custom_key"], "custom_value")

    def test_flush(self):
        client = self.client
        # set up the consumer with more requests than a single batch will allow
        for i in range(1000):
            success, msg = client.identify(self.user)
        # We can't reliably assert that the queue is non-empty here; that's
        # a race condition. We do our best to load it up though.
        client.flush()
        # Make sure that the client queue is empty after flushing
        self.assertTrue(client.queue.empty())

    def test_shutdown(self):
        client = self.client
        # set up the consumer with more requests than a single batch will allow
        for i in range(1000):
            success, msg = client.identify(self.user)
        client.shutdown()
        # we expect two things after shutdown:
        # 1. client queue is empty
        # 2. consumer thread has stopped
        self.assertTrue(client.queue.empty())
        for consumer in client.consumers:
            self.assertFalse(consumer.is_alive())

    def test_synchronous(self):
        client = Client(FAKE_TEST_API_KEY, FAKE_TEST_SERVER_TOKEN, sync_mode=True)

        success, message = client.identify(self.user)
        self.assertFalse(client.consumers)
        self.assertTrue(client.queue.empty())
        self.assertTrue(success)

    def test_overflow(self):
        client = Client(FAKE_TEST_API_KEY, FAKE_TEST_SERVER_TOKEN, max_queue_size=1)
        # Ensure consumer thread is no longer uploading
        client.join()

        for i in range(10):
            client.identify(self.user)

        success, msg = client.identify(self.user)
        # Make sure we are informed that the queue is at capacity
        self.assertFalse(success)

    def test_unicode(self):
        Client(six.u("unicode_key"), six.u("unicode_token"))

    def test_debug(self):
        Client("bad_key", "bad_token", debug=True)

    def test_user_defined_flush_at(self):
        client = Client(FAKE_TEST_API_KEY, FAKE_TEST_SERVER_TOKEN, on_error=self.fail, flush_at=10, flush_interval=3)

        def mock_post_fn(*args, **kwargs):
            self.assertEqual(len(kwargs["batch"]), 10)

        # the post function should be called 2 times, with a batch size of 10
        # each time.
        with mock.patch("usermaven.consumer.batch_post", side_effect=mock_post_fn) as mock_post:
            for _ in range(20):
                client.identify(self.user)
            time.sleep(1)
            self.assertEqual(mock_post.call_count, 2)

    def test_user_defined_timeout(self):
        client = Client(FAKE_TEST_API_KEY, FAKE_TEST_SERVER_TOKEN, timeout=10)
        for consumer in client.consumers:
            self.assertEqual(consumer.timeout, 10)

    def test_default_timeout_15(self):
        client = Client(FAKE_TEST_API_KEY, FAKE_TEST_SERVER_TOKEN)
        for consumer in client.consumers:
            self.assertEqual(consumer.timeout, 15)
