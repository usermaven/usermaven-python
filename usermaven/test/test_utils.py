import unittest
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import UUID

import six

from usermaven import utils

TEST_SERVER_TOKEN = "5ce1039f-e554-41f2-bcb6-55958cfcce0c"
TEST_API_KEY = "UMLAClUgr5"
FAKE_TEST_SERVER_TOKEN = "random_token_for_testing"
FAKE_TEST_API_KEY = "random_api_key_for_testing"


class TestUtils(unittest.TestCase):
    def test_clean(self):
        simple = {
            "decimal": Decimal("0.142857"),
            "unicode": six.u("woo"),
            "date": datetime.now(),
            "long": 200000000,
            "integer": 1,
            "float": 2.0,
            "bool": True,
            "str": "woo",
            "none": None,
        }

        complicated = {
            "exception": Exception("This should show up"),
            "timedelta": timedelta(microseconds=20),
            "list": [1, 2, 3],
        }

        combined = dict(simple.items())
        combined.update(complicated.items())

        pre_clean_keys = combined.keys()

        utils.clean(combined)
        self.assertEqual(combined.keys(), pre_clean_keys)

        # test UUID separately, as the UUID object doesn't equal its string representation according to Python
        self.assertEqual(utils.clean(UUID("12345678123456781234567812345678")), "12345678-1234-5678-1234-567812345678")

    def test_clean_with_dates(self):
        dict_with_dates = {
            "birthdate": date(1980, 1, 1),
            "registration": datetime.utcnow(),
        }
        self.assertEqual(dict_with_dates, utils.clean(dict_with_dates))

    def test_bytes(self):
        if six.PY3:
            item = bytes(10)
        else:
            item = bytearray(10)

        utils.clean(item)

    def test_clean_fn(self):
        cleaned = utils.clean({"fn": lambda x: x, "number": 4})
        self.assertEqual(cleaned["number"], 4)

        if "fn" in cleaned:
            self.assertEqual(cleaned["fn"], None)

    def test_remove_slash(self):
        self.assertEqual("http://usermaven.io", utils.remove_trailing_slash("http://usermaven.io/"))
        self.assertEqual("http://usermaven.io", utils.remove_trailing_slash("http://usermaven.io"))
