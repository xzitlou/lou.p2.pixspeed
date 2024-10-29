from django.contrib.auth.mixins import LoginRequiredMixin

from app.utils import Utils
from django.shortcuts import render
from django.views.generic import View

from commons.models.counter import Counter

from config import SCRIPT_VERSION, API_DOMAIN, RATE_LIMIT, DEBUG
from translations.models.language import Language
from translations.models.translation import Translation


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
            "total_images": Utils.get_from_cache("total_images_optimized"),
            "debug": DEBUG
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


class HowItWorksPage(View):
    @staticmethod
    def get(request):
        settings = GlobalVars.get_globals(request)
        response = render(
            request,
            "views/how-it-works.html",
            {
                "title": f"{settings.get('i18n').get('how_it_works')} - PixSpeed.com",
                "description": settings.get("i18n").get("how_it_works_title_meta_description"),
                "page": "privacy",
                "g": settings
            }
        )

        return response
