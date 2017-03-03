# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from datetime import datetime

import logging
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseNotAllowed
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
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
		ctx["webhooks"] = self.exact.restv1(GET("webhooks/WebhookSubscriptions"))
		ctx["dt"] = datetime.now() - start
		return ctx


@csrf_exempt
def webhook(request):
	logger = logging.getLogger("exact")
	if request.method != "POST":
		return HttpResponseNotAllowed(["POST"])
	try:
		data = json.loads(request.body)
		logger.debug(data)
		return HttpResponse(request.body)
	except Exception as e:
		return HttpResponseBadRequest(e)

