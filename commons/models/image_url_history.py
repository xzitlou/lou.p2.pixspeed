from django.db import models


class ImageUrlHistory(models.Model):
    url = models.TextField()
    format = models.CharField(max_length=50, null=True, blank=True)
    was_success = models.BooleanField(default=False)
    from_api = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.url
