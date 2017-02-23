# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView, RedirectView
from exactonline.api import ExactApi
from exactonline.resource import GET

from exact.storage import DjangoStorage


class Authenticate(RedirectView):
	pattern_name = "exact:status"

	def get_redirect_url(self, *args, **kwargs):
		storage = DjangoStorage()
		api = ExactApi(storage=storage)
		if self.request.GET.get("code"):
			storage.set_code(self.request.GET.get("code"))

		if not storage.get_code():
			return api.create_auth_request_url()

		if not storage.get_access_token():
			api.request_token(storage.get_code())

		return super(Authenticate, self).get_redirect_url(*args, **kwargs)


class Status(TemplateView):
	template_name = "exact/status.html"
	exact = None

	def dispatch(self, request, *args, **kwargs):
		storage = DjangoStorage()
		if not storage.get_code() or not storage.get_access_token():
			return HttpResponseRedirect(reverse("exact:authenticate"))
		self.exact = ExactApi(storage=storage)
		return super(Status, self).dispatch(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		ctx = super(Status, self).get_context_data(**kwargs)
		start = datetime.now()
		ctx["division"] = self.exact.storage.get_division()
		ctx["api_user"] = self.exact.rest(GET("v1/current/Me?$select=*"))[0]
		ctx["dt"] = datetime.now() - start
		return ctx
