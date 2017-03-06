# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import time

import requests
from requests import Request

from exactonline.api import ExactApi as OriginalExactApi

from exact.models import Session
from exact.storage import EXACT_SETTINGS


logger = logging.getLogger("exact")


class ExactException(Exception):
	pass


class DoesNotExist(ExactException):
	pass


class MultipleObjectsReturned(ExactException):
	pass


class Exact:
	# this is only for benchmarking
	# exact needs ~5.5 seconds to open a https connection
	# so reusing it speeds things up a lot. (~200ms per call)
	_REUSE_SESSION = True

	def __init__(self):
		s, created = Session.objects.get_or_create(**EXACT_SETTINGS)
		self.session = s
		self.requests_session = requests.Session()
		# set default headers for this session
		self.requests_session.headers.update({
			"Accept": "application/json",
			"Authorization": "Bearer %s" % self.session.access_token
		})

	def refresh_token(self):
		logger.debug("refreshing token")
		args = {
			'client_id': self.session.client_id,
			'client_secret': self.session.client_secret,
			'grant_type': 'refresh_token',
			'refresh_token': self.session.refresh_token
		}

		req = Request("POST", self.session.api_url + "/oauth2/token", data=args)
		prepped = self.requests_session.prepare_request(req)
		# exact fails/returns 401 if we send an auth header while refreshing
		prepped.headers["Authorization"] = None
		r = self.requests_session.send(prepped)
		if r.status_code != 200:
			raise ExactException("unexpected response while refreshing token: %s", r.text)
		decoded = r.json()
		self.session.access_token = decoded["access_token"]
		self.session.refresh_token = decoded["refresh_token"]
		# TODO: use access_expiry to avoid an unnecessary request if we know we will need to re-auth
		self.session.access_expiry = int(time.time()) + int(decoded["expires_in"])
		self.session.save()
		self.requests_session.headers["Authorization"] = "Bearer %s" % self.session.access_token
		logger.debug("done refreshing token")

	def _send(self, method, resource, data=None, params=None):
		# to test performance penalty of not using a requests session
		if not self._REUSE_SESSION:
			self.requests_session = requests.Session()
			self.requests_session.headers.update({
				"Accept": "application/json",
				"Authorization": "Bearer %s" % self.session.access_token
			})
		url = "%s/v1/%s/%s" % (self.session.api_url, self.session.division, resource)
		request = Request(method, url, data=data, params=params)
		prepped = self.requests_session.prepare_request(request)
		if method in ("POST", "PUT"):
			# only update headers for this request, not updating session
			prepped.headers.update({
				"Content-Type": "application/json",
				"Prefer": "return=representation"
			})
		r = self.requests_session.send(prepped)
		if r.status_code == 401:
			self.refresh_token()
			# prepare again to use new auth-header
			prepped = self.requests_session.prepare_request(request)
			r = self.requests_session.send(prepped)

		# at this point we tried to re-auth, so anything but 200/OK is unexpected
		if r.status_code != 200:
			raise ExactException(r.text)
		return r.json()

	def get(self, resource, filter_string="", select="ID,Name,Code"):
		params = {
			"$top": 2,
			"$select": select,
			"$filter": filter_string
		}
		r = self._send("GET", resource, params=params)

		data = r["d"]
		if len(data) == 0:
			raise DoesNotExist("recource not found. params were: %r" % params)
		if len(data) > 1:
			raise MultipleObjectsReturned("api returned multiple objects. params were: %r" % params)
		return data[0]

	def find(self, resource, filter_string="", select="ID,Name,Code", top=None):
		# TODO: implement pagination
		params = {
			"$top": top,
			"$select": select,
			"$filter": filter_string
		}
		r = self._send("GET", resource, params=params)
		data = r["d"]
		return data


# legacy
class ExactApi(OriginalExactApi):
	def __init__(self, **kwargs):
		from exact.storage import DjangoStorage
		storage = DjangoStorage()
		kwargs["storage"] = storage
		super(ExactApi, self).__init__(**kwargs)

