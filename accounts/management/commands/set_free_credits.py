from dateutil.relativedelta import relativedelta
from django.core.management import BaseCommand
from django.utils import timezone

from accounts.models import CustomUser


class Command(BaseCommand):
    help = "set_free_credits"

    def handle(self, *args, **options):
        today = timezone.now().date()

        for user in CustomUser.objects.filter(
            next_free_credits_date__day=today.day,
            next_free_credits_date__month=today.month,
            next_free_credits_date__year=today.year,
        ):
            user.free_image_credits = 300
            user.next_free_credits_date += relativedelta(months=1)
            user.save()
