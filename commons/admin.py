from django.contrib import admin

from commons.models.counter import Counter
from commons.models.image_url_history import ImageUrlHistory
from commons.models.website_scrape import WebsiteScrape


class CounterAdmin(admin.ModelAdmin):
    list_display = (
        "code_name",
        "counter",
    )


class WebsiteScrapeAdmin(admin.ModelAdmin):
    list_display = (
        "url",
        "status",
        "total_images_found",
        "scraped_at",
    )


class ImageUrlHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "url",
        "format",
        "was_success",
    )


admin.site.register(Counter, CounterAdmin)
admin.site.register(WebsiteScrape, WebsiteScrapeAdmin)
admin.site.register(ImageUrlHistory, ImageUrlHistoryAdmin)
