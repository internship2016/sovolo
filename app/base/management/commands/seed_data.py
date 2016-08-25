from django.core.management.base import BaseCommand
from django.utils import timezone
from event.models import Event, Participation, Frame, Comment, Question, Answer
from group.models import Group, Membership
from user.models import User
from tag.models import Tag

username_sample=[
"koshiba_takahiro"
,"yusuke0803"
,"_daisuke_"
,"sugiyama_xxx"
,"yasunori_abe"
,"tesitesi2"
,"apple_love"
,"windows_love"
,"lovesf531"
,"miyagawa_daisuke"
,"urasima_tarou"
,"gold_tarou"
,"peach_tarou"
,"issunn_bo-shi"
,"nakashima_atushi"
,"haraguti_joji"
,"ai_sakamoto2929"
,"_mami_takahashi_"
,"daiki_kobayashi"
,"xi-fuen"
,"rao-xien1849"
,"ReportsInformer"
,"Robinessa"
,"Sellbreets"
,"Showerzoff"
,"Spotexpeat"
]

eventname_sample=[
    {"name":"TOKYO DESIGN WEEK 2016 会場運営ボランティア","description":"Tokyo Design Weekの会場運営ボランティアを募集します。動きやすい服装でお越しください"},
    {"name":"「ココロをシェアする」コミュニティスペースの看板スタッフ募集","description":"コミュニティスペースの看板作成のスタッフを募集します。だれでも可能ですが日曜大工の経験のある方など歓迎します"},
    {"name":"ダイビングを通してサンゴ礁の保全活動に貢献しませんか？","description":"沖縄の海でダイビングをしてみませんか？ダイビングを通して経験したサンゴ礁保護活動をメディアに発表します"},
    {"name":"御船町ボランティア本部より⬛ 炊き出しプロジェクト","description":"御船町で炊き出しをします。"},
    {"name":" 【PC作業ができる方！】「人と地域を元気に」生活習慣改善センターがボラ募集","description":"仙台でＰＣ作業のできる方を募集します。具体的にはＨＰ作成やエクセルの簡単な操作を手伝っていただきます。仕事内容によっては報酬もあります。"},
    {"name":"【随時募集！】子ども好きの方歓迎！ピースジャムがボランティア募集！","description":""},
    {"name":"おばあちゃんとお化粧&おしゃべりを楽しむ！エステ！@東あずま","description":""},
    {"name":"いつでも、一回でも！気軽にボランティア【登録制】～サッカー、お化粧、革細工、野菜作りe.t.c","description":""},
    {"name":"子どもの遊びと学びを支える学生・若手社会人ボランティア募集！","description":""},
    {"name":"「子ども食堂」運営ボランティア募集","description":""},
    {"name":"入院加療中のこどもへのスポーツ・文化活動をサポートするボランティア募集","description":""},
    {"name":"【国際協力団体ADRA】マーケティングで国際協力。NGOインターン募集","description":""},
    {"name":"ビジネスの手法で社会貢献しよう！社会起業家について学べる無料セミナー","description":""},
    {"name":" 【市民とNPOの交流サロン】『障害を持つ人が地域で安心して生活できる社会の実現をめざして』","description":""},
    {"name":"「きっと見つかるあなたの国際協力のカタチ！ ～NGO×企業トーク&ミャンマーお食事会～」を開催","description":""},
    {"name":" 「NPOの組織マネジメント　強くあたたかい組織のつくり方」 〜NPO22団体の事例・ノウハウから見えてきた３つの観点〜","description":""},
    {"name":"国際協力NGOシャプラニー会報発送ボランティア募集","description":""},
    {"name":"4泊５日の農山村ボランティア「若葉のふるさと協力隊」参加者募集","description":""},
    {"name":" 【シンポジウム】『すべての子どもを社会で支える！』","description":""},
    {"name":"「悩みを話せる友達が見つかる」がコンセプト。悩み相談サイトのメンバー募集！","description":""},
    {"name":"PLAS事務局インターン説明会を開催します！","description":""},
    {"name":"住まいとコミュニティづくりNPO交流会－助成事業活動報告会－","description":""},
    {"name":"施設の子供たちと遊んでくれる学生募集！","description":""},
    {"name":"あなたのアイデアを活かして地域活性化に取り組みませんか？【地域活性化ハッカソン】","description":""},
    {"name":"失われた木々を取り戻すための植林作業～あなたの手で森を守りませんか～","description":""},
    {"name":"子供たちの避難訓練を手伝っていただけるかた募集【昼食付き】","description":""},
    {"name":"介護施設のレクリエーションにご参加いただける団体募集【個人も可】","description":""},
    ]

groupname_sample=[
    "早稲田大学キッズラブ同好会",
    "ボランティアビジネス会VBG",
    "奥多摩の自然を守る会",
    "立命館高校落語研究会ボランティア",
    "キッズボランティアいんたーりんく",
    "PLO児童支援団体",
    "御徒町地域清掃ＮＰＯ団体",
    "自閉症児支援団体",
    "上川町自治体",
    "としま区わくわくボランティア",
    "ボランティア団体ＳＯＶＯＬ",
    "国際協力ＮＧＯシャプラニー",
    "児童教育団体",
    "寝屋川市活性化団体",
    "シルバー支援会温故知新",
    "東京大学情報理工学系研究科ITボランティアサークル UT-VOLIT",
    "被災地支援総合ボランティア団体",
    "地震研究会支援支部",
    "海外青年協力隊プラットフォーム",
    "ＮＰＯ法人キャピタルアース",
    "ＮＰＯ法人山口組",
    "動物愛護団体スワローズ",
]

comment_sample=[
    """Samsung Z2は、“世界初の4G LTE通信対応Tizenスマートフォン” という肩書きを除けば、非常に平凡なローエンド端末であると言えます。
    しかしながら、4590インドルピー（約6850円）という価格設定や、兄弟端末「Samsung Z1」よりも確実に強化されたスペックに加え、
    投入される市場のニーズを抑えた機能を実装することにより、新興成長市場においては魅力的な選択肢となり得る端末に仕上げられている模様です。
    """,
    """
    米グーグルがアプリ開発者向けに提供している「Google Play Developer Console」上においては、
    アプリ上で発生したクラッシュやANR（アプリが応答しない）エラーのデータを確認することができますが、
    Android Policeによると、今回そのページ上にあるフィルタリング用の項目の中に、「Android 7.1」という記述が確認されたとのことです。
    """,
    """
    コメント（英: comment）とは、コンピュータ言語（プログラミング言語やデータ記述言語）によって書かれたソースコードのうち、
    人間のために覚えとして挿入された注釈のことである。この部分はコンピュータが処理を行うときにはないものとして無視されるため、自由に文を挿入することができる。
    """
]


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
            username = username_sample[i]
            email = "test%d@sovol.earth" %(i+1)
            user = User(
                first_name = 'genericuser',
                last_name = lastname,
                username = username,
                birthday = timezone.now() - timezone.timedelta(days=4000+i*365),
                telephone = 123456789,
                emergency_contact = 119,
                email = email,
                occupation = 'NEET',
                region = self.prefec_list[i],
            )
            user.set_password('pass1234')
            user.save()

        for i in range(1,30):
            firstname = 'demo_user'
            lastname = str(i)
            username = 'demo_user_'+str(i)
            email = "demo%d@sovol.earth"%i
            user = User(
                first_name=firstname,
                last_name=lastname,
                username=username,
                birthday=timezone.now() - timezone.timedelta(days=4000+i*365),
                telephone=123456789,
                emergency_contact=119,
                email=email,
                occupation='BUG_TEST',
                region=self.prefec_list[i%47],
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
            name = eventname_sample[i]["name"]
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

        for i in range(1,30):
            for j in [1,2]:
                name = "【第%d回】"%j + eventname_sample[i%len(eventname_sample)]["name"]
                host_user = User.objects.get(username="demo_user_%d"%i)
                demoevent = Event(
                    name=name,
                    start_time=timezone.now() - timezone.timedelta(days=i+1) - timezone.timedelta(hours=j),
                    end_time = timezone.now() - timezone.timedelta(days=i) - timezone.timedelta(hours=j),
                    meeting_place="池袋駅東口母子像前",
                    contact="interlink@interlink.com",
                    details="デモ用の過去のイベントです。",
                    host_user=host_user,
                    region=prefec_list[i%47],
                )
                demoevent.save()
                demoevent.admin = User.objects.filter(pk=i)

        for i in range(1, 4):
            for j in [1,2]:
                name = eventname_sample[(i+(j-1)*3)%len(eventname_sample)]["name"]
                host_user = User.objects.get(username="demo_user_%d" % i)
                demoevent = Event(
                    name=name,
                    start_time=timezone.now() - timezone.timedelta(days=i) - timezone.timedelta(hours=j),
                    end_time=timezone.now() + timezone.timedelta(days=i) + timezone.timedelta(hours=j),
                    meeting_place="池袋駅東口母子像前",
                    contact="interlink@interlink.com",
                    details="デモ用の開催中のイベントです。",
                    host_user=host_user,
                    region=prefec_list[i % 47],
                )
                demoevent.save()
                demoevent.admin = User.objects.filter(pk=i)

                name = eventname_sample[(6+i+(j-1)*3)%len(eventname_sample)]["name"]
                host_user = User.objects.get(username="demo_user_%d"%i)
                demoevent = Event(
                    name=name,
                    start_time=timezone.now() + timezone.timedelta(days=i) + timezone.timedelta(hours=j*3),
                    end_time = timezone.now() + timezone.timedelta(days=i+1) + timezone.timedelta(hours=j*3),
                    meeting_place="池袋駅東口母子像前",
                    contact="interlink@interlink.com",
                    details="デモ用の未来のイベントです。",
                    host_user=host_user,
                    region=prefec_list[i%47],
                )
                demoevent.save()
                demoevent.admin = User.objects.filter(pk=i)

    def _create_frames(self):
        for event in Event.objects.all():
            frame = Frame(
                event=event,
                upper_limit=3,
                deadline=event.start_time,
            )
            frame.save()

            frame2 = Frame(
                event = event,
                deadline=event.start_time - timezone.timedelta(days=1),
                description='no_limit',
            )
            frame2.save()

            for i in range(1,30):
                event.supporter.add(User.objects.get(pk=i))

    def _create_participants(self):
        for event in Event.objects.all():
            frame = event.frame_set.get(description='no_limit')

            participation = Participation(
                event=event,
                frame=frame,
                user=User.objects.get(pk=1),
                status='管理者',
            )
            participation.save()

            for i in range(1,21):
                if event.pk%i==0:
                    user = User.objects.get(username=username_sample[i-1])
                    participation = Participation(
                        event=event,
                        frame=frame,
                        user=user,
                        status='参加中',
                    )
                    participation.save()


    def _create_comments(self):
        for event in Event.objects.all():
            for i,participation in enumerate(Participation.objects.filter(event=event)):
                comment = Comment(
                    event=event,
                    user=participation.user,
                    text=comment_sample[i%len(comment_sample)],
                )
                comment.save()

    def _create_groups(self):
        for i in range(20):
            name = groupname_sample[i]
            description = "完全非営利活動法人のボランティア団体です。詳しい団体説明はホームページをご覧ください。http://google.com"
            group = Group(
                name=name,
                description=description,
                )
            group.save()
            event = Event.objects.get(pk=group.pk)
            group.event.add(event)

    def _create_memberships(self):
        for group in Group.objects.all():
            for i in range(1,21):
                if group.pk in [1, 2] or group.pk==i:
                    member = User.objects.get(username=username_sample[i-1])
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
            '災害',
            '動物'
        )
        user = User.objects.get(pk=1)
        for t in taglist:
            tag = Tag(
                name=t,
            )
            tag.save()

        for user in User.objects.all():
            tag = Tag.objects.get(pk=(user.pk % len(taglist) + 1))
            user.follow_tag.add(tag)

        for event in Event.objects.all():
            for tag in Tag.objects.all():
                if event.pk/len(taglist)<=tag.pk:
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



