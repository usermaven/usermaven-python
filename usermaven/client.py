import atexit
import logging
import numbers
from datetime import datetime
from uuid import UUID

from six import string_types

from usermaven.consumer import Consumer
from usermaven.request import batch_post
from usermaven.utils import clean

try:
    import queue
except ImportError:
    import Queue as queue


ID_TYPES = (numbers.Number, string_types, UUID)


class Client(object):
    """Create a new Usermaven client."""

    log = logging.getLogger("usermaven")

    def __init__(
        self,
        api_key=None,
        host=None,
        debug=False,
        max_queue_size=10000,
        send=True,
        on_error=None,
        flush_at=100,
        flush_interval=0.5,
        gzip=False,
        max_retries=3,
        sync_mode=False,
        timeout=15,
        thread=1,
        personal_api_key=None,
        project_api_key=None,
    ):

        self.queue = queue.Queue(max_queue_size)

        # api_key: This should be the Team API Key (token), public
        self.api_key = project_api_key or api_key

        require("api_key", self.api_key, string_types)

        self.on_error = on_error
        self.debug = debug
        self.send = send
        self.sync_mode = sync_mode
        self.host = host
        self.gzip = gzip
        self.timeout = timeout
        self.group_type_mapping = None

        # personal_api_key: This should be a generated Personal API Key, private
        self.personal_api_key = personal_api_key
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
                    host=host,
                    on_error=on_error,
                    flush_at=flush_at,
                    flush_interval=flush_interval,
                    gzip=gzip,
                    retries=max_retries,
                    timeout=timeout,
                )
                self.consumers.append(consumer)

                # if we've disabled sending, just don't start the consumer
                if send:
                    consumer.start()


    def identify(self, project_id, user, event_id="", company={}, src="", event_type="identify"):
        require("project_id", project_id, ID_TYPES)
        require("user", user, dict)

        msg = {
            "project_id": project_id,
            "event_id": event_id,
            "user": user,
            "utc_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "local_tz_offset": (datetime.now() - datetime.utcnow()).total_seconds() / 60,
            "company": company,
            "api_key": self.api_key,
            "src": src,
            "event_type": event_type
        }

        return self._enqueue(msg)

    def track(self, project_id, user, event_id="", company={}, src="", event_type=""):
        require("project_id", project_id, ID_TYPES)
        require("user", user, dict)

        msg = {
            "project_id": project_id,
            "event_id": event_id,
            "user": user,
            "utc_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "local_tz_offset": (datetime.now() - datetime.utcnow()).total_seconds() / 60,
            "company": company,
            "api_key": self.api_key,
            "src": src,
            "event_type": event_type
        }

        return self._enqueue(msg)


    def _enqueue(self, msg):
        """Push a new `msg` onto the queue, return `(success, msg)`"""

        msg["project_id"] = stringify_id(msg.get("project_id", None))

        msg = clean(msg)
        self.log.debug("queueing: %s", msg)

        # if send is False, return msg as if it was successfully queued
        if not self.send:
            return True, msg

        if self.sync_mode:
            self.log.debug("enqueued with blocking %s.", msg["event_type"])
            batch_post(self.api_key, self.host, gzip=self.gzip, timeout=self.timeout, batch=[msg])

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
