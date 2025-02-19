from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from accounts.models import OtpCode
from django.utils.timezone import now
import pytz


class Command(BaseCommand):

    def handle(self, *args, **options):
        expired_time = datetime.now(tz=pytz.timezone('Asia/Tehran')) - timedelta(minutes=2)
        OtpCode.objects.filter(created__lt=expired_time).delete()
        self.stdout.write('all expired otps are deleted.')
