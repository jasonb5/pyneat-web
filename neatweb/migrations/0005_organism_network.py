# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-08 09:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('neatweb', '0004_auto_20160308_0846'),
    ]

    operations = [
        migrations.AddField(
            model_name='organism',
            name='network',
            field=models.CharField(default='', max_length=256),
            preserve_default=False,
        ),
    ]