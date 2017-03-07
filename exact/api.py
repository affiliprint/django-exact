# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging
import time

from requests import Request, Session as ReqSession

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


class Resource(object):
	resource = ""
	DoesNotExist = DoesNotExist
	MultipleObjectsReturned = MultipleObjectsReturned

	def __init__(self, api):
		self._api = api

	# i am not using *args, and **kwargs (would be more generic) for make autocomplete/hints in IDE work better
	def filter(self, filter_string=None, select=None, order_by=None, limit=None):
		return self._api.filter(self.resource, filter_string=filter_string, select=select, order_by=order_by, limit=limit)

	def get(self, filter_string=None, select=None):
		return self._api.get(self.resource, filter_string=filter_string, select=select)

	def create(self, data):
		return self._api.create(self.resource, data)

	def update(self, guid, data):
		return self._api.update(self.resource, guid, data)

	def delete(self, guid):
		return self._api.delete(self.resource, guid)


# example of simplifying some resources
class Costcenters(Resource):
	resource = "hrm/Costcenters"

	def get(self, code=None, filter_string=None, select=None):
		if code is not None:
			if filter_string:
				filter_string += " and Code eq '%s'" % code
			else:
				filter_string = "Code eq '%s'" % code
		return super(Costcenters, self).get(filter_string=filter_string, select=select)


class Exact(object):
	DoesNotExist = DoesNotExist
	MultipleObjectsReturned = MultipleObjectsReturned
	# this is only for benchmarking
	# exact needs ~5.5 seconds to open a https connection
	# so reusing it speeds things up a lot. (~200ms per call)
	_REUSE_SESSION = True

	def __init__(self):
		s, created = Session.objects.get_or_create(**EXACT_SETTINGS)
		self.session = s
		self.requests_session = ReqSession()
		# set default headers for this session
		self.requests_session.headers.update({
			"Accept": "application/json",
			"Authorization": "Bearer %s" % self.session.access_token,
			"Content-Type": "application/json",
			"Prefer": "return=representation",
		})

		self.costcenters = Costcenters(self)

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
		# this is also the only request which is not "application/json"
		prepped.headers["Content-Type"] = "application/x-www-form-urlencoded"

		r = self.requests_session.send(prepped)
		if r.status_code != 200:
			raise ExactException("unexpected response while refreshing token: %s", r.text)
		decoded = r.json()
		self.session.access_token = decoded["access_token"]
		self.session.refresh_token = decoded["refresh_token"]
		# TODO: use access_expiry to avoid an unnecessary request if we know we will need to re-auth
		self.session.access_expiry = int(time.time()) + int(decoded["expires_in"])
		self.session.save()
		# add new token to default headers
		self.requests_session.headers["Authorization"] = "Bearer %s" % self.session.access_token
		logger.debug("done refreshing token")

	def _send(self, method, resource, data=None, params=None):
		# to test performance penalty of not using a requests session
		if not self._REUSE_SESSION:
			self.requests_session = ReqSession()
			self.requests_session.headers.update({
				"Accept": "application/json",
				"Authorization": "Bearer %s" % self.session.access_token,
				"Content-Type": "application/json",
				"Prefer": "return=representation",
			})

		url = "%s/v1/%s/%s" % (self.session.api_url, self.session.division, resource)
		request = Request(method, url, data=data, params=params)
		prepped = self.requests_session.prepare_request(request)

		r = self.requests_session.send(prepped)
		if r.status_code == 401:
			self.refresh_token()
			# prepare again to use new auth-header
			prepped = self.requests_session.prepare_request(request)
			r = self.requests_session.send(prepped)

		# at this point we tried to re-auth, so anything but 200/OK, 201/Created or 204/no content is unexpected
		# yes: the exact documentation does not mention 204; returned on PUT anyways
		if r.status_code not in (200, 201, 204):
			raise ExactException(r.text)

		# don't try to decode json if we got nothing back
		if r.status_code == 204:
			return None
		return r.json()

	def get(self, resource, filter_string=None, select=None):
		params = {
			"$top": 2,
			"$select": select,
			"$filter": filter_string,
			"$inlinecount": "allpages"  # this forces a returned dict (otherwise we might get a list with one entry)
		}
		r = self._send("GET", resource, params=params)

		data = r["d"]["results"]
		if len(data) == 0:
			raise DoesNotExist("recource not found. params were: %r" % params)
		if len(data) > 1:
			raise MultipleObjectsReturned("api returned multiple objects. params were: %r" % params)
		return data[0]

	def filter(self, resource, filter_string=None, select=None, order_by=None, limit=None):
		params = {
			"$filter": filter_string,
			"$select": select,
			"$orderby": order_by,
			"$top": limit,
			"$inlinecount": "allpages"
		}
		response = self._send("GET", resource, params=params)
		results = response["d"]["results"]
		for r in results:
			yield r

		next_url = response["d"].get("__next")
		while next_url:
			request = Request("GET", next_url)
			prepped = self.requests_session.prepare_request(request)
			response = self.requests_session.send(prepped).json()
			next_url = response["d"].get("__next")
			results = response["d"]["results"]
			for r in results:
				yield r

	def create(self, resource, data):
		# TODO: add possibility to use a more advanced json encoder
		r = self._send("POST", resource, data=json.dumps(data))
		return r["d"]

	def update(self, resource, guid, data):
		# TODO: add possibility to use a more advanced json encoder
		resource = "%s(guid'%s')" % (resource, guid)
		r = self._send("PUT", resource, data=json.dumps(data))
		return r

	def delete(self, resource, guid):
		resource = "%s(guid'%s')" % (resource, guid)
		r = self._send("DELETE", resource)
		return r


# legacy
class ExactApi(OriginalExactApi):
	def __init__(self, **kwargs):
		from exact.storage import DjangoStorage
		storage = DjangoStorage()
		kwargs["storage"] = storage
		super(ExactApi, self).__init__(**kwargs)

