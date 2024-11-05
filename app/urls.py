from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from accounts.views.account import LoginPage, LogoutPage, SignupPage, MagicAccessPage
from app.views import TermsPage, PrivacyPage, IndexPage, ThanksPage, HowItWorksPage, FAQPage
from contact_messages.views import ContactPage
from payments.views import PaymentPage

admin.site.site_title = "PixSpeed.com"
urlpatterns = [
    path("batcave/", admin.site.urls),
    path("favicon.ico", RedirectView.as_view(url="/static/favicon.png")),
    path("captcha/", include("captcha.urls")),
    path("", IndexPage.as_view(), name="index"),
    path("api/", include("apis.url")),
    path("thanks/", ThanksPage.as_view(), name="thanks"),
    path("account/", include("accounts.urls.account")),
    path("login/", LoginPage.as_view(), name="login"),
    path("signup/", SignupPage.as_view(), name="signup"),
    path("logout/", LogoutPage.as_view(), name="logout"),
    path("magic-access/", MagicAccessPage.as_view()),
    path("contact/", ContactPage.as_view(), name="contact"),
    path("terms/", TermsPage.as_view(), name="terms"),
    path("privacy/", PrivacyPage.as_view(), name="privacy"),
    path("how-it-works/", HowItWorksPage.as_view(), name="how-it-works"),
    path("frequently-asked-questions/", FAQPage.as_view(), name="faq"),
    path("checkout/", PaymentPage.as_view(), name="checkout"),
]
