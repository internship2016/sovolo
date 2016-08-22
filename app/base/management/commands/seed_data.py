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

    prefectures = {
        "Hokkaido": "北海道",
        "Aomori": "青森県",
        "Iwate": "岩手県",
        "Miyagi": "宮城県",
        "Akita": "秋田県",
        "Yamagata": "山形県",
        "Fukushima": "福島県",
        "Ibaraki": "茨城県",
        "Tochigi": "栃木県",
        "Gunnma": "群馬県",
        "Saitama": "埼玉県",
        "Chiba": "千葉県",
        "Tokyo": "東京都",
        "Kanagawa": "神奈川県",
        "Niigata": "新潟県",
        "Toyama": "富山県",
        "Ishikawa": "石川県",
        "Fukui": "福井県",
        "Yamanashi": "山梨県",
        "Nagano": "長野県",
        "Gifu": "岐阜県",
        "Shizuoka": "静岡県",
        "Aichi": "愛知県",
        "Mie": "三重県",
        "Shiga": "滋賀県",
        "Kyoto": "京都府",
        "Osaka": "大阪府",
        "Hyogo": "兵庫県",
        "Nara": "奈良県",
        "Wakayama": "和歌山県",
        "Tottori": "鳥取県",
        "Shimane": "島根県",
        "Okayama": "岡山県",
        "Hiroshima": "広島県",
        "Yamaguchi": "山口県",
        "Tokushima": "徳島県",
        "Kagawa": "香川県",
        "Ehime": "愛媛県",
        "Kouchi": "高知県",
        "Fukuoka": "福岡県",
        "Saga": "佐賀県",
        "Nagasaki": "長崎県",
        "Kumamoto": "熊本県",
        "Ooita": "大分県",
        "Miyazaki": "宮崎県",
        "Kagoshima": "鹿児島県",
        "Okinawa": "沖縄県"
    }

    prefec_list = list(prefectures)

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
                occupation = '自宅警備員',
            )
        testuser.set_password('pass1234')
        testuser.save()

        for i in range(20):
            lastname = str(i)
            username = "generic_user_%d" %(i+1)
            email = "test@%d.com" %(i+1)
            user = User(
                first_name = 'genericuser',
                last_name = lastname,
                username = username,
                birthday = timezone.now() - timezone.timedelta(days=i*365),
                telephone = 123456789,
                emergency_contact = 119,
                email = email,
                occupation = 'NEET',
                region = self.prefec_list[i],
            )
            user.set_password('pass1234')
            user.save()


    def _create_events(self):

        prefectures = {
            "Hokkaido": "北海道",
            "Aomori": "青森県",
            "Iwate": "岩手県",
            "Miyagi": "宮城県",
            "Akita": "秋田県",
            "Yamagata": "山形県",
            "Fukushima": "福島県",
            "Ibaraki": "茨城県",
            "Tochigi": "栃木県",
            "Gunnma": "群馬県",
            "Saitama": "埼玉県",
            "Chiba": "千葉県",
            "Tokyo": "東京都",
            "Kanagawa": "神奈川県",
            "Niigata": "新潟県",
            "Toyama": "富山県",
            "Ishikawa": "石川県",
            "Fukui": "福井県",
            "Yamanashi": "山梨県",
            "Nagano": "長野県",
            "Gifu": "岐阜県",
            "Shizuoka": "静岡県",
            "Aichi": "愛知県",
            "Mie": "三重県",
            "Shiga": "滋賀県",
            "Kyoto": "京都府",
            "Osaka": "大阪府",
            "Hyogo": "兵庫県",
            "Nara": "奈良県",
            "Wakayama": "和歌山県",
            "Tottori": "鳥取県",
            "Shimane": "島根県",
            "Okayama": "岡山県",
            "Hiroshima": "広島県",
            "Yamaguchi": "山口県",
            "Tokushima": "徳島県",
            "Kagawa": "香川県",
            "Ehime": "愛媛県",
            "Kouchi": "高知県",
            "Fukuoka": "福岡県",
            "Saga": "佐賀県",
            "Nagasaki": "長崎県",
            "Kumamoto": "熊本県",
            "Ooita": "大分県",
            "Miyazaki": "宮崎県",
            "Kagoshima": "鹿児島県",
            "Okinawa": "沖縄県"
        }

        prefec_list = list(prefectures)

        for i in range(20):
            name = "Generic Event #%d" %(i+1)
            host_user = User.objects.all()[i]
            admin = host_user
            genericevent = Event(
                name=name,
                start_time=timezone.now() - timezone.timedelta(days=i) ,
                end_time=timezone.now() - timezone.timedelta(days=i+1),
                meeting_place="531 Page Street",
                contact="interlink@interlink.com",
                details="This is a generic event.",
                host_user=host_user,
                region=prefec_list[i],
            )
            genericevent.save()
            genericevent.admin = User.objects.filter(pk=1)


    def _create_frames(self):
        for event in Event.objects.all():
            frame = Frame(
                event=event,
                upper_limit=3,
                deadline="2100-12-25 00:00:00",
            )
            frame.save()

    def _create_participants(self):
        for event in Event.objects.all():
            for frame in Frame.objects.filter(event=event):
                participation = Participation(
                    event=event,
                    frame=frame,
                    user=User.objects.get(pk=1),
                    status='管理者',
                )

                participation.save()

                if not frame.pk==1:
                    participation = Participation(
                        event=event,
                        frame=frame,
                        user=User.objects.get(pk=frame.pk),
                        status='参加中',
                    )
                    participation.save()

                participation.save()

        e = Event.objects.get(pk=2)
        f = e.frame_set.first()
        i=3
        while not f.is_full():
            p = Participation(
                event=e,
                frame=f,
                user=User.objects.get(pk=i),
                status='参加中',
            )
            p.save()
            i+=1

        p = Participation(
            event=e,
            frame=f,
            user=User.objects.get(pk=10),
            status='キャンセル待ち',
        )
        p.save()


    def _create_comments(self):
        for event in Event.objects.all():
            for participation in Participation.objects.filter(event=event):
                comment = Comment(
                    event=event,
                    user=participation.user,
                    text="""ああああああああああああああああああああああああああああああああああああああああああああ
                    ああああああああああああああああああああああああああああああああああああああああああああああああ
                    あああああああああああああああああああああああああああああああああああああああああああああああ
                    あああああああああああああああああああああああああああああああああああああああああああああああ
                    あああああああああああああああああああああああああああああああああああああああああああああああ
                    あああああああああああああああああああああああああああああああああああああああああああああああ
                    """,
                )
                comment.save()
                reply_comment = Comment(
                    event=event,
                    user=participation.user,
                    text="""すみませんでした。
                        """,
                    reply_to=comment,
                )
                reply_comment.save()

    def _create_groups(self):
        for i in range(20):
            name = "generic group #%d" %(i+1)
            description = "This is a generic group. Don't join."
            group = Group(
                name=name,
                description=description,
                )
            group.save()
            event = Event.objects.get(pk=group.pk)
            group.event.add(event)

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
        taglist = (
            '環境',
            '地域',
            '人権',
            '教育',
            '医療',
            '介護',
            '国際協力',
            '文化',
            'スポーツ',
            '被災者支援',
            '動物'
        )
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
            tag = Tag.objects.get(pk=(event.pk % len(taglist)+1))
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



