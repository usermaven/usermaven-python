<p align="center">
  <a href="https://usermaven.com/">
    <picture>
        <source media="(prefers-color-scheme: dark)" srcset="https://storage.googleapis.com/lumotive-web-storage/usermaven/usermaven-white.png" height="60">
        <img alt="Dark/Light mode logos" src="https://storage.googleapis.com/lumotive-web-storage/usermaven/usermaven-dark.webp" height="60">
    </picture>
  </a>
  <p align="center">PRIVACY-FRIENDLY ANALYTICS TOOL</p>
</p>

![PyPI](https://img.shields.io/badge/pypi-v0.1.1-blue)
![Software License](https://img.shields.io/badge/license-MIT-green)
![PyPI - Python Version](https://img.shields.io/badge/python-3.6%20and%20above-blue)

# Usermaven Python 

This module is compatible with Python 3.6 and above.

## Installing

```bash
pip3 install usermaven
```

## Usage

```python
from usermaven import Client
client = Client(api_key='your_workspace_api_key', server_token="your_workspace_server_token")
client.identify(user={'email': 'user@domain.com','id': 'lzL24K3kYw', 'created_at': '2022-01-20T09:55:35'})
client.track(user_id='lzL24K3kYw', event_type='signed_up')
```

### Instantiating usermaven-python's client object

Create an instance of the client with your Usermaven workspace credentials.

```python
from usermaven import Client
client = Client(api_key='your_workspace_api_key', server_token="your_workspace_server_token")
```

### Create a Usermaven user profile

```python
client.identify(user={'email': 'user@domain.com','id': 'lzL24K3kYw', 'created_at': '2022-01-20T09:55:35'})
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
client.identify(user={
    # Required attributes of user object
    'email': 'user@domain.com', 'id': 'lzL24K3kYw', 'created_at': '2022-01-20T09:55:35',
    
    # Recommended attributes - First name and last name are shown on people pages.
    'first_name': 'John', 'last_name': 'Smith',
    
    # Optional attributes (you can name attributes what you wish)
    'custom': {'plan_name': 'premium'}
    }, 
    
    # If your product is used by multiple users in a company, we recommend to pass the Company attributes.
    company={
        # Required attributes of company object
        'name': 'Usermaven', 'id': 'uPq9oUGrIt', 'created_at': '2022-01-20T09:55:35',
        
        # Optional attributes such as industry, website, employee count etc.
        'custom': {'plan': 'enterprise', 'industry': 'Technology', 'website': 'https://usermaven.com', 
                   'employees': '20'}
    })
```

### Track a custom event

```python
client.track(user_id='lzL24K3kYw', event_type='plan_purchased')
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

`event_attributes`: This can contain information related to the event that is being tracked. Example:
```python
client.track(
    user_id='lzL24K3kYw', # Unique ID for the user in database. (Required)
    event_type='plan_purchased', # Event name to be tracked (Required)
    
    # Optional attributes
    company={
        # Required attributes of company object
        'name': 'Usermaven', 'id': 'uPq9oUGrIt', 'created_at': '2022-01-20T09:55:35',
        
        # Optional attributes such as industry, website, employee count etc.
        'custom': {'plan': 'enterprise', 'industry': 'Technology', 'website': 'https://usermaven.com', 
                   'employees': '20'}
        },
    
    event_attributes={
        'plan_name': 'premium',
        'plan_price': '100',
        'plan_currency': 'USD'
        }
    )
```

## Local Setup for Development
For local development, you can clone the repository and install the dependencies using the following commands:

```bash
git clone "https://github.com/usermaven/usermaven-python.git"
poetry install
```

## Running tests

Changes to the library can be tested by running `python -m unittest -v` from the parent directory.
