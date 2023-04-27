# -*- coding: utf-8 -*-
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exact', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='session',
            name='division',
        ),
    ]
