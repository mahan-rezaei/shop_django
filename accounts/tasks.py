from celery import shared_task
from datetime import datetime, timedelta
from accounts.models import OtpCode
import pytz


@shared_task
def remove_expired_otp_codes():
    expired_time = datetime.now(tz=pytz.timezone('Asia/Tehran')) - timedelta(minutes=2)
    OtpCode.objects.filter(created__lt=expired_time).delete()