from django.urls import path

from accounts.views.account import *

urlpatterns = [
    path("", AccountPage.as_view(), name="account"),
    path("billing/", AccountBillingPage.as_view(), name="account-billing"),
    path('delete-account/', AccountDeletePage.as_view(), name='delete-account'),
]
