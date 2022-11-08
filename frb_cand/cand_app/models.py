from django.db import models

class FRBEvent(models.Model):
    id = models.AutoField(primary_key=True)
    tns_name = models.CharField(max_length=64, blank=True, null=True, help_text="The name of the FRB from the Transient naming system.")
    time_of_arrival = models.DateTimeField(blank=True, help_text="The time of arrival of the event as measured by the telescope in UTC")
    repeater = models.BooleanField(default=False, help_text="Is the FRB a repeater")

    # Images
    search_path    = models.FileField(upload_to="candidates/", max_length=1024, null=True)
    image_path     = models.FileField(upload_to="candidates/", max_length=1024, null=True)
    histogram_path = models.FileField(upload_to="candidates/", max_length=1024, null=True)

    class Meta:
        ordering = ['-id']


MB = 'MB'
HT = 'HT'
POS_SOURCE_CHOICES = (
    (MB, 'Multibeam'),
    (HT, 'High-time resolution pipleline'),
)

class RadioMeasurement(models.Model):
    frb = models.ForeignKey(
        FRBEvent,
        to_field="id",
        verbose_name="FRB Event",
        help_text="FRB event this position describes.",
        on_delete=models.CASCADE,
    )
    ra = models.FloatField(verbose_name="Right Acension (deg)")
    dec = models.FloatField(verbose_name="Declination (deg)")
    ra_hms  = models.CharField(max_length=64, verbose_name="Right Acension (HMS)")
    dec_dms = models.CharField(max_length=64, verbose_name="Declination (DMS)")
    ra_pos_error  = models.FloatField(verbose_name="Right Acension Error (deg)")
    dec_pos_error = models.FloatField(verbose_name="Declination Error (deg)")

    datetime = models.DateTimeField(auto_now_add=True, blank=True, help_text="The time that the measurement was uploaded (UTC).")
    source = models.CharField(max_length=3, choices=POS_SOURCE_CHOICES, help_text="The source (telescope pipeline) that was used to calculate the candidate position.")
    version = models.CharField(max_length=64, help_text='The version of the "source".')
    dm = models.FloatField(blank=True, null=True, verbose_name="Dispersion Measure (pc cm^-3)")
    dm_err = models.FloatField(blank=True, null=True, verbose_name="Dispersion Measure Error (pc cm^-3)")
    sn = models.FloatField(blank=True, null=True, verbose_name="Signal-to-noise Ratio")
    width = models.FloatField(blank=True, null=True, verbose_name="Width (ms)")
    z = models.FloatField(blank=True, null=True, verbose_name="Red Shift")
    rm = models.FloatField(blank=True, null=True, verbose_name="Rotation Measure (rad/m^2)")
    rm_err = models.FloatField(blank=True, null=True, verbose_name="Rotation Measure Error (rad/m^2)")
    fluence = models.FloatField(blank=True, null=True, verbose_name="Fluence (Jy ms)")
    fluence_err = models.FloatField(blank=True, null=True, verbose_name="Fluence Error (Jy ms)")
    flux = models.FloatField(blank=True, null=True, verbose_name="Flux Density (Jy)")
    flux_err = models.FloatField(blank=True, null=True, verbose_name="Flux Density Error (Jy)")


class SlackUser(models.Model):
    id = models.CharField(primary_key=True, max_length=24, verbose_name="Slack account ID")
    name = models.CharField(max_length=24, verbose_name="Slack account name")


class EventRating(models.Model):
    id = models.AutoField(primary_key=True)
    frb = models.ForeignKey(
        FRBEvent,
        to_field="id",
        verbose_name="FRB Event",
        help_text="FRB event this rating describes.",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        SlackUser,
        to_field="id",
        verbose_name="Slack user",
        help_text="Slack user that made this rating",
        on_delete=models.CASCADE,
    )
    datetime = models.DateTimeField(auto_now_add=True, blank=True)
    rating = models.BooleanField(default=False)
