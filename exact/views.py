# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging
from datetime import datetime

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseNotAllowed
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, RedirectView

from exact.api import Exact


@method_decorator(user_passes_test(lambda u: u.is_staff), name="dispatch")
class Authenticate(RedirectView):
	pattern_name = "exact:status"

	def get_redirect_url(self, *args, **kwargs):
		api = Exact()
		if self.request.GET.get("code"):
			api.session.authorization_code = self.request.GET.get("code")
			api.session.save()

		if not api.session.authorization_code:
			return api.auth_url

		if not api.session.access_token:
			api.get_token()

		return super(Authenticate, self).get_redirect_url(*args, **kwargs)


@method_decorator(user_passes_test(lambda u: u.is_staff), name="dispatch")
class Status(TemplateView):
	template_name = "exact/status.html"
	api = None

	def dispatch(self, request, *args, **kwargs):
		api = Exact()
		if not api.session.authorization_code or not api.session.access_token:
			return HttpResponseRedirect(reverse("exact:authenticate"))
		self.api = api
		return super(Status, self).dispatch(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		ctx = super(Status, self).get_context_data(**kwargs)
		start = datetime.now()
		ctx["division"] = self.api.session.division
		# eval generator to force a possible re-auth
		ctx["webhooks"] = list(self.api.filter("webhooks/WebhookSubscriptions"))

		# fake division. this endpoint only works with "current"
		# make sure we are authenticated first, or api.get()/authenticate/refresh will try to save the session
		# which fails since "current" is not an integer
		# yeah, it's ugly :)
		_real_division = self.api.session.division
		self.api.session.division = "current"
		ctx["api_user"] = self.api.get("Me")
		self.api.session.division = _real_division

		ctx["dt"] = datetime.now() - start
		return ctx


@csrf_exempt
def webhook(request):
	# TODO: show how to validate request
	logger = logging.getLogger("exact")
	if request.method != "POST":
		return HttpResponseNotAllowed(["POST"])
	if len(request.body) == 0:
		return HttpResponse()
	try:
		data = json.loads(request.body)
		logger.debug(data)
		return HttpResponse(request.body)
	except Exception as e:
		logger.debug("error: " + request.body)
		return HttpResponseBadRequest(e)

