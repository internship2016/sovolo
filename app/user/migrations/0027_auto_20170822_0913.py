# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-22 00:13
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0026_auto_20170819_0854'),
    ]

    operations = [
        migrations.AlterField(
            model_name='skill',
            name='admin',
            field=models.ManyToManyField(blank=True, related_name='admin_skill', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='skill',
            name='userskill',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
