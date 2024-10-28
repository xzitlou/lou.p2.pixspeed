from django.db import models

from app.utils import Utils
from config import APP_VERSION, TRANSLATION_VERSION


class Translation(models.Model):
    code_name = models.CharField(max_length=250)
    language = models.CharField(max_length=10)
    text = models.TextField()

    class Meta:
        unique_together = ('language', 'code_name', )

    def __str__(self):
        return self.code_name

    @staticmethod
    def get_text_by_lang(lang: str = None):
        key = f"i18n__{TRANSLATION_VERSION}"
        data = Utils.get_from_cache(key)

        if not data:
            data = {}

            for translation in Translation.objects.all():
                if not data.get(translation.language):
                    data[translation.language] = {}

                data[translation.language][translation.code_name] = translation.text

            Utils.set_to_cache(key, data)

        return data.get(lang, {}) or data.get("en", {})

    @staticmethod
    def register_text_translated(data):
        language = data.get('language')
        code_name = data.get('code_name')
        text = data.get('text')

        try:
            translation = Translation.objects.get(code_name=code_name, language=language)
        except:
            translation = Translation(
                code_name=code_name,
                language=language
            )

        translation.text = text
        translation.save()

        return translation, None
