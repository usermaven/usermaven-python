# Usermaven-python 

## Installing

```bash
pip3 install usermaven-python
```

## Usage

```python
from usermaven import Client
client = Client(api_key='api_key', server_token="server_token")
client.identify({'email': 'john@gmail.com','id': '123', 'created_at': '2022'})
client.track('signed_up', {'email': 'john@gmail.com','id': '123', 'created_at': '2022'})
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

### Track a custom event

```python
client.track('plan_purchased', {'email': 'john@gmail.com','id': '123', 'created_at': '2022'})
```

#### Required arguments
`user`: This is a required argument for `identify` and `track` call. `email`, `id` and `created_at` are required fields
for the user object. It can also contain additional fields like `first_name`, `last_name` etc.

`event_type`: For identify call, event_type is an optional argument and the default event_type is `user_identify`.
However for track call, it is required and you must pass a value to the event_type. We recommend using [verb] [noun],
like `goal created` or `payment succeeded` to easily identify what your events mean later on.

#### Optional arguments
You can also pass optional arguments to the `identify` and `track` methods.

`company`: A company object for which the user belongs to. It is optional but if it is passed, it must contain `name`,
`id` and `created_at` fields. Example:
```python
client.track('signed_up', {'email': 'john@gmail.com','id': '123', 'created_at': '2022'}, company={'name': 'usermaven', 'id': '5', 'created_at': '2022'})
```

`event_attributes`: Only for the track call. This can contain information related to the event that is being tracked. Example:
```python
client.track('video_watched', {'email': 'john@gmail.com','id': '123', 'created_at': '2022'}, event_attributes={'video_title': 'demo', 'watched_at': '2022'})
```

`custom`: You can pass your own custom attributes if you want in this. It must be a dictionary and it can contain
any kwargs. Example:
```python
client.track('plan_purchased', {'email': 'john@gmail.com','id': '123', 'created_at': '2022'}, custom={'plan': 'premium', 'product': 'usermaven'})
```
