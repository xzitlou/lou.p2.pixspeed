from django.core.validators import validate_email
from django.db import models
from django.utils import timezone

from accounts.models import CustomUser


class Message(models.Model):
    email = models.EmailField(max_length=250)
    message = models.TextField()
    created_at = models.DateField(default=timezone.now)

    def __str__(self):
        return self.email

    @staticmethod
    def save_message(data, i18n: dict):
        i18n = i18n or {}
        email = data.get("email_address")
        message = data.get("message")
        errors = []

        try:
            email = email.lower()
            validate_email(email)
        except Exception as e:
            print(str(e))
            errors.append(i18n.get("invalid_email", "invalid_email"))

        if not message:
            errors.append(i18n.get("missing_message", "missing_message"))

        if len(errors):
            return errors

        Message.objects.create(
            email=email,
            message=message
        )
