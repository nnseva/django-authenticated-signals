[![Build Status](https://travis-ci.org/nnseva/django-authenticated-signals.svg?branch=master)](https://travis-ci.org/nnseva/django-authenticated-signals)

# Django-Authenticated-Signals

The Django-Authenticated-Signals package provides several specialized model save and delete signals
with additional `request` parameter.

The built-in set of Django model signals pre_save, post_save, pre_delete, and post_delete
don't provide any information about the user who appears to be the running operation initiator, and other
request context.

The signals provided by the package allow to authenticate model operations for different purposes.

For example, you can create a simple and efficient universal model operation log which works automatically
for any model operation within request context.

## Installation

*Stable version* from the PyPi package repository
```bash
pip install django-authenticated-signals
```

*Last development version* from the GitHub source version control system
```bash
pip install git+git://github.com/nnseva/django-authenticated-signals.git
```

## Configuration

Include the `authenticated_signals` application into the `INSTALLED_APPS` list, like:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    ...
    'authenticated_signals',
    ...
]
```

Insert the special packet middleware into your middleware pipe:

```
MIDDLEWARE = [
    ...
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'authenticated_signals.middleware.AuthenticatedSignalsMiddleware',
    ...
]
```

## Using

### Subscribing to the signals

Use standard Django way to subscribe to the signal, like:

```
from authenticated_signals.signals import *

def q(*av,**kw):
    print "The signal has been generated:",av,kw

authenticated_post_save.connect(q)
```

Note that the request parameter may be None if:

- you didn't insert the special packet middleware into your middleware pipe
- the request is not evaluated at all, in management commands for example

You can use the following signals:

- `authenticated_pre_save` - generated from built-in Django `pre_save` signal
- `authenticated_post_save` - generated from built-in Django `post_save` signal
- `authenticated_pre_delete` - generated from built-in Django `pre_delete` signal
- `authenticated_post_delete` - generated from built-in Django `post_delete` signal

also:

- `authenticated_save` - alias for `authenticated_post_save`
- `authenticated_delete` - alias for `authenticated_pre_delete`

The `authenticated_signals.middleware.current_request()` function returns
a thread-specific current request object if it has been already catched
by the packet middleware.

You can check the request `user` or any other request attribute to authenticate
a signal in the signal processing callback function as you wish.
