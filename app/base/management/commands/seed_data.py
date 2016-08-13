from django.core.management.base import BaseCommand
from django.utils import timezone
from event.models import Event, Participation, Frame, Comment, Question, Answer
from group.models import Group, Membership
from user.models import User
from tag.models import Tag

class Command(BaseCommand):
    help = """
    This is a custom command created to seed the database with test data.
    The following flags can be specified to add specific data sets.
    -user: Adds users.
    -event: Adds events. Requires users to exist.
    -frame: Adds frames. Requires users and events to exist.
    -participation: Adds participations. Requires users, events, and frames to exist.
    -comment: Adds comments. Requires users, events, frames, and participations to exist.
    -group: Adds groups. Requires users to exist.
    -member: Adds members to groups. Requires users and groups to exist.
    -tag: Adds tags. Requires users to exist.
    -qanda: Adds questions and answers. Requires users, events, frames, and participations to exist.
    """

    attributes = ('user', 'event', 'frame', 'participation', 'comment', 'group', 'member', 'tag', 'qanda')

    def add_arguments(self, parser):
        parser.add_argument(
            '-user',
            dest='user',
            action='store_true',
            default=False,
        )
        parser.add_argument(
            '-event',
            dest='event',
            action='store_true',
            default=False,
        )
        parser.add_argument(
            '-frame',
            dest='frame',
            action='store_true',
            default=False,
        )
        parser.add_argument(
            '-participation',
            dest='participation',
            action='store_true',
            default=False,
        )
        parser.add_argument(
            '-comment',
            dest='comment',
            action='store_true',
            default=False,
        )
        parser.add_argument(
            '-group',
            dest='group',
            action='store_true',
            default=False,
        )
        parser.add_argument(
            '-member',
            dest='member',
            action='store_true',
            default=False,
        )
        parser.add_argument(
            '-tag',
            dest='tag',
            action='store_true',
            default=False,
        )
        parser.add_argument(
            '-qanda',
            dest='qanda',
            action='store_true',
            default=False,
        )

    def _create_users(self):
        default_admin = User(
                first_name = 'admin',
                last_name = 'admin',
                username = 'admin',
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
                username = 'test',
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
            username = "generic_user_%d" %(i)
            email = "test@%d.com" %(i)
            user = User(
                first_name = 'genericuser',
                last_name = lastname,
                username = username,
                birthday = timezone.now(),
                telephone = 123456789,
                emergency_contact = 119,
                email = email,
                occupation = 'NEET',
            )
            user.set_password('pass1234')
            user.save()


    def _create_events(self):

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


    def _create_frames(self):
        for event in Event.objects.all():
            frame = Frame(
                event=event,
                lower_limit=0,
                upper_limit=100,
                deadline="2100-12-25 00:00:00",
            )
            frame.save()

    def _create_participants(self):
        for event in Event.objects.all():
            for frame in Frame.objects.filter(event=event):
                participation = Participation(
                    event=event,
                    frame=frame,
                    user=User.objects.get(pk=frame.pk),
                    status='participating',
                )
                participation.save()

                if not frame.pk==1:
                    participation = Participation(
                        event=event,
                        frame=frame,
                        user=User.objects.get(pk=1),
                        status='participating',
                    )
                participation.save()

    def _create_comments(self):
        for event in Event.objects.all():
            for participation in Participation.objects.filter(event=event):
                comment = Comment(
                    event=event,
                    user=participation.user,
                    text="あああああああああああああああああああああああ",
                )
                comment.save()

        for comment in Comment.objects.all():
            target = Comment.objects.get(pk=1)
            comment.text = "黙れ"
            comment.reply_to = target


    def _create_groups(self):
        for i in range(10):
            name = "generic group #%d" %(i)
            description = "This is a generic group. Don't join."
            group = Group(
                name=name,
                description=description,
                )
            group.save()

    def _create_memberships(self):
        for group in Group.objects.all():
            member = User.objects.get(pk=group.pk)
            membership = Membership(
                member=member,
                group=group,
            )
            membership.save()   

            if group.pk==1:
                continue

            membership = Membership(
                member=User.objects.get(pk=1),
                group=group,
                role='admin',
            )

            membership.save()

    def _create_tags(self):
        taglist = ('python', 'ruby', 'django', 'ohmygod', 'mddslkfjakl', 'global', 'ゴミ拾い', '環境保護', 'interlink', '子供')
        user = User.objects.get(pk=1)
        for t in taglist:
            tag = Tag(
                name=t,
            )
            tag.save()
            user.follow_tag.add(tag)
            user2 = User.objects.get(pk=tag.pk)
            user2.follow_tag.add(tag)
        for event in Event.objects.all():
            tag = Tag.objects.get(pk=event.pk)
            event.tag.add(tag)

    def _create_questions_and_answers(self):
        for event in Event.objects.all():
            question = Question(
                event=event,
                question="How are you?",
            )
            question.save()
            for participation in Participation.objects.filter(event=event):
                answer = Answer(
                    question=question,
                    participation=participation,
                    text="I'm fine thank you.",
                )
                answer.save()


    def handle(self, *args, **options):
        arg_exist = False
        for attr in self.attributes:
            arg_exist = arg_exist or options[attr]

        if not arg_exist:
            self._create_users()
            self._create_events()
            self._create_frames()
            self._create_participants()
            self._create_comments()
            self._create_groups()
            self._create_memberships()
            self._create_tags()
            self._create_questions_and_answers()
        else:
            if options['user']:
                self._create_users()
            if options['event']:
                self._create_events()
            if options['frame']:
                self._create_frames()
            if options['participation']:
                self._create_participants()
            if options['comment']:
                self._create_comments()
            if options['member']:
                self._create_memberships()
            if options['tag']:
                self._create_tags()
            if options['qanda']:
                self._create_questions_and_answers()

