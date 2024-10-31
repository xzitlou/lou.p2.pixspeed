from django.db import models


class WebsiteScrape(models.Model):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    STATUS_CHOICES = (
        (PENDING, PENDING),
        (SUCCESS, SUCCESS),
        (FAILED, FAILED),
    )

    url = models.URLField()
    scraped_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default=PENDING, choices=STATUS_CHOICES)
    total_images_found = models.IntegerField(default=0)

    def __str__(self):
        return self.url
