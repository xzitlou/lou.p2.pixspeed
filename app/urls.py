from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from accounts.views.account import LoginPage, LostPasswordPage, RestorePasswordPage, LogoutPage, VerificationPage, SignupPage
from app.views import TermsPage, PrivacyPage, IndexPage, ThanksPage, WebExtractorAPIPage, ImageCounterAPI
from contact_messages.views import ContactPage

admin.site.site_title = "TL;DR AI"
urlpatterns = [
    path("batcave/", admin.site.urls),
    path("favicon.ico", RedirectView.as_view(url="/static/favicon.png")),
    path("captcha/", include("captcha.urls")),
    path("", IndexPage.as_view(), name="index"),
    path("api/web/", WebExtractorAPIPage.as_view(), name="web-extractor"),
    path("api/counter/", ImageCounterAPI.as_view(), name="api-counter"),
    path("thanks/", ThanksPage.as_view(), name="thanks"),
    path("account/", include("accounts.urls.account")),
    path("login/", LoginPage.as_view(), name="login"),
    path("signup/", SignupPage.as_view(), name="signup"),
    path("verification/", VerificationPage.as_view(), name="verification"),
    path("logout/", LogoutPage.as_view(), name="logout"),
    path("lost-password/", LostPasswordPage.as_view(), name="lost-password"),
    path("restore-password/", RestorePasswordPage.as_view(), name="restore-password"),
    path("contact/", ContactPage.as_view(), name="contact"),
    path("terms/", TermsPage.as_view(), name="terms"),
    path("privacy/", PrivacyPage.as_view(), name="privacy"),
]
