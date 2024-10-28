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
            "rate_limit": RATE_LIMIT,
            "total_images": Utils.get_from_cache("total_images_optimized")
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
                "title": f"{settings.get('i18n').get('home_title')} | PixSpeed.com",
                "description": settings.get("i18n").get("home_meta_description"),
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
    @staticmethod
    def post(request, *args, **kwargs):
        settings = GlobalVars.get_globals(request)
        website_url = request.POST.get("website")

        # Validar la URL
        validator = URLValidator()
        try:
            validator(website_url)
        except ValidationError:
            return JsonResponse({
                "error": settings.get("i18n").get("invalid_url")
            }, status=400)

        # Realizar una solicitud a la URL para extraer imágenes
        try:
            response = requests.get(website_url)
            response.raise_for_status()
        except requests.RequestException:
            return JsonResponse({
                "error": settings.get("i18n").get("failed_fetch_webpage")
            }, status=500)

        # Extraer las URLs de las imágenes usando BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        img_urls = [img["src"] for img in soup.find_all("img") if img.get("src")]

        # Convertir URLs relativas a absolutas
        images = []
        for img_url in img_urls:
            if ".webp" in img_url or ".jpg" in img_url or ".jpeg" in img_url or ".png" in img_url:
                img_url = img_url.split("?")[0]
                absolute_url = requests.compat.urljoin(website_url, img_url)
                filename = os.path.basename(absolute_url)
                images.append({
                    "filename": filename,
                    "url": absolute_url
                })

        html_content = render_to_string(
            "components/images.website.html",
            {
                "images": images,
                "g": settings,
            }
        )

        return JsonResponse({"html": html_content})


class ImageCounterAPI(View):
    @staticmethod
    def post(request, *args, **kwargs):
        # Obtener el contador actual o iniciar en 0 si no existe
        total_images = Utils.get_from_cache('total_images_optimized')

        # Incrementar el contador
        total_images += 1
        Utils.set_to_cache('total_images_optimized', total_images)

        return JsonResponse({"total_images_optimized": total_images})


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
