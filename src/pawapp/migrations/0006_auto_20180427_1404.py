# Generated by Django 2.0.3 on 2018-04-27 14:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pawapp', '0005_auto_20180425_1337'),
    ]

    operations = [
        migrations.RenameField(
            model_name='billitem',
            old_name='from_time',
            new_name='from_datetime',
        ),
        migrations.RenameField(
            model_name='billitem',
            old_name='to_time',
            new_name='to_datetime',
        ),
    ]