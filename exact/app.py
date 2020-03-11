from django.apps import AppConfig
from django.utils.translation import gettext_lazy


class Config(AppConfig):
	name = "exact"
	verbose_name = gettext_lazy("Exact Online")

	def ready(self):
		import exact.signals
