from django.urls import include, path

urlpatterns = [
	path("exact/", include(("exact.urls", "exact"))),
]
