from django.urls import path

from apis.views import WebExtractorAPIPage, ImageCounterAPI

urlpatterns = [
    path("web/", WebExtractorAPIPage.as_view(), name="web-extractor"),
    path("counter/", ImageCounterAPI.as_view(), name="api-counter"),
]
