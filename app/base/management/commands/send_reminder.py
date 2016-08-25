# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.template.loader import get_template
from django.template import Context
from django.core.mail import send_mail
from event.models import Event, Frame
from base.utils import send_template_mail
from django.utils import timezone
import datetime
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class Command(BaseCommand):
    help = """
    以下の動作をします。毎日午前9時に一度実行されることを想定しています。
    - 翌日開催or翌日登録締切のボランティア参加者にリマインダーを送る
    """
    from_address = "reminder@sovol.earth"

    def handle(self, *args, **options):
        self.stdout.write("running...")
        today = datetime.datetime.combine(
            datetime.date.today(),
            datetime.time(0, 0, tzinfo=timezone.LocalTimezone())
        )

        reminder_template = get_template("email/reminder.txt")
        reminder_events = Event.objects.filter(
            start_time__gte= today + datetime.timedelta(days=1),
            start_time__lt = today + datetime.timedelta(days=2),
        )
        for event in reminder_events:
            for user in event.participant.all():
                send_template_mail(
                    reminder_template,
                    {'user': user, 'event': event},
                    self.from_address,
                    [user.email]
                )

        deadline_template = get_template("email/deadline.txt")
        deadline_frames = Frame.objects.filter(
            deadline__gte=today + datetime.timedelta(days=1),
            deadline__lt=today + datetime.timedelta(days=2),
        )

        for frame in deadline_frames:
            if not frame.event in reminder_events:
                for user in frame.participant.all():
                    send_template_mail(
                        deadline_template,
                        {'user': user, 'event': frame.event},
                        self.from_address,
                        [user.email]
                    )

        self.stdout.write("success...!")