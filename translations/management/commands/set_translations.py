import json

from django.core.management import BaseCommand

from translations.models.translation import Translation


class Command(BaseCommand):
    help = 'set_translations'

    def handle(self, *args, **options):
        for lang in ["en", "es", "pt"]:
            with open(f'./translations/json/textbase_data_{lang}.json') as translation_json:
                translations = json.load(translation_json)

            for translation in translations:
                Translation.objects.update_or_create(
                    code_name=translation['code_name'],
                    language=lang,
                    defaults={
                        "text": translation['text'],
                    }
                )
