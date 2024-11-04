from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from accounts.models import CustomUser
from app.utils import Utils
from app.views import GlobalVars


class LoginPage(View):
    errors = None
    settings = None

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("account")

        self.settings = GlobalVars.get_globals(request)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        response = render(
            request,
            "views/login.html",
            {
                "page": "login",
                "title": f"{self.settings.get('i18n').get('login_title')} - PixSpeed.com",
                "description": self.settings.get("i18n").get("login_meta_description"),
                "g": self.settings,
                "data": request.GET,
                "errors": self.errors,
            }
        )

        return response

    def post(self, request):
        account, errors = CustomUser.login_user(
            email=request.POST.get("email"),
            i18n=self.settings.get("i18n")
        )

        if errors:
            self.errors = errors
            return self.get(request)

        Utils.send_email(
            recipients=[account.email],
            subject=self.settings.get("i18n").get("subject_verification"),
            template="login.html",
            data={
                "user": account,
                "g": self.settings
            }
        )
        return redirect(reverse("login") + "?success=1")


class SignupPage(View):
    errors = None
    settings = None
    data = None

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("account")

        self.settings = GlobalVars.get_globals(request)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        response = render(
            request,
            "views/register.html",
            {
                "page": "register",
                "title": f"{self.settings.get('i18n').get('register')} - PixSpeed.com",
                "description": self.settings.get("i18n").get("signup_meta_description"),
                "g": self.settings,
                "errors": self.errors,
                "data": self.data or request.GET
            }
        )

        return response

    def post(self, request):
        data = request.POST
        account, errors = CustomUser.register_user(
            full_name=data.get("full_name"),
            email=data.get("email"),
            i18n=self.settings.get("i18n"),
            lang=self.settings.get("lang").iso,
        )

        if errors:
            self.errors = errors
            self.data = data
            return self.get(request)

        Utils.send_email(
            recipients=[account.email],
            subject=self.settings.get("i18n").get("subject_verification"),
            template="login.html",
            data={
                "user": account,
                "g": self.settings
            }
        )
        return redirect(reverse("signup") + "?success=1")


class LogoutPage(LoginRequiredMixin, View):
    login_url = "login"

    @staticmethod
    def get(request):
        logout(request)
        return redirect("index")


class MagicAccessPage(View):
    @staticmethod
    def get(request, *args, **kwargs):
        try:
            account = CustomUser.objects.get(
                verification_code=request.GET.get("token")
            )
        except Exception as e:
            print(str(e))
            return redirect("login")

        account.is_confirm = True
        account.save()
        login(request, account)
        return redirect("index")


class AccountPage(LoginRequiredMixin, View):
    login_url = "login"

    def get(self, request):
        settings = GlobalVars.get_globals(request)
        response = render(
            request,
            "views/account.html",
            {
                "page": "account",
                "title": f"{settings.get('i18n').get('account_title')} - PixSpeed.com",
                "description": "",
                "g": settings,
                "reasons": [item for k, item in settings.get("i18n").items() if "cancellation_reason_" in k]
            }
        )
        return response


class AccountSecurityPage(LoginRequiredMixin, View):
    login_url = "login"
    errors = None
    settings = None

    def dispatch(self, request, *args, **kwargs):
        self.settings = GlobalVars.get_globals(request)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        response = render(
            request,
            "views/account.security.html",
            {
                "page": "account",
                "title": f"Security - PixSpeed.com",
                "description": "",
                "g": self.settings,
                "errors": self.errors,
                "data": request.GET,
            }
        )
        return response

    def post(self, request):
        account, errors = request.user.update_password(
            data=request.POST,
            i18n=self.settings.get("i18n")
        )

        if errors:
            self.errors = errors
            return self.get(request)

        update_session_auth_hash(request, account)
        return redirect(reverse("account-security") + "?status=1")


class AccountCancelSubscriptionPage(LoginRequiredMixin, View):
    login_url = "login"
    errors = None
    settings = None

    def dispatch(self, request, *args, **kwargs):
        self.settings = GlobalVars.get_globals(request)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        response = render(
            request,
            "views/account.cancel-subscription.html",
            {
                "page": "account",
                "title": f"Cancel subscription - PixSpeed.com",
                "description": "",
                "g": self.settings,
                "errors": self.errors,
                "data": request.GET,
            }
        )
        Utils.print_connections()

        return response

    def post(self, request):
        data = request.POST
        errors = request.user.cancel_subscription(
            reasons=data.get("reasons", []),
            cancellation_type="subscription"
        )

        if errors:
            self.errors = errors
            return self.get(request)

        return redirect(reverse("account-cancel-subscription") + "?status=1")


class AccountConversionsPage(LoginRequiredMixin, View):
    login_url = "login"

    def get(self, request):
        settings = GlobalVars.get_globals(request)
        response = render(
            request,
            "views/account.conversions.html",
            {
                "page": "account",
                "title": f"Conversions - PixSpeed.com",
                "description": "",
                "g": settings,
            }
        )
        return response


class AccountBillingPage(LoginRequiredMixin, View):
    login_url = "login"

    def get(self, request):
        settings = GlobalVars.get_globals(request)
        response = render(
            request,
            "views/account.billing.html",
            {
                "page": "account",
                "title": f"Billing - PixSpeed.com",
                "description": "",
                "g": settings,
                "payments": request.user.get_payments(page=request.GET.get("page")),
            }
        )
        return response
