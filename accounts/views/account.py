from django.contrib.auth import login, logout
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


class AccountDeletePage(LoginRequiredMixin, View):
    login_url = "login"

    @staticmethod
    def get(request):
        settings = GlobalVars.get_globals(request)
        response = render(
            request,
            "views/account.delete.html",
            {
                "page": "account",
                "title": f"%s | Yout.com" % settings.get("i18n").get("delete_account"),
                "description": settings.get("i18n").get("delete_account"),
                "g": settings,
            }
        )
        Utils.print_connections()

        return response

    @staticmethod
    def post(request, *args, **kwargs):
        Utils.send_email(
            recipients=[request.user.email],
            subject="Your account at PixSpeed.com has been successfully deleted",
            template="account.deleted.html",
            data={
                "user": request.user
            }
        )
        request.user.delete()

        return redirect("index")


class RegenerateTokenPage(LoginRequiredMixin, View):
    login_url = "login"

    @staticmethod
    def post(request, *args, **kwargs):
        request.user.api_token = Utils.generate_hex_uuid()
        request.user.save()

        return redirect("account")
