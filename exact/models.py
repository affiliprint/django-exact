# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Session(models.Model):
	base_url = models.URLField(_("OAuth2 redirect URL"))
	client_id = models.CharField(max_length=255)
	client_secret = models.CharField(max_length=255)

	auth_url = models.URLField(_("OAuth2 auth URL"))
	token_url = models.URLField(_("OAuth2 token URL"))
	rest_url = models.URLField(_("API base URL"))

	access_expiry = models.CharField(max_length=255, blank=True, default="")
	access_token = models.TextField(blank=True, default="")
	refresh_token = models.TextField(blank=True, default="")
	code = models.TextField(blank=True, default="")

	division = models.TextField()
