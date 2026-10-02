SECRET_KEY = "tests"
INSTALLED_APPS = [
	"django.contrib.auth",
	"django.contrib.contenttypes",
	"django.contrib.sites",
	"exact.app.Config",
]
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
ROOT_URLCONF = "tests.urls"
SITE_ID = 1
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

EXACT_ONLINE_API_URL = "https://exact.test/api"
EXACT_ONLINE_CLIENT_ID = "client-id"
EXACT_ONLINE_CLIENT_SECRET = "client-secret"
EXACT_ONLINE_REDIRECT_URI = "https://example.com/exact/authenticate"
EXACT_ONLINE_DIVISION = 1
