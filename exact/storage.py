# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from exactonline.storage import ExactOnlineConfig

from exact.models import Session


def get(option):
	try:
		return settings.EXACT_ONLINE[option]
	except:
		raise ImproperlyConfigured("Exact: Setting for '%s' not found!" % option)

EXACT_SETTINGS = {
	"base_url": get("CALLBACK"),
	"client_id": get("CLIENT_ID"),
	"client_secret": get("CLIENT_SECRET"),
	"auth_url": get("API") + "/oauth2/auth",
	"token_url": get("API") + "/oauth2/token",
	"rest_url": get("API"),
	"division": get("DIVISION")
}


class DjangoStorage(ExactOnlineConfig):
	def __init__(self):
		s, created = Session.objects.get_or_create(**EXACT_SETTINGS)
		self._session = s

	def get(self, section, option):
		return getattr(self._session, option)

	def set(self, section, option, value):
		setattr(self._session, option, value)
		self._session.save()
