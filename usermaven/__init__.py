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
    distinct_id,  # type: str
    event,  # type: str
    properties=None,  # type: Optional[Dict]
    context=None,  # type: Optional[Dict]
    timestamp=None,  # type: Optional[datetime.datetime]
    uuid=None,  # type: Optional[str]
    groups=None,  # type: Optional[Dict]
    # send_feature_flags=False,
):
    # type: (...) -> None
    """
    Track allows you to track anything a user does within your system, which you can later use in Usermaven to find patterns in usage, work out which features to improve or where people are giving up.

    A `track` call requires
    - `distinct id` which uniquely identifies your user
    - `event name` to specify the event
    - We recommend using [verb] [noun], like `goal created` or `payment succeeded` to easily identify what your events mean later on.

    Optionally you can submit
    - `properties`, which can be a dict with any information you'd like to add
    - `groups`, which is a dict of group type -> group key mappings

    For example:
    ```python
    usermaven.track('distinct id', 'app opened')
    usermaven.track('distinct id', 'video watched', {'video_id': '123', 'category': 'demo'})

    usermaven.track('distinct id', 'purchase', groups={'company': 'id:5'})
    ```
    """
    _proxy(
        "track",
        distinct_id=distinct_id,
        event=event,
        properties=properties,
        context=context,
        timestamp=timestamp,
        uuid=uuid,
        groups=groups,
    )


def identify(
    distinct_id,  # type: str
    properties=None,  # type: Optional[Dict]
    context=None,  # type: Optional[Dict]
    timestamp=None,  # type: Optional[datetime.datetime]
    uuid=None,  # type: Optional[str]
):
    # type: (...) -> None
    """
    Identify lets you add metadata on your users so you can more easily identify who they are in Usermaven, and even do things like segment users by these properties.

    An `identify` call requires
    - `distinct id` which uniquely identifies your user
    - `properties` with a dict with any key: value pairs

    For example:
    ```python
    usermaven.identify('distinct id', {
        'email': 'john@gmail.com',
        'name': 'John Doe'
    })
    ```
    """
    _proxy(
        "identify",
        distinct_id=distinct_id,
        properties=properties,
        context=context,
        timestamp=timestamp,
        uuid=uuid,
    )


def set(
    distinct_id,  # type: str,
    properties=None,  # type: Optional[Dict]
    context=None,  # type: Optional[Dict]
    timestamp=None,  # type: Optional[datetime.datetime]
    uuid=None,  # type: Optional[str]
):
    # type: (...) -> None
    """
    Set properties on a user record.
    This will overwrite previous people property values, just like `identify`.

     A `set` call requires
     - `distinct id` which uniquely identifies your user
     - `properties` with a dict with any key: value pairs

     For example:
     ```python
     usermaven.set('distinct id', {
         'current_browser': 'Chrome',
     })
     ```
    """
    _proxy(
        "set",
        distinct_id=distinct_id,
        properties=properties,
        context=context,
        timestamp=timestamp,
        uuid=uuid,
    )


def set_once(
    distinct_id,  # type: str,
    properties=None,  # type: Optional[Dict]
    context=None,  # type: Optional[Dict]
    timestamp=None,  # type: Optional[datetime.datetime]
    uuid=None,  # type: Optional[str]
):
    # type: (...) -> None
    """
    Set properties on a user record, only if they do not yet exist.
    This will not overwrite previous people property values, unlike `identify`.

     A `set_once` call requires
     - `distinct id` which uniquely identifies your user
     - `properties` with a dict with any key: value pairs

     For example:
     ```python
     usermaven.set_once('distinct id', {
         'referred_by': 'friend',
     })
     ```
    """
    _proxy(
        "set_once",
        distinct_id=distinct_id,
        properties=properties,
        context=context,
        timestamp=timestamp,
        uuid=uuid,
    )


def group_identify(
    group_type,  # type: str
    group_key,  # type: str
    properties=None,  # type: Optional[Dict]
    context=None,  # type: Optional[Dict]
    timestamp=None,  # type: Optional[datetime.datetime]
    uuid=None,  # type: Optional[str]
):
    # type: (...) -> None
    """
    Set properties on a group

     A `group_identify` call requires
     - `group_type` type of your group
     - `group_key` unique identifier of the group
     - `properties` with a dict with any key: value pairs

     For example:
     ```python
     usermaven.group_identify('company', 5, {
         'employees': 11,
     })
     ```
    """
    _proxy(
        "group_identify",
        group_type=group_type,
        group_key=group_key,
        properties=properties,
        context=context,
        timestamp=timestamp,
        uuid=uuid,
    )


def alias(
    previous_id,  # type: str,
    distinct_id,  # type: str,
    context=None,  # type: Optional[Dict]
    timestamp=None,  # type: Optional[datetime.datetime]
    uuid=None,  # type: Optional[str]
):
    # type: (...) -> None
    """
    To marry up whatever a user does before they sign up or log in with what they do after you need to make an alias call. This will allow you to answer questions like "Which marketing channels leads to users churning after a month?" or "What do users do on our website before signing up?"

    In a purely back-end implementation, this means whenever an anonymous user does something, you'll want to send a session ID ([Django](https://stackoverflow.com/questions/526179/in-django-how-can-i-find-out-the-request-session-sessionid-and-use-it-as-a-vari), [Flask](https://stackoverflow.com/questions/15156132/flask-login-how-to-get-session-id)) with the track call. Then, when that users signs up, you want to do an alias call with the session ID and the newly created user ID.

    The same concept applies for when a user logs in.

    An `alias` call requires
    - `previous distinct id` the unique ID of the user before
    - `distinct id` the current unique id

    For example:
    ```python
    usermaven.alias('anonymous session id', 'distinct id')
    ```
    """
    _proxy(
        "alias",
        previous_id=previous_id,
        distinct_id=distinct_id,
        context=context,
        timestamp=timestamp,
        uuid=uuid,
    )


def page(*args, **kwargs):
    """Send a page call."""
    _proxy("page", *args, **kwargs)


def screen(*args, **kwargs):
    """Send a screen call."""
    _proxy("screen", *args, **kwargs)


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
            poll_interval=poll_interval,
        )

    fn = getattr(default_client, method)
    return fn(*args, **kwargs)
