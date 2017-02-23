# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Session


class SessionAdmin(admin.ModelAdmin):
	model = Session
	list_display = ["id", "rest_url", "base_url", "client_id"]
admin.site.register(Session, SessionAdmin)
