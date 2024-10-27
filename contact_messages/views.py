from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from app.views import GlobalVars
from contact_messages.models import Message


class ContactPage(View):
    errors = []

    def get(self, request):
        settings = GlobalVars.get_globals(request)
        from contact_messages.forms import CaptchaForm
        form = CaptchaForm()
        response = render(
            request,
            "views/contact.html",
            {
                "title": f"{settings.get('i18n').get('contact_title')} - TLDRai.com",
                "description": settings.get("i18n").get("contact_meta"),
                "page": "contact",
                "g": settings,
                "form": form,
                "data": request.GET
            }
        )

        return response

    def post(self, request):
        settings = GlobalVars.get_globals(request)
        from contact_messages.forms import CaptchaForm
        data = request.POST
        form = CaptchaForm(data)
        errors = None

        if not form.is_valid():
            errors = [settings.get("i18n").get("captcha_error")]
        if not errors:
            _, errors = Message.save_message(data, settings)
            if not errors:
                return redirect(reverse("contact") + "?status=1")

        self.errors = errors
        return self.get(request)
