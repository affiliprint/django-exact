API Wrapper and Django app for Exact Online
===========================================

* transparently handles re-authentication. Exact's OAuth2 tokens are valid for 10 minutes
* handles pagination. `filter()` returns a generator
* uses connection keep-alive (thanks to the requests library) resulting in huge performance gain. Exact can take over 5 seconds to establish a HTTPS/TLS connection, subsequent requests are faster)

Setup
-----

install && migrate

settings.py:
```python
EXACT_ONLINE_API_URL = "https://start.exactonline.nl/api"
EXACT_ONLINE_CLIENT_ID = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
EXACT_ONLINE_CLIENT_SECRET = "asdf"
EXACT_ONLINE_REDIRECT_URI = "http://localhost:8000/exact/authenticate"
EXACT_ONLINE_DIVISION = 1234567
```

urls.py:
```python
url(r'^exact/', include(('exact.urls', 'exact'), namespace='exact'))
```


Usage
-----

go to `http://localhost:8000/exact/authenticate` to start the OAuth2 dance.

generic usage:
first param is the resource.
see [Exact Online](https://start.exactonline.nl/docs/HlpRestAPIResources.aspx) for available resources

```python
    from exact.api import Exact
    e = Exact()

    # first param is the resource.
    # see https://start.exactonline.nl/docs/HlpRestAPIResources.aspx

    # filter returns a generator and handles pagination for you
    for acc in e.filter("crm/Accounts", filter_string="substringof('GmbH', Name) eq true"):
        pass

    # can raise e.DoesNotExist and e.MultipleObjectsReturned
    e.get(resource, filter_string=None, select=None):

    e.create(resource, data)

    e.update(resource, guid, data)

    e.delete(resource, guid)
```

see [odata.org](http://www.odata.org/documentation/odata-version-2-0/uri-conventions/#FilterSystemQueryOption) for info on how to use `filter_string`


helpers:
```python
    from exact.api import Exact
    e = Exact()
    e.accounts.get(code="1234")
    e.glaccounts.get(code="1234")
    e.costcenters.get(code="12345")

```


webhooks
--------
... are easily created/deleted through /admin/exact/webhook
