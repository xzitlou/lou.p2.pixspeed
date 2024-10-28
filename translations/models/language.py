from django.db import models

from app.utils import Utils
from config import APP_VERSION, TRANSLATION_VERSION


class Language(models.Model):
    name = models.CharField(max_length=250)
    en_label = models.CharField(max_length=250)
    iso = models.CharField(max_length=5, unique=True)

    def __str__(self):
        return self.name

    @staticmethod
    def get_all(iso: str = None):
        key = f"languages__{TRANSLATION_VERSION}"
        data = Utils.get_from_cache(key)

        if not data:
            data = Language.objects.all().order_by("en_label")
            Utils.set_to_cache(key, data)

        language_iso, language_en = None, None

        for language in data:
            if language.iso == "en":
                language_en = language
            if language.iso == iso:
                language_iso = language
                break

        if not language_iso:
            language_iso = language_en

        return data, language_iso
