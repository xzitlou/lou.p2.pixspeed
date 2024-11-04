from django.urls import path

from apis.views import WebExtractorAPI, OptimizerAPI, TokenVerificationAPI, RestoreCreditAPI, SuccessOptimizationAPI, APIDocumentationPage

urlpatterns = [
    path("documentation/", APIDocumentationPage.as_view(), name="api-documentation-page"),
    path("web/", WebExtractorAPI.as_view(), name="web-extractor"),
    path("optimizer/", OptimizerAPI.as_view(), name="url-optimizer"),
    path("token-verification/", TokenVerificationAPI.as_view()),
    path("restore-credit/", RestoreCreditAPI.as_view()),
    path("success-optimization/", SuccessOptimizationAPI.as_view()),
]
