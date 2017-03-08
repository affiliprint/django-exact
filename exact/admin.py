# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.contrib import admin

from .models import Session, Webhook


class SessionAdmin(admin.ModelAdmin):
	model = Session
	list_display = ["id", "api_url", "redirect_uri", "client_id"]
admin.site.register(Session, SessionAdmin)


# TODO: maybe use a better validation than just failing in pre_save/post_delete :)
class WebhookAdminForm(forms.ModelForm):
	class Meta:
		model = Webhook
		exclude = []

	def clean(self):
		if not self.changed_data:
			return

		#api = ExactApi()


class WebhookAdmin(admin.ModelAdmin):
	model = Webhook
	# form = WebhookAdminForm
	list_display = ["topic", "callback"]
admin.site.register(Webhook, WebhookAdmin)
