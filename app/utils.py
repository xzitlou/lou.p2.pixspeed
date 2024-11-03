import uuid
from random import randint

import requests
from django.core.cache import cache
from django.db import connection
from django.template.loader import get_template

from config import MAILGUN_KEYS


class Utils:
    @staticmethod
    def get_ip(request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("HTTP_X_REAL_IP")

            if not ip:
                ip = request.META.get("REMOTE_ADDR")

        return ip

    @staticmethod
    def get_positive_integer(value, default=1):
        try:
            value = int(value)
            return max(value, default) if value >= default else default
        except (TypeError, ValueError):
            return default

    @staticmethod
    def print_connections(label: str = "____"):
        print(f"Queries: {label} => {len(connection.queries)}")

    @staticmethod
    def generate_verification_code():
        return "".join(["%s" % randint(0, 9) for _ in range(0, 6)])

    @staticmethod
    def send_email(
            sender="PixSpeed.com <no-reply@pixspeed.com>",
            recipients=None,
            subject=None,
            template=None,
            data=None
    ):
        template = get_template(f"mailing/{template}.html")
        html_content = template.render(data)

        return requests.post(
            f"https://api.mailgun.net/v3/{MAILGUN_KEYS.get('domain')}/messages",
            auth=("api", MAILGUN_KEYS.get("pk")),
            data={
                "from": sender,
                "to": recipients,
                "subject": subject,
                "html": html_content
            })

    @staticmethod
    def get_language(request):
        lang = request.GET.get("lang")

        if lang:
            data = lang.split("-")
            lang = data[0]
        if not lang:
            lang = request.session.get("lang")
        if not lang:
            http_accept_language = request.META.get("HTTP_ACCEPT_LANGUAGE")
            if http_accept_language:
                lang = http_accept_language.split("-")[0]
        if not lang:
            lang = "en"

        return lang

    @staticmethod
    def generate_hex_uuid():
        return uuid.uuid4().hex

    @staticmethod
    def generate_uuid():
        return str(uuid.uuid4())

    @staticmethod
    def clear_cache():
        cache.clear()

    @staticmethod
    def get_expire_info_cache(key):
        return cache.ttl(key)

    @staticmethod
    def get_from_cache(key):
        return cache.get(key, 0)

    @staticmethod
    def set_to_cache(key, value, exp=60 * 60 * 24 * 30):
        cache.set(key, value, timeout=exp)
