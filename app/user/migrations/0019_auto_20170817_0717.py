# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-16 22:17
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0018_auto_20170817_0613'),
    ]

    operations = [
        migrations.AddField(
            model_name='frame',
            name='admin',
            field=models.ManyToManyField(blank=True, related_name='admin_frame', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='user',
            name='region',
            field=models.CharField(choices=[('Hokkaido', 'Hokkaido'), ('Aomori', 'Aomori'), ('Iwate', 'Iwate'), ('Miyagi', 'Miyagi'), ('Akita', 'Akita'), ('Yamagata', 'Yamagata'), ('Fukushima', 'Fukushima'), ('Ibaraki', 'Ibaraki'), ('Tochigi', 'Tochigi'), ('Gunnma', 'Gunnma'), ('Saitama', 'Saitama'), ('Chiba', 'Chiba'), ('Tokyo', 'Tokyo'), ('Kanagawa', 'Kanagawa'), ('Niigata', 'Niigata'), ('Toyama', 'Toyama'), ('Ishikawa', 'Ishikawa'), ('Fukui', 'Fukui'), ('Yamanashi', 'Yamanashi'), ('Nagano', 'Nagano'), ('Gifu', 'Gifu'), ('Shizuoka', 'Shizuoka'), ('Aichi', 'Aichi'), ('Mie', 'Mie'), ('Shiga', 'Shiga'), ('Kyoto', 'Kyoto'), ('Osaka', 'Osaka'), ('Hyogo', 'Hyogo'), ('Nara', 'Nara'), ('Wakayama', 'Wakayama'), ('Tottori', 'Tottori'), ('Shimane', 'Shimane'), ('Okayama', 'Okayama'), ('Hiroshima', 'Hiroshima'), ('Yamaguchi', 'Yamaguchi'), ('Tokushima', 'Tokushima'), ('Kagawa', 'Kagawa'), ('Ehime', 'Ehime'), ('Kouchi', 'Kouchi'), ('Fukuoka', 'Fukuoka'), ('Saga', 'Saga'), ('Nagasaki', 'Nagasaki'), ('Kumamoto', 'Kumamoto'), ('Ooita', 'Ooita'), ('Miyazaki', 'Miyazaki'), ('Kagoshima', 'Kagoshima'), ('Okinawa', 'Okinawa')], max_length=10),
        ),
    ]