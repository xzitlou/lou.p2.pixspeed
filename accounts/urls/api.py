from django.urls import path

from accounts.views.api import *

urlpatterns = [
    path("rate_limit/", RateLimitAPI.as_view(), name="rate-limit"),
    path("resend-verification/", ResendVerificationEmailAPI.as_view(), name="resend-verification"),
]
