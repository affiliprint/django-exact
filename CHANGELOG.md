0.8.0
-----
* fix compatibility issue with urllib3 >=2.0.0

0.7.0
-----
* Remove old storage for [exactonline](https://github.com/ossobv/exactonline)
* ignore "django_exact.egg-info" and "dist" folders in .gitignore

0.6.0
-----
* Add ability to override division setting on API instantiation (thanks to @Alex-Sichkar)
* add check if thumbnail exist in auth status template (thanks to @Alex-Sichkar)
* raise new ExactAuthException when getting/refreshing auth token fails (thanks to @Alex-Sichkar)

0.5.0
-----
* Django 4.0 compatibility

0.4.0
-----
* Retry (with backoff) when hitting 429s/Rate limiting

0.3.0
-----
* remove support for python 2.7

0.2.5
-----
* fix error reporting when getting/refreshing token fails. thanks @fijter

0.2.4
-----
* add Costunit resource

0.2.1 - 0.2.3
-------------
* improved logging/reporting when Exact errors out

0.2.0
-----
* Added `response` attribute to `ExactException`
* `DoesNotExist` and `MultipleObjectsReturned` are no longer subclasses of `ExactException`

