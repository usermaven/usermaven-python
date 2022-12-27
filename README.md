# Usermaven-python 

## Installing

```bash
pip3 install usermaven-python
```

## Usage

```python
from usermaven import Client
client = Client(server_token="server_token")
client.identify('api_key', {'email': 'john@gmail.com','id': '123', 'created_at': '2022'})
client.track('api_key', {'email': 'john@gmail.com','id': '123', 'created_at': '2022'}, event_type= 'signed_up')
client.track('api_key', {'email': 'john@gmail.com','id': '123', 'created_at': '2022'}, event_type= 'video_watched',
             company={'name': 'John','id': '5', 'created_at': '2022'})
```

### Instantiating usermaven-python's client object

Create an instance of the client with your Usermaven workspace credentials.

```python
from usermaven import Client
client = Client(server_token="server_token")
```

### Create a Usermaven user profile

```python
client.identify('api_key', {'email': 'john@gmail.com','id': '123', 'created_at': '2022'})
```

### Track a custom event

```python
client.track('api_key', {'email': 'john@gmail.com','id': '123', 'created_at': '2022'}, event_type="signed_up")
```

`api_key`: This is the first and a must required argument for `identify` and `track` call. It is your project/workspace id.
`user`: This is the second and also a must required argument for `identify` and `track` call. It is the user object 
which must be passed and should contain `email`, `id` and `created_at`. Otherwise the call won't be successful. 
Example: user = {'email': 'john@gmail.com',  -- Required
                 'id': '123',     -- Required
                 'created_at': '2022',  -- Required
                 'first_name': 'John',   -- Optional
                 'last_name': 'Doe'     -- Optional
                 }

You can also pass optional arguments to the `identify` and `track` methods. These optional arguments include event_id,
ids, company, src, event_type, custom.

`event_id`: Event id for which the call is being made.
`ids` : Linked social accounts ids.
`company`: A company object for which the user belongs to. It is optional but if it is passed, it must follow the 
following schema.
Example: company = {'name': 'Usermaven',  -- Required
                    'id': '5',     -- Required
                    'created_at': '2022',  -- Required
                    }
`src`: Source of the event.
`event_type`: For identify call, the default event_type is `user_identify`. For track call, you can pass any value to
the event_type.
`custom`: You can pass your own custom attributes if you want in this. It must be a dictionary and it can contain
any kwargs. Example: custom = {'plan': 'premium',
                               'expires_at': '2025'
                              }
