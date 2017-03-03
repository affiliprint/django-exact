# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from django.contrib.sites.models import Site
from django.db import models
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from exactonline.resource import PUT, POST, DELETE

logger = logging.getLogger("exact")


class Session(models.Model):
	base_url = models.URLField(_("OAuth2 redirect URL"))
	client_id = models.CharField(max_length=255)
	client_secret = models.CharField(max_length=255)

	auth_url = models.URLField(_("OAuth2 auth URL"))
	token_url = models.URLField(_("OAuth2 token URL"))
	rest_url = models.URLField(_("API base URL"))

	access_expiry = models.CharField(max_length=255, blank=True, default="")
	access_token = models.TextField(blank=True, default="")
	refresh_token = models.TextField(blank=True, default="")
	code = models.TextField(blank=True, default="")

	division = models.TextField()


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


@receiver(post_delete, sender=Webhook)
def delete_webhook(sender, instance, *args, **kwargs):
	if instance.guid:
		from .api import ExactApi
		api = ExactApi()
		logger.debug("deleting webhook %s: %s -> %s" % (instance.guid, instance.topic, instance.callback))
		api.restv1(DELETE("webhooks/WebhookSubscriptions(guid'%s')" % instance.guid))


@receiver(pre_save, sender=Webhook)
def create_or_update_webhook(sender, instance, raw, *args, **kwargs):
	if not raw:
		from .api import ExactApi
		api = ExactApi()
		if instance.pk or instance.guid:
			logger.debug("updating webhook %s: %s -> %s" % (instance.guid, instance.topic, instance.callback))
			api.restv1(PUT("webhooks/WebhookSubscriptions(guid'%s')" % instance.guid, {
				"Topic": instance.topic,
				"CallbackURL": instance.callback
			}))
		else:
			logger.debug("creating webhook: %s -> %s" % (instance.topic, instance.callback))
			webhook = api.restv1(POST("webhooks/WebhookSubscriptions", {
				"Topic": instance.topic,
				"CallbackURL": instance.callback
			}))
			instance.guid = webhook["ID"]

