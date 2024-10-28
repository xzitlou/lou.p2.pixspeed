from django.db import models


class TextBase(models.Model):
    code_name = models.CharField(max_length=250, unique=True)
    text = models.TextField()

    def __str__(self):
        return self.code_name
