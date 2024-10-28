from django.contrib import admin

from translations.models.language import Language
from translations.models.textbase import TextBase
from translations.models.translation import Translation


class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'iso', 'en_label',)


class TranslationAdmin(admin.ModelAdmin):
    list_display = ('code_name', 'language', 'text',)
    search_fields = ('code_name', 'text',)
    list_filter = ('language',)


class TextBaseAdmin(admin.ModelAdmin):
    list_display = ('code_name', 'text',)
    search_fields = ('code_name', 'text',)


admin.site.register(Language, LanguageAdmin)
admin.site.register(Translation, TranslationAdmin)
admin.site.register(TextBase, TextBaseAdmin)
