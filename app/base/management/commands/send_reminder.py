# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.template.loader import get_template
from django.template import Context
from django.core.mail import send_mail
from event.models import Event

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class Command(BaseCommand):
    help = """
    以下の動作をします。毎日午前9時に一度実行されることを想定しています。
    - 翌日開催or翌日登録締切のイベント参加者にリマインダーを送る
    """
    from_email = "reminder@sovolo.earth"
    reminder_template = get_template("email/reminder.txt")
    deadline_template = get_template("email/deadline.txt")

    def handle(self, *args, **options):
        # arg_exist = False
        # for attr in self.attributes:
        #     arg_exist = arg_exist or options[attr]
        #
        # if not arg_exist:
        #     pass
        # else:
        #     pass
        self.stdout.write("running...")

        # TODO
        reminder_events = Event.objects.all()
        for event in reminder_events:
            for user in event.participant.all():
                context = Context({'user': user, 'event': event})
                content = self.reminder_template.render(context)
                subject = content.split("\n", 1)[0]
                message = content.split("\n", 1)[1]
                send_mail(subject, message, self.from_email, [user.email])

        # TODO
        deadline_events = Event.objects.all()
        for event in reminder_events:
            for user in event.participant.all():
                context = Context({'user': user, 'event': event})
                content = self.reminder_template.render(context)
                subject = content.split("\n", 1)[0]
                message = content.split("\n", 1)[1]
                send_mail(subject, message, self.from_email, [user.email])


        self.stdout.write("success...!")

    # def add_arguments(self, parser):
    #     parser.add_argument(
    #         '-user',
    #         dest='user',
    #         action='store_true',
    #         default=False,
    #     )
