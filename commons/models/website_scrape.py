from django.db import models


class WebsiteScrape(models.Model):
    url = models.URLField()
    scraped_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.url
