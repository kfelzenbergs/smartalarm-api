# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-12-03 00:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('smartalarm_api', '0012_auto_20171202_1910'),
    ]

    operations = [
        migrations.RenameField(
            model_name='globalstat',
            old_name='update_time',
            new_name='updated_at',
        ),
        migrations.RenameField(
            model_name='trackerevent',
            old_name='update_time',
            new_name='updated_at',
        ),
        migrations.RenameField(
            model_name='trackerstat',
            old_name='update_time',
            new_name='updated_at',
        ),
        migrations.RenameField(
            model_name='trip',
            old_name='update_time',
            new_name='updated_at',
        ),
        migrations.RenameField(
            model_name='zone',
            old_name='update_time',
            new_name='updated_at',
        ),
        migrations.RemoveField(
            model_name='tripstat',
            name='created',
        ),
        migrations.AddField(
            model_name='trip',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='trip',
            name='time_end',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='trip',
            name='time_start',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='tripstat',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
