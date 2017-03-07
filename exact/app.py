from django.apps import AppConfig
from django.utils.translation import ugettext_lazy


class Config(AppConfig):
	name = "exact"
	verbose_name = ugettext_lazy(u"Exact Online")

	def ready(self):
		import exact.signals
