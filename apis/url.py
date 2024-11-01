from django.urls import path

from apis.views import WebExtractorAPIPage, ImageCounterAPI, FailedConversionAPI

urlpatterns = [
    path("web/", WebExtractorAPIPage.as_view(), name="web-extractor"),
    path("counter/", ImageCounterAPI.as_view(), name="api-counter"),
    path("failed-conversion/", FailedConversionAPI.as_view(), name="failed-conversion-api"),
]
