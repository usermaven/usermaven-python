from typing import Callable, Dict, Optional

from usermaven.client import Client
from usermaven.version import VERSION

__version__ = VERSION

"""Settings."""
api_key = None  # type: str
server_token = None  # type: str
host = None  # type: str
on_error = None  # type: Callable
debug = False  # type: bool
send = True  # type: bool
sync_mode = False  # type: bool
disabled = False  # type: bool

default_client = None


def track(
    user_id,              # type: str
    event_type,           # type: str
    company={},           # type: Optional[Dict]
    event_attributes={},  # type: Optional[Dict]
):
    # type: (...) -> None
    """
    Track allows you to track anything a user does within your system, which you can later use in Usermaven
    to find patterns in usage, work out which features to improve or where people are giving up.

    A `track` call requires
    - `user_id` which is the unique identifier for the user.
    - `event_type` which defines what sort of event are you tracking from this call. We recommend using [verb] [noun],
     like `goal created` or `payment succeeded` to easily identify what your events mean later on.

    Optionally you can submit
    - `company`, which is a dict with company properties. Name, id and created_at are required fields for the
    company object. You can also submit custom properties for the company object.
    - 'event_attributes', which is a dict that contain information about the event.


    For example:
    ```python
    usermaven.track('user_id', 'payment_succeeded')
    usermaven.track('user_id', 'video_watched', 'event_attributes'={'video_title': 'demo', 'watched_at': '2022'})
    usermaven.track('user_id', 'plan_purchased', company={'name': 'Company Name', 'id': '1', 'created_at': '2022',
    'custom': {'plan': 'enterprise', 'industry': 'Technology'}}, event_attributes={'plan': 'premium'})
    ```
    """
    _proxy(
        "track",
        user_id=user_id,
        event_type=event_type,
        company=company,
        event_attributes=event_attributes
    )


def identify(
    user,        # type: Dict
    company={},  # type: Optional[Dict]
):
    # type: (...) -> None
    """
    Identify lets you add metadata to the user so you can know who they are in Usermaven.

    An `identify` call requires
    - `user` which is a dict of user properties. Email, id and created_at are required fields for the user object.
    You can also submit custom properties for the user object.

    For example:
    ```python
    usermaven.identify({'email': 'john@gmail.com','id': '123', 'created_at': '2022'})
    ```
    Optionally you can submit
    - `company`, which is a dict with company properties. Name, id and created_at are required fields for the
    company object. You can also submit custom properties for the company object.

    """
    _proxy(
        "identify",
        user=user,
        company=company
    )


def flush():
    """Tell the client to flush."""
    _proxy("flush")


def join():
    """Block program until the client clears the queue"""
    _proxy("join")


def shutdown():
    """Flush all messages and cleanly shutdown the client"""
    _proxy("flush")
    _proxy("join")


def _proxy(method, *args, **kwargs):
    """Create an analytics client if one doesn't exist and send to it."""
    global default_client
    if disabled:
        return None
    if not default_client:
        default_client = Client(
            api_key,
            server_token,
            host=host,
            debug=debug,
            on_error=on_error,
            send=send,
            sync_mode=sync_mode,
        )

    fn = getattr(default_client, method)
    return fn(*args, **kwargs)
