# Generated by Django 4.1.2 on 2022-11-08 03:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cand_app', '0004_slackuser_eventrating'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Position',
            new_name='RadioMeasurement',
        ),
    ]