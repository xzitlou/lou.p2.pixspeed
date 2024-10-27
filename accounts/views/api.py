import json
from hashlib import md5

from django.http import JsonResponse
from django.views import View

from app.utils import Utils
from app.views import GlobalVars
from config import RATE_LIMIT


class RateLimitAPI(View):
    @staticmethod
    def post(request):
        ip = Utils.get_ip(request)
        user_agent = request.headers["User_Agent"]
        cache_key = md5(f"{ip} {user_agent}".encode()).hexdigest()
        rate_total_seconds = 60 * 60
        counter = 0

        if request.user.is_authenticated and request.user.has_pro_benefits():
            print("User has PRO benefits")
            return JsonResponse({
                "status": True,
                "ip": ip
            })

        cache_data = Utils.get_from_cache(cache_key)

        if cache_data:
            counter = cache_data.get("counter")
        if counter >= RATE_LIMIT:
            return JsonResponse({
                "rate_limit": True,
                "ip": ip,
                "until": Utils.get_expire_info_cache(cache_key),
            }, status=400)

        counter += 1
        Utils.set_to_cache(cache_key, {"counter": counter}, exp=rate_total_seconds)

        return JsonResponse({
            "status": True,
            "ip": ip
        })


class ResendVerificationEmailAPI(View):
    @staticmethod
    def post(request):
        settings = GlobalVars.get_globals(request)
        request.user.regenerate_email_verification_code()
        Utils.send_email(
            recipients=[request.user.email],
            subject=settings.get("i18n").get("subject_verification"),
            template="email-verification",
            data={
                "user": request.user,
                "g": settings
            }
        )

        return JsonResponse({
            "html": f"""<div class="alert alert-success">{settings.get('i18n').get('verification_email_resent')}</div>"""
        })


class DeleteAccountAPI(View):
    @staticmethod
    def delete(request):
        request.user.cancel_subscription(
            reasons=json.loads(request.body).get("deleting"),
            cancellation_type="delete_account"
        )
        request.user.delete()
        return JsonResponse({"status": True})
