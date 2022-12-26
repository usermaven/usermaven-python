import json
import unittest
from datetime import date, datetime

import requests

from usermaven.request import DatetimeSerializer, batch_post
from usermaven.test.test_utils import TEST_SERVER_TOKEN


class TestRequests(unittest.TestCase):
    def test_valid_request(self):
        res = batch_post(TEST_SERVER_TOKEN,
                         batch=[{"type": "track", "user": {"anonymous_id": "", "id": "", "email": "", "created_at": "",
                                           "first_name": "", "last_name": "", "is_integrated_with_pixel": True},
                                 "api_key": "api_key"}])
        self.assertEqual(res.status_code, 200)

    def test_invalid_request_error(self):
        self.assertRaises(Exception, batch_post, "testsecret", "https://t.usermaven.com", False, "[{]")

    def test_invalid_host(self):
        self.assertRaises(Exception, batch_post, "testsecret", "t.usermaven.com/", batch=[])

    def test_datetime_serialization(self):
        data = {"created": datetime(2012, 3, 4, 5, 6, 7, 891011)}
        result = json.dumps(data, cls=DatetimeSerializer)
        self.assertEqual(result, '{"created": "2012-03-04T05:06:07.891011"}')

    def test_date_serialization(self):
        today = date.today()
        data = {"created": today}
        result = json.dumps(data, cls=DatetimeSerializer)
        expected = '{"created": "%s"}' % today.isoformat()
        self.assertEqual(result, expected)

    def test_should_not_timeout(self):
        res = batch_post(
            TEST_SERVER_TOKEN, batch=[{"type": "track", "user": {"anonymous_id": "", "id": "", "email": "",
                                                                 "created_at": "", "first_name": "", "last_name": "",
                                                                 "is_integrated_with_pixel": True},
                                       "api_key": "api_key"}], timeout=15)
        self.assertEqual(res.status_code, 200)

    def test_should_timeout(self):
        with self.assertRaises(requests.ReadTimeout):
            batch_post(
                "key", batch=[{"type": "track", "user": {"anonymous_id": "", "id": "", "email": "", "created_at": "",
                                                         "first_name": "", "last_name": "",
                                                         "is_integrated_with_pixel": True}, "api_key": "api_key"}],
                timeout=0.0001)
