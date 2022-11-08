# Generated by Django 4.1.2 on 2022-11-08 03:34

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('cand_app', '0005_rename_position_radiomeasurement'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='frbevent',
            name='dm',
        ),
        migrations.RemoveField(
            model_name='frbevent',
            name='sn',
        ),
        migrations.RemoveField(
            model_name='frbevent',
            name='width',
        ),
        migrations.AddField(
            model_name='frbevent',
            name='repeater',
            field=models.BooleanField(default=False, help_text='Is the FRB a repeater'),
        ),
        migrations.AddField(
            model_name='frbevent',
            name='time_of_arrival',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, help_text='The time of arrival of the event as measured by the telescope in UTC'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='radiomeasurement',
            name='dm',
            field=models.FloatField(blank=True, null=True, verbose_name='Dispersion Measure (pc cm^-3)'),
        ),
        migrations.AddField(
            model_name='radiomeasurement',
            name='dm_err',
            field=models.FloatField(blank=True, null=True, verbose_name='Dispersion Measure Error (pc cm^-3)'),
        ),
        migrations.AddField(
            model_name='radiomeasurement',
            name='rm',
            field=models.FloatField(blank=True, null=True, verbose_name='Rotation Measure (rad/m^2)'),
        ),
        migrations.AddField(
            model_name='radiomeasurement',
            name='rm_err',
            field=models.FloatField(blank=True, null=True, verbose_name='Rotation Measure Error (rad/m^2)'),
        ),
        migrations.AddField(
            model_name='radiomeasurement',
            name='sn',
            field=models.FloatField(blank=True, null=True, verbose_name='Signal-to-noise Ratio'),
        ),
        migrations.AddField(
            model_name='radiomeasurement',
            name='version',
            field=models.CharField(default='v1', help_text='The version of the "source".', max_length=64),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='radiomeasurement',
            name='width',
            field=models.FloatField(blank=True, null=True, verbose_name='Width (ms)'),
        ),
        migrations.AddField(
            model_name='radiomeasurement',
            name='z',
            field=models.FloatField(blank=True, null=True, verbose_name='Red Shift'),
        ),
        migrations.AlterField(
            model_name='radiomeasurement',
            name='datetime',
            field=models.DateTimeField(auto_now_add=True, help_text='The time that the measurement was uploaded (UTC).'),
        ),
        migrations.AlterField(
            model_name='radiomeasurement',
            name='dec',
            field=models.FloatField(verbose_name='Declination (deg)'),
        ),
        migrations.AlterField(
            model_name='radiomeasurement',
            name='dec_dms',
            field=models.CharField(max_length=64, verbose_name='Declination (DMS)'),
        ),
        migrations.AlterField(
            model_name='radiomeasurement',
            name='dec_pos_error',
            field=models.FloatField(verbose_name='Declination Error (deg)'),
        ),
        migrations.AlterField(
            model_name='radiomeasurement',
            name='ra',
            field=models.FloatField(verbose_name='Right Acension (deg)'),
        ),
        migrations.AlterField(
            model_name='radiomeasurement',
            name='ra_hms',
            field=models.CharField(max_length=64, verbose_name='Right Acension (HMS)'),
        ),
        migrations.AlterField(
            model_name='radiomeasurement',
            name='ra_pos_error',
            field=models.FloatField(verbose_name='Right Acension Error (deg)'),
        ),
        migrations.AlterField(
            model_name='radiomeasurement',
            name='source',
            field=models.CharField(choices=[('MB', 'Multibeam'), ('HT', 'High-time resolution pipleline')], help_text='The source (telescope pipeline) that was used to calculate the candidate position.', max_length=3),
        ),
    ]