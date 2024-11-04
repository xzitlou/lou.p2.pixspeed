from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.paginator import Paginator
from django.core.validators import validate_email
from django.db import models
from django.utils import timezone

from app.utils import Utils


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The Email must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length=255, null=True, blank=False)
    email = models.EmailField(max_length=250, unique=True, null=False, blank=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_confirm = models.BooleanField(default=False)
    uuid = models.CharField(max_length=250, default=Utils.generate_uuid, null=False, blank=False)
    verification_code = models.CharField(default=Utils.generate_hex_uuid, max_length=10, null=True, blank=True)
    verification_code_sent_at = models.DateTimeField(default=timezone.now)
    restore_password_token = models.CharField(max_length=250, null=True, blank=False)
    lost_password_email_sent_at = models.DateTimeField(null=True, blank=True)
    lang = models.CharField(max_length=5, default="en")
    updated_at = models.DateField(auto_now_add=True, null=True)
    created_at = models.DateField(default=timezone.now)
    api_token = models.CharField(default=Utils.generate_hex_uuid, max_length=250, null=True, blank=True)
    plan_subscribed = models.CharField(max_length=50, null=True, blank=True)
    is_plan_active = models.BooleanField(default=False)
    image_credits = models.IntegerField(default=0)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["is_staff"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def has_pro_benefits(self):
        if not self.is_authenticated:
            return False

        if self.plan_subscribed and self.next_billing_date and self.next_billing_date >= timezone.now():
            return True

        return False

    def get_payments(self, page=1, per_page=20):
        payments = self.payment_set.filter(
            paypal_redundant_payment=False,
        ).order_by("-id")
        paginator = Paginator(payments, per_page)

        return paginator.get_page(page)

    def regenerate_email_verification_code(self):
        self.verification_code = Utils.genetate_verification_code()
        self.verification_code_sent_at = timezone.now()
        self.save()

    def verify_code(self, data, i18n: dict):
        try:
            code = data.get("verificationCode").strip()
        except Exception as e:
            print(str(e))
            code = None

        if not code:
            return None, i18n.get("missing_verification_code")
        if self.verification_code != code:
            return None, i18n.get("invalid_verification_code")

        self.is_confirm = True
        self.save()

        return self, None

    @staticmethod
    def restore_password(data, i18n: dict):
        token = data.get("tempToken")
        password = data.get("restorePassword")
        confirm_password = data.get("restoreConfirmPassword")
        errors = []

        if not token:
            errors.append(i18n.get("missing_restore_token", "missing_restore_token"))
        if not password:
            errors.append(i18n.get("missing_password", "missing_password"))
        if not confirm_password:
            errors.append(i18n.get("missing_confirm_password", "missing_confirm_password"))
        if len(password) < 8:
            errors.append(i18n.get("weak_password", "weak_password"))
        if password != confirm_password:
            errors.append(i18n.get("passwords_dont_match", "passwords_dont_match"))

        if len(errors):
            return None, errors

        try:
            user = CustomUser.objects.get(restore_password_token=token)
        except Exception as e:
            print(str(e))
            return None, [i18n.get("invalid_restore_token", "invalid_restore_token")]

        user.set_password(password)
        user.save()

        return user, None

    @staticmethod
    def lost_password(data, i18n: dict):
        try:
            email = data.get("lostPasswordEmail").lower()
            validate_email(email)
        except Exception as e:
            print(str(e))
            return None, [i18n.get("invalid_email", "invalid_email")]

        try:
            user = CustomUser.objects.get(email=email)
        except Exception as e:
            print(str(e))
            return None, [i18n.get("invalid_email", "invalid_email")]

        if user.lost_password_email_sent_at and (timezone.now() - user.lost_password_email_sent_at).seconds < 600:
            return None, [i18n.get("email_sent_wait", "email_sent_wait")]

        user.restore_password_token = Utils.generate_hex_uuid()
        user.lost_password_email_sent_at = timezone.now()
        user.save()

        return user, None

    @staticmethod
    def login_user(email: str, i18n: dict):
        try:
            email = email.lower().strip()
            validate_email(email)
            user = CustomUser.objects.get(email__iexact=email)
        except Exception as e:
            print(str(e))
            return None, [i18n.get("wrong_credentials", "wrong_credentials")]

        return user, None

    @staticmethod
    def register_user(full_name: str, email: str, i18n: dict, lang: str):
        if not full_name:
            return None, [i18n.get("missing_full_name", "missing_full_name")]
        try:
            email = email.lower().strip()
            validate_email(email)
        except Exception as e:
            print(str(e))
            return None, [i18n.get("invalid_email", "invalid_email")]

        if CustomUser.objects.filter(email=email).exists():
            return None, [i18n.get("email_taken", "email_taken")]

        user = CustomUser.objects.create(
            full_name=full_name.title(),
            email=email,
            lang=lang
        )
        user.set_password(Utils.generate_hex_uuid())
        user.save()

        return user, None

    def update_password(self, data, i18n: dict):
        current_password = data.get("securityPassword")
        new_password = data.get("securityNewPassword")
        confirm_new_password = data.get("securityConfirmNewPassword")
        errors = []

        if not current_password:
            errors.append(i18n.get("missing_password", "missing_password"))
        if not new_password:
            errors.append(i18n.get("missing_new_password", "missing_new_password"))
        if not confirm_new_password:
            errors.append(i18n.get("missing_confirm_new_password", "missing_confirm_new_password"))
        if len(new_password) < 8:
            errors.append(i18n.get("weak_password", "weak_password"))
        if new_password != confirm_new_password:
            errors.append(i18n.get("passwords_dont_match", "passwords_dont_match"))
        if len(errors):
            return None, errors

        if not self.check_password(current_password):
            return None, [i18n.get("wrong_password", "wrong_password")]

        self.set_password(new_password)
        self.save()

        return self, None
