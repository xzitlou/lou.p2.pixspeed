from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from app.views import GlobalVars
from contact_messages.forms import CaptchaForm
from contact_messages.models import Message


class ContactPage(View):
    errors = None
    settings = None

    def dispatch(self, request, *args, **kwargs):
        self.settings = GlobalVars.get_globals(request)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = CaptchaForm()
        response = render(
            request,
            "views/contact.html",
            {
                "title": f"{self.settings.get('i18n').get('contact_title')} - PixSpeed.com",
                "description": self.settings.get("i18n").get("contact_meta"),
                "page": "contact",
                "g": self.settings,
                "form": form,
                "data": request.GET,
                "errors": self.errors,
            }
        )

        return response

    def post(self, request):
        data = request.POST
        form = CaptchaForm(data)
        errors = None

        if not form.is_valid():
            errors = [self.settings.get("i18n").get("captcha_error")]
        if not errors:
            errors = Message.save_message(
                data=data,
                i18n=self.settings.get("i18n")
            )
            if not errors:
                return redirect(reverse("contact") + "?status=1")

        self.errors = errors
        return self.get(request)
