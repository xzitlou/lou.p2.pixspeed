from django.db import models

from accounts.models import CustomUser


class Payment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('CARD', 'Card'),
        ('GOOGLE_PAY', 'Google Pay'),
        ('APPLE_PAY', 'Apple Pay'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="payments")
    payment_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.email} - {self.payment_method} - {self.amount} {self.currency}"

    class Meta:
        ordering = ["-created_at"]

    @staticmethod
    def save_payment(user, payment_id, total_credits, status, payment_method):
        if total_credits <= 10000:
            amount = total_credits * 0.009
        else:
            amount = total_credits * 0.002

        amount_in_cents = int(amount * 100)
        payment = Payment.objects.create(
            user=user,
            payment_id=payment_id,
            amount=amount_in_cents / 100,
            status=status,
            payment_method=payment_method,
            description=f"{total_credits} Credits for PixSpeed.com",
        )
        return payment
