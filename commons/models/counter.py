from django.db import models
from django.utils.text import slugify


class Counter(models.Model):
    code_name = models.CharField(max_length=150)
    counter = models.IntegerField(default=0)

    def __str__(self):
        return self.code_name

    def save(self, *args, **kwargs):
        self.code_name = slugify(self.code_name).replace("-", "_")
        super().save(*args, **kwargs)

    @staticmethod
    def increase_count(code_name: str):
        counter, _ = Counter.objects.get_or_create(code_name=code_name)
        counter.counter += 1
        counter.save()

    @staticmethod
    def get_counter(code_name: str):
        try:
            return Counter.objects.get(code_name=code_name).counter
        except Exception as e:
            print(str(e))
            return 0
