# coding=utf-8
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.urlresolvers import reverse
from django.conf import settings
from django.apps import apps

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext

from datetime import datetime
from django.utils import timezone

from tag.models import Tag
from base.models import AbstractBaseModel

import os
import math

# review
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg


class UserManager(BaseUserManager):
    def create_user(self, email="", username="", password=None):
        user = self.model(
            username=username,
            email=self.normalize_email(email)
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(email, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user


# FIXME: Remove 'get_' prefixes, this is bad/meaningless/Java-ish habits
class User(AbstractBaseModel, AbstractBaseUser):
    # Numbers are arbitrary
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    username = models.CharField(max_length=100, null=True, unique=True)
    birthday = models.DateField(null=True, blank=True)
    telephone = models.CharField(max_length=11, null=True)
    emergency_contact = models.CharField(max_length=11, null=True)
    email = models.EmailField(unique=True, db_index=True)
    sex = models.NullBooleanField()  # True:Men, False:Women
    occupation = models.CharField(max_length=100, null=True)
    # regionは都道府県で指定
    # XXX: dup
    prefectures = settings.PREFECTURES
    prefs = prefectures.items()
    prefs = sorted(prefs, key=lambda x: x[1][1])
    region_list = [(k, v[0]) for k, v in prefs]

    region = models.CharField(max_length=10, choices=region_list)

    follow_tag = models.ManyToManyField(Tag,
                                        related_name='follower',
                                        blank=True)

    image = models.ImageField(upload_to='users/', null=True, blank=True)
    objects = UserManager()
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    language = models.CharField(verbose_name=_('Language'),
                                max_length=10,
                                choices=settings.LANGUAGES,
                                default=settings.LANGUAGE_CODE,  # FIXME: !!
                                null=True)

    # helper or sufferer
    role = models.CharField(blank=True,
                            null=True,
                            max_length=15,
                            default='helper')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # XXX: Nuts, poor django template engine doesn't allow spaces in args
    def msg_you_need_more_xxx_sovolage_to_the_next_level(self):
        points_to_next = self.get_points_to_next_level()
        return ungettext(
            "You need %(points_to_next)d more Sovolage to the next level!",
            "You need %(points_to_next)d more Sovolages to the next level!",
            points_to_next
        ) % {"points_to_next": points_to_next}

    def get_about_age(self):
        today = datetime.today()
        birthday = self.birthday
        age = today.year - birthday.year

        if (today.month, today.day) <= (birthday.month, birthday.day):
            age -= 1

        return math.floor(age / 10) * 10

    def is_manager_for(self, event):
        if event in self.admin_event.all():
            return True

        if event in self.host_event.all():
            return True

        return False

    def get_point(self):
        return self.participating_event \
                   .filter(supporter__isnull=False) \
                   .values_list('supporter', flat=True) \
                   .count()

    def get_level(self):
        point = self.get_point()
        level = 1

        # FIXME: Deterministic, this shouldn't be using while statement
        while(self.is_level(level, point)):
            level += 1

        return level

    def level_threshold(self, level):
        # 有効数字2桁
        base = 1.08
        tmp = 10 * math.pow(base, level)
        digit = int(math.log10(tmp)) + 1

        return int(round(tmp, -digit + 2))

    def is_level(self, level, point):
        return self.level_threshold(level) <= point

    def get_points_to_next_level(self):
        return self.level_threshold(self.get_level()) - self.get_point()

    def get_level_percentage(self):
        point = float(self.get_point())
        threshold = float(self.level_threshold(self.get_level()))
        return math.floor(point * 100 / threshold)

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def admin_group(self):
        return self.group_set.filter(membership__role='admin')

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        return self.is_admin

    def get_absolute_url(self):
        return reverse('user:detail', kwargs={'pk': self.id})

    def __str__(self):
        return self.email

    def get_image_url(self):
        if self.image:
            return self.image.url
        else:
            return os.path.join(settings.MEDIA_URL,
                                'users/',  # FIXME: trailing slash?
                                "default_user_image.png")

    def save(self, *args, **kwargs):
        return super(User, self).save(*args, **kwargs)

    def get_region_kanji(self):
        region = self.prefectures.get(self.region)
        if not region:
            return '未設定'  # XXX: regionがこない場合は未設定でいいのか
        return region[0]

    def get_new_group_events(self):
        Event = apps.get_model('event', 'Event')
        group_list = self.group_set.all()

        return Event.objects \
                    .filter(group__in=group_list) \
                    .distinct() \
                    .order_by('-created')[:5]

    def get_new_region_events(self):
        Event = apps.get_model('event', 'Event')

        events = Event.objects \
                      .filter(region=self.region) \
                      .distinct() \
                      .order_by('-created')

        # TODO: Consider using 'filter()' to return an iterator
        return [event for event in events if not event.is_over()]

    def get_future_participating_events(self):
        events = self.participating_event \
                     .all() \
                     .order_by('start_time')
        return [event for event in events if not event.is_over()]

    def get_past_participated_events(self):
        events = self.participating_event \
                     .all() \
                     .order_by('start_time')
        return [event for event in events if event.is_over()]

    def get_new_tag_events(self):
        Event = apps.get_model('event', 'Event')
        tag_list = self.follow_tag.all()

        return Event.objects \
                    .filter(tag__in=tag_list) \
                    .distinct() \
                    .order_by('-created')[:5]

    def trophy_list(self):
        date = timezone.now()
        participated = self.participating_event \
                           .all() \
                           .filter(end_time__lte=date)

        trophies = []
        for tag in Tag.objects.all():
            count = participated.filter(tag=tag).count()
            if count >= 20:
                trophies.append({'name': tag.name, 'type': 'master'})
            elif count >= 10:
                trophies.append({'name': tag.name, 'type': 'senior'})
            elif count >= 3:
                trophies.append({'name': tag.name, 'type': 'beginner'})
            elif count >= 1:
                trophies.append({'name': tag.name, 'type': 'rookie'})

        return trophies

    # Review (using by participant)
    def get_mean_rating(self):
        avg_rate = self.to_rate_user.aggregate(Avg('rating'))['rating__avg']

        # FIXME: avg_rate might be None
        if avg_rate is None:
            return avg_rate

        return round(avg_rate, 2)

    def get_reviewed_events(self):
        return [event.joined_event for event in self.from_rate_user.all()]

    def get_past_participated_and_unreviewed_events(self):
        participating_events = self.participating_event.all()
        finished = [e for e in participating_events if e.is_over()]
        reviewed = [e.id for e in self.get_reviewed_events()]
        unreviewed = [e for e in finished if e.id not in reviewed]
        return unreviewed

    # Review (using by host)
    def get_past_hosted_events(self):
        host_events = self.host_event.all().order_by('start_time')
        return [e for e in host_events if e.is_over()]

    def get_participant_of_past_hosted_events(self):
        user_reviewed_list = []
        for event in self.get_past_hosted_events():
            users = [p.user for p in event.participation_set.all()]
            user_reviewed_list.append(users)
        return user_reviewed_list

    def get_reviewed_participant_of_past_hosted_events(self):
        user_reviewed_list = []
        for event in self.get_past_hosted_events():
            reviews = self.from_rate_user.all()

            users = [r.to_rate_user for r
                     in reviews
                     if r.joined_event == event]

            user_reviewed_list.append(users)
        return user_reviewed_list

    def get_unreviewed_participant_of_past_hosted_events(self):
        user_unreviewed_list = []

        zipped = zip(self.get_participant_of_past_hosted_events(),
                     self.get_reviewed_participant_of_past_hosted_events())

        for user_list_all, user_list_re in zipped:
            temp = [user for user in user_list_all if user not in user_list_re]
            user_unreviewed_list.append(temp)

        return user_unreviewed_list

    # pop Null
    def get_unreviewed_past_hosted_events(self):
        user_unreviewed_list = []

        zipped = zip(self.get_past_hosted_events(),
                     self.get_unreviewed_participant_of_past_hosted_events())

        for event, unreviewed in zipped:
            if len(unreviewed) == 0:
                continue
            user_unreviewed_list.append(event)

        return user_unreviewed_list

    def get_unreviewed_participant_of_past_hosted_events_poped(self):
        user_unreviewed_list = []
        events = self.get_unreviewed_participant_of_past_hosted_events()
        for user_list in events:
            if len(user_list) == 0:
                continue
            user_unreviewed_list.append(user_list)
        return user_unreviewed_list

    # send html template
    def get_zipped_unreviewed_hosted(self):
        return zip(self.get_unreviewed_past_hosted_events(),
                   self.get_unreviewed_participant_of_past_hosted_events_poped())

    # for Notification
    def get_unreview_num_for_participant(self):
        return len(self.get_past_participated_and_unreviewed_events())

    def get_unreview_num_for_host(self):
        num = 0
        for user_list in self.get_unreviewed_participant_of_past_hosted_events_poped():
            num += len(user_list)
        return num

    def get_unreview_list(self):
        """Get Unreview List.
        ログインしているユーザーの未レビューの最新５件を返す。
        """
        back_num = 5

        res_obj = []

        if self.role == 'helper':
            unreview_events = self.get_past_participated_and_unreviewed_events()
            for event in unreview_events[:back_num]:
                res_obj.append({
                    'event_id': event.id,
                    'event_name': event.name,
                    'event_host': event.host_user,
                    'event_img': event.get_image_url(),
                    'message': event.name + 'へのレビューをおねがいします。'
                })

        else:
            counter = 0

            # XXX: Bad method name: zip(event, user_list)
            unreview_events = self.get_zipped_unreviewed_hosted()

            for event, user_list in unreview_events:
                if counter >= back_num:
                    break

                for h_user in user_list:
                    if counter >= back_num:
                        break
                    res_obj.append({
                        'event_id': event.id,
                        'event_name': event.name,
                        'event_host': event.host_user,
                        'event_img': event.get_image_url(),
                        'helper_name': h_user.username,
                        'helper_id': h_user.pk,
                        'helper_img': h_user.get_image_url(),
                        'message': h_user.username + 'さんへのレビューをおねがいします。'
                    })
                    counter += 1

        return res_obj


class UserActivation(models.Model):
    user = models.OneToOneField(User)
    key = models.CharField(max_length=255, unique=True)
    created = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        return super().save(*args, **kwargs)


class UserPasswordResetting(models.Model):
    user = models.OneToOneField(User)
    key = models.CharField(max_length=255, unique=True)
    created = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        return super().save(*args, **kwargs)


class UserReviewList(models.Model):

    RATE_CHOICES = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5')
    ]

    to_rate_user = models.ForeignKey(User,
                                     on_delete=models.CASCADE,
                                     related_name='to_rate_user')

    from_rate_user = models.ForeignKey(User,
                                       on_delete=models.CASCADE,
                                       related_name='from_rate_user')

    rating = models.IntegerField(choices=RATE_CHOICES,
                                 validators=[MinValueValidator(0),
                                             MaxValueValidator(5)],
                                 default=3)

    comment = models.CharField(max_length=200, null=True, blank=True)

    joined_event = models.ForeignKey('event.Event')

    post_day = models.DateTimeField(default=timezone.now)

    from_event_host = models.NullBooleanField(default=False)

    def __str__(self):
        # Built-in attribute of django.contrib.auth.models.User !
        return str(self.to_rate_user)


class Skill(AbstractBaseModel):
    userskill = models.ForeignKey(User, on_delete=models.CASCADE)
    tag = models.ManyToManyField(Tag)
    skilltodo = models.CharField(max_length=200, null=True)

    def __str__(self):
        return "Skill #" + str(self.pk) + " in User #" + str(self.userskill_id)

    def get_tags_as_string(self):
        return "\n".join([tag.name for tag in self.tag.all()])

    def get_absolute_url(self):
        return reverse('user:detail', kwargs={'pk': self.id})
