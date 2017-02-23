# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from exactonline.api import ExactApi as OriginalExactApi

from exact.storage import DjangoStorage


class ExactApi(OriginalExactApi):
	def __init__(self, **kwargs):
		storage = DjangoStorage()
		kwargs["storage"] = storage
		super(ExactApi, self).__init__(**kwargs)

