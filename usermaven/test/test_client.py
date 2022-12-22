import time
import unittest
from datetime import datetime
from uuid import uuid4

import mock
import six

from usermaven.client import Client
from usermaven.test.test_utils import FAKE_TEST_API_KEY


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
        self.client = Client(FAKE_TEST_API_KEY, on_error=self.set_fail)
        self.user = {"email": "johndoe@gmail.com", "name": "John Doe", "id": "123456789"}

    def test_requires_api_key(self):
        self.assertRaises(AssertionError, Client)

    def test_empty_flush(self):
        self.client.flush()

    def test_basic_track(self):
        client = self.client
        success, msg = client.track("project_id", self.user)
        client.flush()
        self.assertTrue(success)
        self.assertFalse(self.failed)

        self.assertEqual(msg["user"], {"email": "johndoe@gmail.com", "name": "John Doe", "id": "123456789"})
        self.assertTrue(isinstance(msg["utc_time"], str))
        self.assertTrue(isinstance(msg["local_tz_offset"], float))
        self.assertTrue(isinstance(msg["company"], dict))
        self.assertEqual(msg["project_id"], "project_id")

    def test_basic_track_with_event_id(self):
        client = self.client
        event_id = str(uuid4())
        success, msg = client.track("project_id", self.user, event_id=event_id)
        client.flush()
        self.assertTrue(success)
        self.assertFalse(self.failed)

        self.assertEqual(msg["user"], {"email": "johndoe@gmail.com", "name": "John Doe", "id": "123456789"})
        self.assertTrue(isinstance(msg["utc_time"], str))
        self.assertTrue(isinstance(msg["local_tz_offset"], float))
        self.assertEqual(msg["event_id"], event_id)
        self.assertEqual(msg["project_id"], "project_id")

    def test_basic_track_with_project_api_key(self):

        client = Client(project_api_key=FAKE_TEST_API_KEY, on_error=self.set_fail)

        success, msg = client.track("project_id", self.user)
        client.flush()
        self.assertTrue(success)
        self.assertFalse(self.failed)

        self.assertEqual(msg["user"], {"email": "johndoe@gmail.com", "name": "John Doe", "id": "123456789"})
        self.assertTrue(isinstance(msg["utc_time"], str))
        self.assertTrue(isinstance(msg["local_tz_offset"], float))
        self.assertTrue(isinstance(msg["company"], dict))
        self.assertEqual(msg["project_id"], "project_id")

    def test_stringifies_project_id(self):
        # A large number that loses precision in node:
        # node -e "console.log(157963456373623802 + 1)" > 157963456373623800
        client = self.client
        success, msg = client.track(project_id=157963456373623802, user=self.user)
        client.flush()
        self.assertTrue(success)
        self.assertFalse(self.failed)

        self.assertEqual(msg["project_id"], "157963456373623802")

    def test_advanced_track(self):
        client = self.client
        success, msg = client.track(
            "project_id",
            self.user,
            "event_id",
            {"name": "usermaven", "id": "456"},
            "www.google.com",
            "site_opened",
        )

        self.assertTrue(success)

        self.assertEqual(msg["utc_time"], datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
        self.assertEqual(msg["company"]["name"], "usermaven")
        self.assertEqual(msg["company"]["id"], "456")
        self.assertEqual(msg["src"], "www.google.com")
        self.assertEqual(msg["user"], {"email": "johndoe@gmail.com", "name": "John Doe", "id": "123456789"})
        self.assertEqual(msg["event_id"], "event_id")
        self.assertEqual(msg["project_id"], "project_id")
        self.assertEqual(msg["event_type"], "site_opened")

    def test_company_track(self):
        success, msg = self.client.track(
            "project_id",
            self.user,
            company={"company_details": "id:5", "instance": "app.usermaven.com"},
        )

        self.assertTrue(success)
        self.assertEqual(msg["company"], {"company_details": "id:5", "instance": "app.usermaven.com"})

    def test_basic_identify(self):
        client = self.client
        success, msg = client.identify("project_id", self.user)
        client.flush()
        self.assertTrue(success)
        self.assertFalse(self.failed)

        self.assertEqual(msg["user"], {"email": "johndoe@gmail.com", "name": "John Doe", "id": "123456789"})
        self.assertTrue(isinstance(msg["utc_time"], str))
        self.assertTrue(isinstance(msg["local_tz_offset"], float))
        self.assertEqual(msg["project_id"], "project_id")

    def test_advanced_identify(self):
        client = self.client
        success, msg = client.identify(
            "project_id",
            self.user,
            "event_id",
            {"name": "usermaven", "id": "456"},
            "www.google.com",
            "site_opened",
        )

        self.assertTrue(success)

        self.assertEqual(msg["utc_time"], datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
        self.assertEqual(msg["company"]["name"], "usermaven")
        self.assertEqual(msg["company"]["id"], "456")
        self.assertEqual(msg["src"], "www.google.com")
        self.assertEqual(msg["user"], {"email": "johndoe@gmail.com", "name": "John Doe", "id": "123456789"})
        self.assertEqual(msg["event_id"], "event_id")
        self.assertEqual(msg["project_id"], "project_id")
        self.assertEqual(msg["event_type"], "site_opened")

    def test_flush(self):
        client = self.client
        # set up the consumer with more requests than a single batch will allow
        for i in range(1000):
            success, msg = client.identify("project_id", self.user)
        # We can't reliably assert that the queue is non-empty here; that's
        # a race condition. We do our best to load it up though.
        client.flush()
        # Make sure that the client queue is empty after flushing
        self.assertTrue(client.queue.empty())

    def test_shutdown(self):
        client = self.client
        # set up the consumer with more requests than a single batch will allow
        for i in range(1000):
            success, msg = client.identify("project_id", self.user)
        client.shutdown()
        # we expect two things after shutdown:
        # 1. client queue is empty
        # 2. consumer thread has stopped
        self.assertTrue(client.queue.empty())
        for consumer in client.consumers:
            self.assertFalse(consumer.is_alive())

    def test_synchronous(self):
        client = Client(FAKE_TEST_API_KEY, sync_mode=True)

        success, message = client.identify("project_id", self.user)
        self.assertFalse(client.consumers)
        self.assertTrue(client.queue.empty())
        self.assertTrue(success)

    def test_overflow(self):
        client = Client(FAKE_TEST_API_KEY, max_queue_size=1)
        # Ensure consumer thread is no longer uploading
        client.join()

        for i in range(10):
            client.identify("project_id", self.user)

        success, msg = client.identify("project_id", self.user)
        # Make sure we are informed that the queue is at capacity
        self.assertFalse(success)

    def test_unicode(self):
        Client(six.u("unicode_key"))

    def test_numeric_project_id(self):
        self.client.track(1234, self.user)
        self.client.flush()
        self.assertFalse(self.failed)

    def test_debug(self):
        Client("bad_key", debug=True)

    def test_gzip(self):

        client = Client(FAKE_TEST_API_KEY, on_error=self.fail, gzip=True)
        for _ in range(10):
            client.identify("project_id", self.user)
        client.flush()
        self.assertFalse(self.failed)

    def test_user_defined_flush_at(self):
        client = Client(FAKE_TEST_API_KEY, on_error=self.fail, flush_at=10, flush_interval=3)

        def mock_post_fn(*args, **kwargs):
            self.assertEqual(len(kwargs["batch"]), 10)

        # the post function should be called 2 times, with a batch size of 10
        # each time.
        with mock.patch("usermaven.consumer.batch_post", side_effect=mock_post_fn) as mock_post:
            for _ in range(20):
                client.identify("project_id", self.user)
            time.sleep(1)
            self.assertEqual(mock_post.call_count, 2)

    def test_user_defined_timeout(self):
        client = Client(FAKE_TEST_API_KEY, timeout=10)
        for consumer in client.consumers:
            self.assertEqual(consumer.timeout, 10)

    def test_default_timeout_15(self):
        client = Client(FAKE_TEST_API_KEY)
        for consumer in client.consumers:
            self.assertEqual(consumer.timeout, 15)
