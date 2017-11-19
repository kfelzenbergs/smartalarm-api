# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-11-19 13:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smartalarm_api', '0008_auto_20171109_1540'),
    ]

    operations = [
        migrations.AddField(
            model_name='tracker',
            name='tracker_type',
            field=models.CharField(choices=[('owl', 'Owl'), ('coban', 'Coban')], default='unknown', max_length=100),
        ),
    ]