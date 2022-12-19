import atexit
import logging
import numbers
from datetime import datetime, timedelta
from uuid import UUID

from dateutil.tz import tzutc
from six import string_types


try:
    import queue
except ImportError:
    import Queue as queue

ID_TYPES = (numbers.Number, string_types, UUID)
MAX_DICT_SIZE = 50_000


class Client(object):
    """Create a new Usermaven client."""

    log = logging.getLogger("usermaven")

    def __init__(self):
        self.log.debug("client initialized.")

    def identify(self, distinct_id=None, properties=None, context=None, timestamp=None, uuid=None):
        properties = properties or {}
        context = context or {}
        require("distinct_id", distinct_id, ID_TYPES)
        require("properties", properties, dict)

        msg = {
            "timestamp": timestamp,
            "context": context,
            "distinct_id": distinct_id,
            "$set": properties,
            "event": "$identify",
            "uuid": uuid,
        }

        return self._enqueue(msg)

    def track(
        self,
        distinct_id=None,
        event=None,
        properties=None,
        context=None,
        timestamp=None,
        uuid=None,
        groups=None,
    ):
        properties = properties or {}
        context = context or {}
        require("distinct_id", distinct_id, ID_TYPES)
        require("properties", properties, dict)
        require("event", event, string_types)

        msg = {
            "properties": properties,
            "timestamp": timestamp,
            "context": context,
            "distinct_id": distinct_id,
            "event": event,
            "uuid": uuid,
        }

        if groups:
            require("groups", groups, dict)
            msg["properties"]["$groups"] = groups

        return self._enqueue(msg)



def require(name, field, data_type):
    """Require that the named `field` has the right `data_type`"""
    if not isinstance(field, data_type):
        msg = "{0} must have {1}, got: {2}".format(name, data_type, field)
        raise AssertionError(msg)
