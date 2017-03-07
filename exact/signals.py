# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from exact.api import Exact
from exact.models import Webhook


logger = logging.getLogger("exact")


@receiver(post_delete, sender=Webhook)
def delete_webhook(sender, instance, *args, **kwargs):
	if instance.guid:
		api = Exact()
		logger.debug("deleting webhook %s: %s -> %s" % (instance.guid, instance.topic, instance.callback))
		api.delete("webhooks/WebhookSubscriptions", instance.guid)


@receiver(pre_save, sender=Webhook)
def create_or_update_webhook(sender, instance, raw, *args, **kwargs):
	if not raw:
		api = Exact()
		if instance.pk or instance.guid:
			logger.debug("updating webhook %s: %s -> %s" % (instance.guid, instance.topic, instance.callback))
			api.update("webhooks/WebhookSubscriptions", instance.guid, {
				"Topic": instance.topic,
				"CallbackURL": instance.callback
			})
		else:
			logger.debug("creating webhook: %s -> %s" % (instance.topic, instance.callback))
			webhook = api.create("webhooks/WebhookSubscriptions", {
				"Topic": instance.topic,
				"CallbackURL": instance.callback
			})
			instance.guid = webhook["ID"]
