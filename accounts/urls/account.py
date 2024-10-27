from django.urls import path, include

from accounts.views.account import *

urlpatterns = [
    path("", AccountPage.as_view(), name="account"),
    path("cancel-subscription/", AccountCancelSubscriptionPage.as_view(), name="account-cancel-subscription"),
    path("security/", AccountSecurityPage.as_view(), name="account-security"),
    path("conversions/", AccountConversionsPage.as_view(), name="account-conversions"),
    path("billing/", AccountBillingPage.as_view(), name="account-billing"),
    path("api/", include("accounts.urls.api")),
]
