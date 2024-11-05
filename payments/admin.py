from django.contrib import admin

from payments.models import Payment


class PaymentAdmin(admin.ModelAdmin):
    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(Payment, PaymentAdmin)
