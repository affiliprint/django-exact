import json
from unittest import mock

from requests import ConnectionError, Response

from django.test import TestCase

from exact.api import Exact, ExactAuthException, ExactException, ExactUnavailable
from exact.models import Session


def make_response(status, body=""):
	response = Response()
	response.status_code = status
	response._content = (body if isinstance(body, str) else json.dumps(body)).encode("utf-8")
	return response


TOKEN_OK = {"access_token": "new-access", "refresh_token": "new-refresh", "expires_in": "600"}
RESULT = {"d": {"results": [{"ID": 1}]}}


class ExactTest(TestCase):
	def setUp(self):
		Session.objects.create(
			api_url="https://exact.test/api",
			client_id="client-id",
			client_secret="client-secret",
			redirect_uri="https://example.com/exact/authenticate",
			access_token="old-access",
			refresh_token="old-refresh",
		)
		self.api = Exact()

	def mock_send(self, *responses):
		patcher = mock.patch("exact.api.ReqSession.send", side_effect=responses)
		patcher.start()
		self.addCleanup(patcher.stop)

	def test_refresh_on_401(self):
		self.mock_send(make_response(401), make_response(200, TOKEN_OK), make_response(200, RESULT))
		self.assertEqual(self.api.get("crm/Accounts"), {"ID": 1})
		session = Session.objects.get()
		self.assertEqual((session.access_token, session.refresh_token), ("new-access", "new-refresh"))

	def test_5xx_is_unavailable(self):
		self.mock_send(make_response(503, "<html>maintenance</html>"))
		with self.assertRaises(ExactUnavailable) as cm:
			self.api.get("crm/Accounts")
		self.assertIsNone(cm.exception.error_message)

	def test_html_with_200_is_unavailable(self):
		self.mock_send(make_response(200, "<html>maintenance</html>"))
		with self.assertRaises(ExactUnavailable):
			self.api.get("crm/Accounts")

	def test_error_message(self):
		error = {"error": {"code": "", "message": {"lang": "", "value": "VAT\r\ninvalid"}}}
		self.mock_send(make_response(400, error))
		with self.assertRaises(ExactException) as cm:
			self.api.create("crm/Accounts", {})
		self.assertNotIsInstance(cm.exception, ExactUnavailable)
		self.assertEqual(cm.exception.error_message, "VAT\ninvalid")

	def test_rejected_refresh_token(self):
		error = {"error": "invalid_grant", "error_description": "Refresh token is invalid."}
		self.mock_send(make_response(401), make_response(400, error))
		with self.assertRaises(ExactAuthException) as cm:
			self.api.get("crm/Accounts")
		self.assertEqual(cm.exception.error_message, "Refresh token is invalid.")

	def test_refresh_network_error(self):
		self.mock_send(make_response(401), ConnectionError("reset"))
		with self.assertLogs("exact", "ERROR"), self.assertRaises(ExactException) as cm:
			self.api.get("crm/Accounts")
		self.assertIsNone(cm.exception.response)
		self.assertIsInstance(cm.exception.__cause__, ConnectionError)
		self.assertFalse(cm.exception.limits_reached)
		self.assertIsNone(cm.exception.error_message)
