# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from exactonline.storage import ExactOnlineConfig

from exact.models import Session


def get(option):
	try:
		return getattr(settings, "EXACT_ONLINE_" + option)
	except AttributeError:
		raise ImproperlyConfigured("Exact: Setting '%s' not found!" % option)


EXACT_SETTINGS = {
	"redirect_uri": get("REDIRECT_URI"),
	"client_id": get("CLIENT_ID"),
	"client_secret": get("CLIENT_SECRET"),
	"api_url": get("API_URL"),
	"division": get("DIVISION")
}


class DjangoStorage(ExactOnlineConfig):
	def __init__(self):
		s, created = Session.objects.get_or_create(**EXACT_SETTINGS)
		self._session = s

	def get_auth_url(self):
		return self._session.api_url + "/oauth2/auth"

	def get_rest_url(self):
		return self._session.api_url

	def get_token_url(self):
		return self._session.api_url + "/oauth2/token"

	def get_base_url(self):
		return self._session.redirect_uri

	def get_client_id(self):
		return self._session.client_id

	def get_client_secret(self):
		return self._session.client_secret

	def get_access_expiry(self):
		return self._session.access_expiry

	def set_access_expiry(self, value):
		self._session.access_expiry = value
		self._session.save()

	def get_access_token(self):
		return self._session.access_token

	def set_access_token(self, value):
		self._session.access_token = value
		self._session.save()

	def get_code(self):
		return self._session.authorization_code

	def set_code(self, value):
		self._session.authorization_code = value
		self._session.save()

	def get_division(self):
		return self._session.division

	def set_division(self, value):
		self._session.division = value
		self._session.save()

	def get_refresh_token(self):
		return self._session.refresh_token

	def set_refresh_token(self, value):
		self._session.refresh_token = value
		self._session.save()
