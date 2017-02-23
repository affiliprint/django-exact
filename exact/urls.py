# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls import url

from .views import Authenticate, Status

urlpatterns = [
	url(r'^authenticate$', Authenticate.as_view(), name="authenticate"),
	url(r'^status', Status.as_view(), name="status")
]
