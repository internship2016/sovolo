# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-17 22:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0022_userreviewlist_joined_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='userreviewlist',
            name='post_day',
            field=models.DateTimeField(editable=False, null=True),
        ),
    ]
