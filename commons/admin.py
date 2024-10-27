from django.contrib import admin

from commons.models.counter import Counter


class CounterAdmin(admin.ModelAdmin):
    list_display = (
        "code_name",
        "counter",
    )


admin.site.register(Counter, CounterAdmin)
