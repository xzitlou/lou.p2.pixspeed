import os

import requests
from bs4 import BeautifulSoup
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views import View

from app.utils import Utils
from app.views import GlobalVars
from commons.models.website_scrape import WebsiteScrape


class WebExtractorAPIPage(View):
    @staticmethod
    def post(request, *args, **kwargs):
        settings = GlobalVars.get_globals(request)
        website_url = request.POST.get("website", "").strip()

        # Validar la URL
        validator = URLValidator()
        try:
            validator(website_url)
        except ValidationError:
            return JsonResponse({
                "error": settings.get("i18n").get("invalid_url")
            }, status=400)

        WebsiteScrape.objects.create(url=website_url)

        # Realizar una solicitud a la URL para extraer imágenes
        try:
            response = requests.get(website_url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.115 Safari/537.36"
            })
            response.raise_for_status()
        except Exception as e:
            print(str(e))
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