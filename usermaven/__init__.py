from typing import Callable, Dict, Optional

from usermaven.client import Client
from usermaven.version import VERSION

__version__ = VERSION

"""Settings."""
api_key = None  # type: str
host = None  # type: str
on_error = None  # type: Callable
debug = False  # type: bool
send = True  # type: bool
sync_mode = False  # type: bool
disabled = False  # type: bool
personal_api_key = None  # type: str
project_api_key = None  # type: str

default_client = None


def track(
    project_id,    # type: str
    user,          # type: Dict
    event_id,      # type: Optional[str]
    company={},    # type: Optional[Dict]
    src="",        # type: Optional[str]
    event_type=""  # type: Optional[str]
):
    # type: (...) -> None
    """
    Track allows you to track anything a user does within your system, which you can later use in Usermaven to find patterns in usage, work out which features to improve or where people are giving up.

    A `track` call requires
    - `project id` which is your project id from which the call has been made
    - `user` which is a dict of user properties

    Optionally you can submit
    - `company`, which can be a dict with company properties
    - `event_type`, which is the type of event you are tracking
    - We recommend using [verb] [noun], like `goal created` or `payment succeeded` to easily identify what your events mean later on.


    For example:
    ```python
    usermaven.track('project id', {'email': 'john@gmail.com','name': 'John Doe'}, event_type='app opened')
    usermaven.track('project id', {'email': 'john@gmail.com','name': 'John Doe'}, "123-45", event_type ='video watched')

    usermaven.track('project id', {'email': 'john@gmail.com','name': 'John Doe'}, "123-45",
     company={'name': 'Company Name'}, event_type ='purchase')
    ```
    """
    _proxy(
        "track",
        project_id=project_id,
        user=user,
        event_id=event_id,
        company=company,
        src=src,
        event_type=event_type
    )


def identify(
    project_id,  # type: str
    user,        # type: Dict
    event_id,    # type: Optional[str]
    company={},  # type: Optional[Dict]
    src="",  # type: Optional[str]
    event_type="identify"  # type: Optional[str]
):
    # type: (...) -> None
    """
    Identify lets you add metadata on your users so you can more easily identify who they are in Usermaven, and even do things like segment users by these properties.

    An `identify` call requires
    - `project id` which is your project id from which the call has been made
    - `user` which is a dict of user properties

    For example:
    ```python
    usermaven.identify('project id', {
        'email': 'john@gmail.com',
        'name': 'John Doe'
    })
    ```
    """
    _proxy(
        "identify",
        project_id=project_id,
        user=user,
        event_id=event_id,
        company=company,
        src=src,
        event_type=event_type
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
            host=host,
            debug=debug,
            on_error=on_error,
            send=send,
            sync_mode=sync_mode,
            personal_api_key=personal_api_key,
            project_api_key=project_api_key,
        )

    fn = getattr(default_client, method)
    return fn(*args, **kwargs)
