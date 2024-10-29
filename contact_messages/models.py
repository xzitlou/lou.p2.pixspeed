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
    def save_message(data, settings: dict):
        i18n = settings.get("i18n")
        email = data.get("contactEmail")
        message = data.get("contactMessage")
        errors = []

        if not email:
            errors.append(i18n.get("missing_email", "missing_email"))
        else:
            try:
                email = email.lower()
                validate_email(email)
            except:
                errors.append(i18n.get("invalid_email", "invalid_email"))

        if not message:
            errors.append(i18n.get("missing_message", "missing_message"))

        if len(errors):
            return None, errors

        message = Message.objects.create(
            email=email,
            message=message
        )
        message.save()

        return message, None
