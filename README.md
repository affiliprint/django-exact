Django storage and authentication view for [exactonline](https://github.com/ossobv/exactonline)
===============================================================================================

Usage
-----
install exactonline & exact & migrate... yadayadayada...

put the following in your settings.py:
```python
EXACT_ONLINE = {
    "API": "https://start.exactonline.nl/api",
    "CLIENT_ID": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "CLIENT_SECRET": "asdf",
    # oauth2 callback / redirect uri
    "CALLBACK": "http://localhost:8000/exact/authenticate",
    "DIVISION": "1234567"
}
```

urls.py:
```python
url(r'^exact/', include('exact.urls'))
```

then go to `http://localhost:8000/exact/authenticate` to start the OAuth2 dance.

then you can use it like this:
```python
    from exactonline.api import ExactApi
    from exact import DjangoStorage

    storage = DjangoStorage()
    api = ExactApi(storage=storage)
```
or
```python
    from exact.api import ExactApi
    api = ExactApi()
```