from typing import Callable, Dict, Optional

from usermaven.client import Client
from usermaven.version import VERSION

__version__ = VERSION

"""Settings."""
server_token = None  # type: str
host = None  # type: str
on_error = None  # type: Callable
debug = False  # type: bool
send = True  # type: bool
sync_mode = False  # type: bool
disabled = False  # type: bool

default_client = None


def track(
    api_key,        # type: str
    user,           # type: Dict
    ids,            # type: Optional[Dict]
    event_id,       # type: Optional[str]
    company={},     # type: Optional[Dict]
    src="",         # type: Optional[str]
    event_type="",  # type: Optional[str]
    custom={}       # type: Optional[Dict]
):
    # type: (...) -> None
    """
    Track allows you to track anything a user does within your system, which you can later use in Usermaven to find patterns in usage, work out which features to improve or where people are giving up.

    A `track` call requires
    - `api_key` which is your project id from which the call has been made
    - `user` which is a dict of user properties

    Optionally you can submit
    - `company`, which can be a dict with company properties
    - `event_type`, which is the type of event you are tracking
    - We recommend using [verb] [noun], like `goal created` or `payment succeeded` to easily identify what your events mean later on.
    - `custom`, which is a dict of custom properties


    For example:
    ```python
    usermaven.track('api_key', {'email': 'john@gmail.com','id': '123', 'created_at': '2022'}, event_type= 'app opened')
    usermaven.track('api_key', {'email': 'john@gmail.com','id': '123', 'created_at': '2022'}, event_id= "123-45",
    event_type ='video watched')

    usermaven.track('api_key', {'email': 'john@gmail.com','id': '123', 'created_at': '2022'}, event_id="123-45",
     company={'name': 'Company Name', 'id': '1', created_at: '2022'}, event_type ='purchase')
    ```
    """
    _proxy(
        "track",
        api_key=api_key,
        user=user,
        ids=ids,
        event_id=event_id,
        company=company,
        src=src,
        event_type=event_type,
        custom=custom
    )


def identify(
    api_key,     # type: str
    user,        # type: Dict
    ids,         # type: Optional[Dict]
    event_id,    # type: Optional[str]
    company={},  # type: Optional[Dict]
    src="",  # type: Optional[str]
    event_type="user_identify",  # type: Optional[str]
    custom={}  # type: Optional[Dict]

):
    # type: (...) -> None
    """
    Identify lets you add metadata on your users so you can more easily identify who they are in Usermaven, and even do things like segment users by these properties.

    An `identify` call requires
    - `api_key` which is your project id from which the call has been made
    - `user` which is a dict of user properties

    For example:
    ```python
    usermaven.identify('api_key', {'email': 'john@gmail.com','id': '123', 'created_at': '2022'})
    ```
    """
    _proxy(
        "identify",
        api_key=api_key,
        user=user,
        ids=ids,
        event_id=event_id,
        company=company,
        src=src,
        event_type=event_type,
        custom=custom
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
            server_token,
            host=host,
            debug=debug,
            on_error=on_error,
            send=send,
            sync_mode=sync_mode,
        )

    fn = getattr(default_client, method)
    return fn(*args, **kwargs)
