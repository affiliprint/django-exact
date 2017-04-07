# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.sites.models import Site
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class Session(models.Model):
	api_url = models.URLField(_("API base URL"), help_text=_("E.g https://start.exactonline.nl/api"))
	client_id = models.CharField(max_length=255, help_text=_("Your OAuth2/Exact App client ID"))
	client_secret = models.CharField(max_length=255, help_text=_("Your OAuth2/Exact App client secret"))
	redirect_uri = models.URLField(_("OAuth2 redirect URI"), help_text=_("Callback URL on your server. https://example.com/exact/authenticate"))
	division = models.IntegerField()

	access_expiry = models.IntegerField(blank=True, null=True)
	access_token = models.TextField(blank=True, null=True)
	refresh_token = models.TextField(blank=True, null=True)
	authorization_code = models.TextField(blank=True, null=True)


def _default_callback_url():
	return "https://%s%s" % (Site.objects.get_current().domain, reverse("exact:webhook"))


class Webhook(models.Model):
	TOPIC_CHOICES = (
		("Accounts", _("Accounts")),
		("BankAccounts", _("Bank Accounts")),
		("Contacts", _("Contacts")),
		("CostTransactions", _("CostTransactions")),
		("DocumentAttachments", _("Document Attachments")),
		("Documents", _("Documents")),
		("FinancialTransactions", _("FinancialTransactions")),
		("GoodsDeliveries", _("GoodsDeliveries")),
		("Items", _("Items")),
		("ProjectPlanning", _("ProjectPlanning")),
		("PurchaseOrders", _("PurchaseOrders")),
		("Quotations", _("Quotations")),
		("SalesInvoices", _("SalesInvoices")),
		("SalesOrders", _("SalesOrders")),
		("StockPositions", _("StockPositions")),
		("TimeTransactions", _("TimeTransactions")),
	)
	topic = models.CharField(choices=TOPIC_CHOICES, max_length=255, unique=True)
	callback = models.URLField(_("Callback"), help_text=_("Webhook callback"), default=_default_callback_url)

	# division = models.PositiveIntegerField(_("Division"), help_text=_("Company inside Exact Online."))
	guid = models.CharField(max_length=36, blank=True, null=True)
