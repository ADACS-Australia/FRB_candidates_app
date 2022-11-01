# Generated by Django 4.1.2 on 2022-10-20 03:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cand_app', '0003_position_datetime'),
    ]

    operations = [
        migrations.CreateModel(
            name='SlackUser',
            fields=[
                ('id', models.CharField(max_length=24, primary_key=True, serialize=False, verbose_name='Slack account ID')),
                ('name', models.CharField(max_length=24, verbose_name='Slack account name')),
            ],
        ),
        migrations.CreateModel(
            name='EventRating',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('rating', models.BooleanField(default=False)),
                ('frb', models.ForeignKey(help_text='FRB event this rating describes.', on_delete=django.db.models.deletion.CASCADE, to='cand_app.frbevent', verbose_name='FRB Event')),
                ('user', models.ForeignKey(help_text='Slack user that made this rating', on_delete=django.db.models.deletion.CASCADE, to='cand_app.slackuser', verbose_name='Slack user')),
            ],
        ),
    ]