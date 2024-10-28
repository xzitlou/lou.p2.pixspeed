import json

from django.core.management import BaseCommand

from translations.models.language import Language
from translations.models.textbase import TextBase


class Command(BaseCommand):
    help = 'create_textbase_json'

    def handle(self, *args, **options):
        textbase_values = []

        for textbase in TextBase.objects.all():
            textbase_values.append({
                "code_name": textbase.code_name,
                "text": textbase.text,
            })

        with open("./translations/json/textbase_data_en.json", "w") as json_file:
            json.dump(textbase_values, json_file, indent=4, ensure_ascii=False)
