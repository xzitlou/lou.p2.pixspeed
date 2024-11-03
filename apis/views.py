import os
import re

import bugsnag
import requests
from bs4 import BeautifulSoup
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from django.core.validators import URLValidator
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views import View
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait

from accounts.models import CustomUser
from app.utils import Utils
from app.views import GlobalVars
from commons.models.image_url_history import ImageUrlHistory
from commons.models.website_scrape import WebsiteScrape
from config import IMG_EXTENSIONS, API_DOMAIN, MAIN_KEY


class WebExtractorAPI(View):
    @staticmethod
    def post(request, *args, **kwargs):
        settings = GlobalVars.get_globals(request)
        website_url = request.POST.get("website", "").strip().lower()
        web_scrape = WebsiteScrape.objects.create(url=website_url)

        # Validar la URL
        validator = URLValidator()
        try:
            validator(website_url)
        except Exception as e:
            bugsnag.notify(Exception(f'WebExtractorAPIPage [invalid_url]: {str(e)}'))
            web_scrape.status = WebsiteScrape.FAILED
            web_scrape.save()
            return JsonResponse({
                "error": settings.get("i18n").get("invalid_url")
            }, status=400)

        # Determinar si la URL es una imagen
        if any(ext in website_url for ext in IMG_EXTENSIONS):
            img_url = website_url.split("?")[0]
            absolute_url = requests.compat.urljoin(website_url, img_url)
            filename = os.path.basename(absolute_url)
            images = [{
                "filename": filename,
                "url": absolute_url
            }]
            html_content = render_to_string(
                "components/images.website.html",
                {
                    "images": images,
                    "g": settings,
                    "extensions": [re.escape(ext[1:]) for ext in IMG_EXTENSIONS]
                }
            )

            web_scrape.status = WebsiteScrape.SUCCESS
            web_scrape.total_images_found = len(images)
            web_scrape.save()

            return JsonResponse({"html": html_content})

        ## Colocar aquí la lógica con selenium
        html_text = None
        driver = None

        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")  # Mejora el rendimiento en servidores
            options.add_argument("--no-sandbox")  # Evita problemas de permisos en entornos root
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--use-gl=desktop")

            driver = webdriver.Chrome(options=options)
            driver.set_page_load_timeout(15)  # Tiempo de espera de carga de página

            driver.get(website_url)

            # Espera hasta que el <body> esté cargado para asegurar el HTML básico
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            html_text = driver.page_source  # Obtiene el HTML actual de la página
        except TimeoutException as e:
            bugsnag.notify(Exception(f'WebExtractorAPIPage [selenium_fetch]: {str(e)}'))
            html_text = driver.page_source  # Obtener HTML disponible si hay timeout
        except Exception as e:
            bugsnag.notify(Exception(f'WebExtractorAPIPage [selenium_fetch]: {str(e)}'))
        finally:
            if driver:
                driver.quit()

        # Realizar una solicitud a la URL para extraer imágenes
        if html_text:
            # Extraer las URLs de las imágenes usando BeautifulSoup
            soup = BeautifulSoup(html_text, "html.parser")
            img_urls = [img["src"] for img in soup.find_all("img") if img.get("src")]

            # Convertir URLs relativas a absolutas
            images = []
            for img_url in img_urls:
                img_url = img_url.split("?")[0]

                # Convertir a URL absoluta utilizando siempre la URL base
                absolute_url = requests.compat.urljoin(website_url, img_url)

                # Filtrar extensiones deseadas
                if any(ext in absolute_url for ext in IMG_EXTENSIONS):
                    filename = os.path.basename(absolute_url)

                    # Agregar imagen solo si no es un duplicado
                    if absolute_url not in [image["url"] for image in images]:
                        images.append({
                            "filename": filename,
                            "url": absolute_url
                        })
        else:
            try:
                response = requests.get(website_url, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.115 Safari/537.36",
                    "Referer": website_url
                })
                response.raise_for_status()
                html_text = response.text
            except Exception as e:
                bugsnag.notify(Exception(f'WebExtractorAPIPage [fetch_webpage]: {str(e)}'))

                web_scrape.status = WebsiteScrape.FAILED
                web_scrape.save()

                return JsonResponse({
                    "error": f'{settings.get("i18n").get("failed_fetch_webpage")}'
                }, status=500)

            # Extraer las URLs de las imágenes usando BeautifulSoup
            soup = BeautifulSoup(html_text, "html.parser")
            img_urls = [img["src"] for img in soup.find_all("img") if img.get("src")]

            # Convertir URLs relativas a absolutas
            images = []
            for img_url in img_urls:
                img_url = img_url.split("?")[0]

                # Convertir a URL absoluta utilizando siempre la URL base
                absolute_url = requests.compat.urljoin(website_url, img_url)

                # Filtrar extensiones deseadas
                if any(ext in absolute_url for ext in IMG_EXTENSIONS):
                    filename = os.path.basename(absolute_url)

                    # Agregar imagen solo si no es un duplicado
                    if absolute_url not in [image["url"] for image in images]:
                        images.append({
                            "filename": filename,
                            "url": absolute_url
                        })

            # Buscar URLs de imágenes en el HTML como texto completo
            html_content = html_text  # Obtener HTML completo
            extensions_pattern = "|".join([re.escape(ext[1:]) for ext in IMG_EXTENSIONS])
            img_regex = rf'(https?://[^\s]+?\.({extensions_pattern})|\/\/[^\s]+?\.({extensions_pattern})|\/[^\s]+?\.({extensions_pattern})|\bimg\/[^\s]+?\.({extensions_pattern}))'
            text_img_urls = re.findall(img_regex, html_content)

            # Convertir URLs encontradas en el HTML como texto a absolutas
            for img_url in text_img_urls:
                if img_url.startswith("//"):
                    img_url = "https:" + img_url  # Agregar protocolo si falta
                # Asegurar que `website_url` termine en '/' si `img_url` es relativo y no comienza con '/'
                base_url = website_url if img_url.startswith('/') else website_url.rstrip('/') + '/'
                absolute_url = requests.compat.urljoin(base_url, img_url)

                if absolute_url not in [image["url"] for image in images]:  # Evitar duplicados
                    filename = os.path.basename(absolute_url)
                    images.append({
                        "filename": filename,
                        "url": absolute_url
                    })

        web_scrape.status = WebsiteScrape.SUCCESS
        web_scrape.total_images_found = len(images)
        web_scrape.save()

        html_content = render_to_string(
            "components/images.website.html",
            {
                "images": images,
                "g": settings,
                "extensions": [re.escape(ext[1:]) for ext in IMG_EXTENSIONS]
            }
        )

        return JsonResponse({"html": html_content})


class OptimizerAPI(View):
    @staticmethod
    def post(request, *args, **kwargs):
        api_url = f"{API_DOMAIN}/url"  # API de Go
        image_url = request.POST.get("url", "")
        format_requested = request.POST.get("format", "")
        response = requests.post(api_url, headers={
            "key": MAIN_KEY
        }, data={
            "url": image_url,
            "format": format_requested
        })

        if response.status_code != 200:
            print(response.json())
            ImageUrlHistory.objects.create(
                url=image_url,
                format=format_requested
            )
            return JsonResponse({"failed": True}, status=400)

        total_images = Utils.get_from_cache('total_images_optimized')
        total_images += 1
        Utils.set_to_cache('total_images_optimized', total_images)

        ImageUrlHistory.objects.create(
            url=image_url,
            was_success=True,
            format=format_requested
        )

        html_content = render_to_string(
            "components/image.optimization_summary.html",
            context={
                **response.json(),
            }
        )

        return JsonResponse({"html": html_content})


@method_decorator(csrf_exempt, name='dispatch')
class TokenVerificationAPI(View):
    @staticmethod
    @transaction.atomic
    def post(request, *args, **kwargs):
        try:
            user = CustomUser.objects.select_for_update().get(
                api_token=request.headers.get("key", None)
            )

            if user.image_credits <= 0:
                return JsonResponse({"error": "You need more credits"}, status=400)

            user.image_credits -= 1
            user.save()
            return JsonResponse({"status": True, "remaining_credits": user.image_credits})

        except Exception as e:
            print(str(e))
            return JsonResponse({"error": "Invalid API Key"}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class RestoreCreditAPI(View):
    @staticmethod
    @transaction.atomic
    def post(request, *args, **kwargs):
        try:
            user = CustomUser.objects.select_for_update().get(
                api_token=request.headers.get("key", None)
            )

            user.image_credits += 1
            user.save()
            return JsonResponse({"status": True, "remaining_credits": user.image_credits})

        except CustomUser.DoesNotExist:
            return JsonResponse({"error": "Invalid API Key"}, status=400)
