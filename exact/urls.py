# -*- coding: utf-8 -*-
from django.urls import path

from .views import Authenticate, Status, webhook

urlpatterns = [
	path('authenticate', Authenticate.as_view(), name="authenticate"),
	path('status', Status.as_view(), name="status"),
	path('webhook', webhook, name="webhook"),
]
