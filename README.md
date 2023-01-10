<p align="center">
  <a href="https://usermaven.com/">
    <img src="usermaven/assets/images/logos/usermaven-logo.png" height="60">
  </a>
  <p align="center">PRIVACY-FRIENDLY ANALYTICS TOOL</p>
</p>


# Usermaven-python 

This module is compatible with Python 3.6 and above.

## Installing

```bash
pip3 install usermaven-python
```

## Usage

```python
from usermaven import Client
client = Client(api_key='api_key', server_token="server_token")
client.identify({'email': 'john@gmail.com','id': '123', 'created_at': '2022'})
client.track('user_id', 'signed_up')
```

### Instantiating usermaven-python's client object

Create an instance of the client with your Usermaven workspace credentials.

```python
from usermaven import Client
client = Client(api_key="api_key", server_token="server_token")
```

### Create a Usermaven user profile

```python
client.identify({'email': 'john@gmail.com','id': '123', 'created_at': '2022'})
```

#### Required arguments
`user`: The user object is the only required argument for `identify` call. `email`, `id` and `created_at` are required
fields for the user object. Recommended fields for the user object are `first_name` and `last_name`. Additionally you 
can pass any custom properties in the form of dictionary to your user object.

#### Optional arguments
You can also pass optional arguments to the `identify` method.

`company`: A company object for which the user belongs to. It is optional but if it is passed, it must contain `name`,
`id` and `created_at` fields. You can also submit custom properties in the form of dictionary for the company object. 
Example:
```python
client.identify({'email': 'john@gmail.com','id': '123', 'created_at': '2022'}, 
                company={'name': 'usermaven', 'id': '5', 'created_at': '2022',
                         'custom': {'plan': 'enterprise', 'industry': 'Technology'}})
```

### Track a custom event

```python
client.track('user_id', 'plan_purchased')
```

#### Required arguments
`user_id`: For the `track` call, you must pass the `user_id` of the user you want to track the event for.

`event_type`: For track call, `event_type` is a required argument and you must pass a value to the event_type.
We recommend using [verb] [noun], like `goal created` or `payment succeeded` to easily identify what your events mean
later on.

#### Optional arguments
You can also pass optional arguments to the `track` method.

`company`: A company object for which the user belongs to. It is optional but if it is passed, it must contain `name`,
`id` and `created_at` fields. You can also submit custom properties in the form of dictionary for the company object. 
Example:
```python
client.track('user_id', 'signed_up', company={'name': 'usermaven', 'id': '5', 'created_at': '2022',
                                              'custom': {'plan': 'enterprise', 'industry': 'Technology'}})
```

`event_attributes`: This can contain information related to the event that is being tracked. Example:
```python
client.track('user_id', 'video_watched', event_attributes={'video_title': 'demo', 'watched_at': '2022'})
```

## Local Setup for Development
For local development, you can clone the repository and install the dependencies using the following commands:

```bash
git clone "https://github.com/usermaven/usermaven-python.git"
poetry install
```

## Running tests

Changes to the library can be tested by running `python -m unittest -v` from the parent directory.
