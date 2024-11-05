from django.shortcuts import render, redirect
from django.views import View
from square.client import Client

from app.views import GlobalVars
from config import SQUARE_KEYS
from payments.models import Payment


class PaymentPage(View):
    settings = None
    errors = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")

        self.settings = GlobalVars.get_globals(request)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        response = render(
            request,
            "views/payment.html",
            {
                "title": f"Check-out - PixSpeed.com",
                "description": "",
                "errors": self.errors,
                "g": self.settings,
                "squareup": SQUARE_KEYS,
            }
        )

        return response

    def post(self, request, *args, **kwargs):
        data = request.POST
        total_credits = int(data.get("credits"))
        payment_method = data.get("method")
        nonce = data.get("nonce")

        if total_credits <= 10000:
            amount_in_cents = int(total_credits * 0.009 * 100)
        else:
            amount_in_cents = int(total_credits * 0.002 * 100)

        client = Client(
            access_token=SQUARE_KEYS.get("access_token"),
            environment=SQUARE_KEYS.get("environment"),
        )

        try:
            result = client.payments.create_payment(
                {
                    "source_id": nonce,
                    "amount_money": {
                        "amount": amount_in_cents,
                        "currency": "USD"
                    },
                    "idempotency_key": f"{request.user.id}-{nonce}"
                }
            )

            if result.is_success():
                Payment.save_payment(
                    user=request.user,
                    payment_id=result.body['payment']['id'],
                    total_credits=total_credits,
                    status='COMPLETED',
                )
                return redirect("thanks")

            self.errors = [result.errors[0]['detail'] if result.errors else "Unknown error"]
            return self.get(request, *args, **kwargs)

        except Exception as e:
            self.errors = [str(e)]
            return self.get(request, *args, **kwargs)
