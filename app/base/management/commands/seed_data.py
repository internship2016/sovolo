from django.core.management.base import BaseCommand
from django.utils import timezone
from event.models import Event, Participation
from group.models import Group, Membership
from user.models import User

class Command(BaseCommand):
    help = 'This is a custom command created to seed the database with test data.'

    def _create_user(self):
        default_admin = User(
                first_name = 'admin',
                last_name = 'admin',
                nickname = 'admin',
                birthday = timezone.now(),
                telephone = 123456789,
                emergency_contact = 119,
                email = 'admin@admin.com',
                occupation = 'ADMIN',
                is_admin = True
            )
        default_admin.set_password('pass1234')
        default_admin.save()

        testuser = User(
                first_name = 'test',
                last_name = 'user',
                nickname = 'test',
                birthday = timezone.now(),
                telephone = 123456789,
                emergency_contact = 119,
                email = 'test@test.com',
                occupation = 'NEET',
            )
        testuser.set_password('pass1234')
        testuser.save()

        for i in range(10):
            lastname = str(i)
            nickname = "generic_user_%d" %(i)
            email = "test@%d.com" %(i)
            user = User(
                first_name = 'genericuser',
                last_name = lastname,
                nickname = nickname,
                birthday = timezone.now(),
                telephone = 123456789,
                emergency_contact = 119,
                email = email,
                occupation = 'NEET',
            )
            user.set_password('pass1234')
            user.save()

    def _create_event(self):

        for i in range(10):
            name = "Generic Event #%d" %(i)
            host_user = User.objects.all()[i]
            admin = host_user
            genericevent = Event(
                name=name,
                start_time=timezone.now(),
                end_time=timezone.now(),
                meeting_place="531 Page Street",
                place="531 Page Street",
                contact="interlink@interlink.com",
                details="This is a generic event.",
                ticket=False,
                host_user=host_user,
                region=1,
            )
            genericevent.save()
            genericevent.admin = User.objects.filter(pk=1)

    def _create_participant(self):
        for event in Event.objects.all():
            participation = Participation(
                event=event,
                user=User.objects.get(pk=event.pk),
                status='participating',
            )
            participation.save()

            if event.pk==1:
                continue

            participation = Participation(
                event=event,
                user=User.objects.get(pk=1),
                status='participating',
            )
            participation.save()

    def _create_group(self):
        for i in range(10):
            name = "generic group #%d" %(i)
            description = "This is a generic group. Don't join."
            group = Group(
                name=name,
                description=description,
                )
            group.save()

    def _create_membership(self):
        for group in Group.objects.all():
            member = User.objects.get(pk=group.pk)
            membership = Membership(
                member=member,
                group=group,
            )

            if group.pk==1:
                continue

            membership = Membership(
                member=User.objects.get(pk=1),
                group=group,
                role='admin',
            )

    def handle(self, *args, **options):
        self._create_user()
        self._create_event()
        self._create_participant()
        self._create_group()
        self._create_membership()
