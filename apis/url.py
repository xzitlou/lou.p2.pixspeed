from django.urls import path

from apis.views import WebExtractorAPIPage, OptimizerAPIPage

urlpatterns = [
    path("web/", WebExtractorAPIPage.as_view(), name="web-extractor"),
    path("optimizer/", OptimizerAPIPage.as_view(), name="url-optimizer"),
]
