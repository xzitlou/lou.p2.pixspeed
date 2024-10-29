import os

from google.cloud import translate_v2 as translate
from django.core.management.base import BaseCommand

from app.settings import BASE_DIR
from translations.models.language import Language
from translations.models.textbase import TextBase
from translations.models.translation import Translation


class Command(BaseCommand):
    help = 'start_translation'

    def handle(self, *args, **options):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(BASE_DIR / 'gcreds.json')
        translate_client = translate.Client()
        text_base_list = TextBase.objects.filter(
            translated=False
        )

        for language in Language.objects.all():
            for text_base in text_base_list:
                if language.iso != "en":
                    translation = translate_client.translate(
                        text_base.text,
                        target_language=language.iso,
                        source_language='en'
                    )
                    text = translation.get('translatedText', text_base.text)
                else:
                    text = text_base.text

                print(f"{language.iso}: {text}")

                Translation.objects.update_or_create(
                    code_name=text_base.code_name,
                    language=language.iso,
                    defaults={
                        "text": text,
                    }
                )

                text_base.translated = True
                text_base.save()
