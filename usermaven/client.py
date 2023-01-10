import atexit
import logging
import random
import string

from six import string_types

from usermaven.consumer import Consumer
from usermaven.request import batch_post
from usermaven.utils import clean
from usermaven.settings import ID_TYPES

try:
    import queue
except ImportError:
    import Queue as queue


class Client(object):
    """Create a new Usermaven client."""

    log = logging.getLogger("usermaven")

    def __init__(
        self,
        api_key=None,
        server_token=None,
        host=None,
        debug=False,
        max_queue_size=10000,
        send=True,
        on_error=None,
        flush_at=100,
        flush_interval=0.5,
        max_retries=3,
        sync_mode=False,
        timeout=15,
        thread=1,
    ):

        self.queue = queue.Queue(max_queue_size)

        # api_key: This is the project_id/workspace_id which is required for authentication
        self.api_key = stringify_id(api_key)

        # server_token: This should be the server secret token used for authentication when sending the events.
        self.server_token = stringify_id(server_token)

        require("api_key", self.api_key, string_types)
        require("server_token", self.server_token, string_types)

        self.on_error = on_error
        self.debug = debug
        self.send = send
        self.sync_mode = sync_mode
        self.host = host
        self.timeout = timeout
        self.group_type_mapping = None

        if debug:
            # Ensures that debug level messages are logged when debug mode is on.
            # Otherwise, defaults to WARNING level. See https://docs.python.org/3/howto/logging.html#what-happens-if-no-configuration-is-provided
            logging.basicConfig()
            self.log.setLevel(logging.DEBUG)
        else:
            self.log.setLevel(logging.WARNING)

        if sync_mode:
            self.consumers = None
        else:
            # On program exit, allow the consumer thread to exit cleanly.
            # This prevents exceptions and a messy shutdown when the
            # interpreter is destroyed before the daemon thread finishes
            # execution. However, it is *not* the same as flushing the queue!
            # To guarantee all messages have been delivered, you'll still need
            # to call flush().
            if send:
                atexit.register(self.join)
            for n in range(thread):
                self.consumers = []
                consumer = Consumer(
                    self.queue,
                    self.api_key,
                    self.server_token,
                    host=host,
                    on_error=on_error,
                    flush_at=flush_at,
                    flush_interval=flush_interval,
                    retries=max_retries,
                    timeout=timeout,
                )
                self.consumers.append(consumer)

                # if we've disabled sending, just don't start the consumer
                if send:
                    consumer.start()

    def identify(self, user, company={}):
        require("user", user, dict)
        if "id" in user and "email" in user and "created_at" in user:
            # user object has required attributes
            require("user_id", user["id"], ID_TYPES)
            require("user_email", user["email"], string_types)
            require("user_created_at", user["created_at"], string_types)
        else:
            # user object is missing one or more of the required attributes
            raise ValueError("user object is missing one or more of the required attributes")

        msg = {
            "api_key": self.api_key,
            "event_id": "",
            "event_type": "user_identify",
            "ids": {},
            "user": {
                "anonymous_id": generate_id(),
                "id": user["id"],
                "email": user["email"],
                "created_at": user["created_at"],
            },
            "screen_resolution": "0",
            "src": "usermaven-python"
        }

        if "custom" in user:
            require("user_custom", user["custom"], dict)
            msg["user"]["custom"] = user["custom"]

        if company:
            require("company", company, dict)
            if "id" in company and "name" in company and "created_at" in company:
                # company object has required attributes
                require("company_id", company["id"], ID_TYPES)
                require("company_name", company["name"], string_types)
                require("company_created_at", company["created_at"], string_types)
            else:
                # company object is missing one or more of the required attributes
                raise ValueError("company object is missing one or more of the required attributes")

            msg["company"] = {
                "id": company["id"],
                "name": company["name"],
                "created_at": company["created_at"]
            }
            if "custom" in company:
                require("company_custom", company["custom"], dict)
                msg["company"]["custom"] = company["custom"]

        return self._enqueue(msg)

    def track(self, user_id, event_type, company={}, event_attributes={}):
        require("user_id", user_id, ID_TYPES)
        require("event_type", event_type, string_types)

        msg = {
            "api_key": self.api_key,
            "event_type": event_type,
            "event_id": "",
            "ids": {},
            "user": {
                "anonymous_id": generate_id(),
                "id": user_id
            },
            "screen_resolution": "0",
            "src": "usermaven-python",
            "event_attributes": event_attributes
        }

        if company:
            require("company", company, dict)
            if "id" in company and "name" in company and "created_at" in company:
                # company object has required attributes
                require("company_id", company["id"], ID_TYPES)
                require("company_name", company["name"], string_types)
                require("company_created_at", company["created_at"], string_types)
            else:
                # company object is missing one or more of the required attributes
                raise ValueError("company object is missing one or more of the required attributes")

            msg["company"] = {
                "id": company["id"],
                "name": company["name"],
                "created_at": company["created_at"]
            }
            if "custom" in company:
                require("company_custom", company["custom"], dict)
                msg["company"]["custom"] = company["custom"]

        return self._enqueue(msg)

    def _enqueue(self, msg):
        """Push a new `msg` onto the queue, return `(success, msg)`"""

        msg = clean(msg)
        self.log.debug("queueing: %s", msg)

        # if send is False, return msg as if it was successfully queued
        if not self.send:
            return True, msg

        if self.sync_mode:
            self.log.debug("enqueued with blocking %s.", msg["event_type"])
            batch_post(self.api_key, self.server_token, self.host, timeout=self.timeout, batch=[msg])

            return True, msg

        try:
            self.queue.put(msg, block=False)
            self.log.debug("enqueued %s.", msg["event_type"])
            return True, msg
        except queue.Full:
            self.log.warning("analytics-python queue is full")
            return False, msg

    def flush(self):
        """Forces a flush from the internal queue to the server"""
        queue = self.queue
        size = queue.qsize()
        queue.join()
        # Note that this message may not be precise, because of threading.
        self.log.debug("successfully flushed about %s items.", size)

    def join(self):
        """Ends the consumer thread once the queue is empty.
        Blocks execution until finished
        """
        for consumer in self.consumers:
            consumer.pause()
            try:
                consumer.join()
            except RuntimeError:
                # consumer thread has not started
                pass

    def shutdown(self):
        """Flush all messages and cleanly shutdown the client"""
        self.flush()
        self.join()


def require(name, field, data_type):
    """Require that the named `field` has the right `data_type`"""
    if not isinstance(field, data_type):
        msg = "{0} must have {1}, got: {2}".format(name, data_type, field)
        raise AssertionError(msg)


def stringify_id(val):
    if val is None:
        return None
    if isinstance(val, string_types):
        return val
    return str(val)


def generate_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
