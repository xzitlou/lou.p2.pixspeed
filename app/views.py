import os

import requests
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.http import JsonResponse
from django.template.loader import render_to_string

from app.utils import Utils
from django.shortcuts import render
from django.views.generic import View

from commons.models.counter import Counter
from config import SCRIPT_VERSION, API_DOMAIN, RATE_LIMIT, DEBUG
from translations.models.language import Language
from translations.models.translation import Translation

from bs4 import BeautifulSoup


class GlobalVars:
    @staticmethod
    def get_globals(request):
        if DEBUG:
            Utils.clear_cache()

        lang_iso = Utils.get_language(request)
        languages, lang = Language.get_all(lang_iso)
        request.session["lang"] = lang.iso
        context = {
            "lang": lang,
            "i18n": Translation.get_text_by_lang(lang.iso),
            "languages": languages,
            "scripts_version": SCRIPT_VERSION,
            "api_domain": API_DOMAIN,
            "conversions": "{:,}".format(Counter.get_counter("conversion")),
            "rate_limit": RATE_LIMIT
        }
        Utils.print_connections()
        return context


class IndexPage(View):
    @staticmethod
    def get(request):
        settings = GlobalVars.get_globals(request)
        response = render(
            request,
            "views/home.html",
            {
                "page": "home",
                "title": f"PixSpeed: Image Optimization for Faster, SEO-Friendly Websites | PixSpeed.com",
                "description": "Optimize your images with PixSpeed to boost your website's loading speed and SEO performance. Compress JPEG, PNG, and WebP images without compromising quality for a faster, more user-friendly experience.",
                "g": settings,
            }
        )

        return response


class ThanksPage(LoginRequiredMixin, View):
    login_url = "login"

    @staticmethod
    def get(request):
        settings = GlobalVars.get_globals(request)
        response = render(
            request,
            "views/thanks.html",
            {
                "page": "thanks",
                "title": f"{settings.get('i18n').get('thanks_title')} | PixSpeed.com",
                "description": settings.get('i18n').get('thanks_meta'),
                "g": settings,
            }
        )

        return response


class WebExtractorAPIPage(View):
    def post(self, request, *args, **kwargs):
        website_url = request.POST.get("website")

        # Validar la URL
        validator = URLValidator()
        try:
            validator(website_url)
        except ValidationError:
            return JsonResponse({"error": "Invalid URL"}, status=400)

        # Realizar una solicitud a la URL para extraer imágenes
        try:
            response = requests.get(website_url)
            response.raise_for_status()
        except requests.RequestException:
            return JsonResponse({"error": "Failed to fetch the webpage"}, status=500)

        # Extraer las URLs de las imágenes usando BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        img_urls = [img["src"] for img in soup.find_all("img") if img.get("src")]

        # Convertir URLs relativas a absolutas
        images = []
        for img_url in img_urls:
            absolute_url = requests.compat.urljoin(website_url, img_url)
            filename = os.path.basename(absolute_url)
            images.append({"filename": filename, "url": absolute_url})

        html_content = render_to_string(
            "components/images.website.html",
            {
                "images": images
            }
        )

        return JsonResponse({"html": html_content})


class TermsPage(View):
    @staticmethod
    def get(request):
        settings = GlobalVars.get_globals(request)
        response = render(
            request,
            "views/terms.html",
            {
                "title": f"{settings.get('i18n').get('terms_title')} - PixSpeed.com",
                "description": settings.get("i18n").get("terms_meta"),
                "page": "terms",
                "g": settings
            }
        )

        return response


class PrivacyPage(View):
    @staticmethod
    def get(request):
        settings = GlobalVars.get_globals(request)
        response = render(
            request,
            "views/privacy.html",
            {
                "title": f"{settings.get('i18n').get('privacy_title')} - PixSpeed.com",
                "description": settings.get("i18n").get("privacy_meta"),
                "page": "privacy",
                "g": settings
            }
        )

        return response
