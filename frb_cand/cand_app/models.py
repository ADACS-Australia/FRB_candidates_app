from django.db import models


class Observation(models.Model):
    id = models.AutoField(primary_key=True)
    beam_semi_major_axis = models.FloatField(verbose_name='Beam Semi-major Axis (arcminutes)')
    beam_semi_minor_axis = models.FloatField(verbose_name='Beam Semi-minor Axis (arcminutes)')
    beam_rotation_angle = models.FloatField(verbose_name='Beam Rotation Angle (degrees)')
    sampling_time = models.FloatField(verbose_name='Sampling Time (ms)')
    bandwidth = models.FloatField(verbose_name='Bandwidth (MHz)')
    nchan = models.IntegerField(verbose_name='nchan')
    centre_frequency = models.FloatField(verbose_name='Centre Frequency (MHz)')
    npol = models.IntegerField(verbose_name='npol')
    bits_per_sample = models.IntegerField(verbose_name='Bits Per Sample')
    gain = models.FloatField(verbose_name='Gain (K/Jy)')
    tsys = models.FloatField(verbose_name='Tsys (K)')
    backend = models.CharField(verbose_name='Backend', max_length=128)
    beam = models.IntegerField(
        blank=True, null=True,
        verbose_name='Beam Number',
        help_text='Detection beam number if backend is a multi beam receiver'
    )


class FRBEvent(models.Model):
    id = models.AutoField(primary_key=True)
    observation = models.ForeignKey(
        Observation,
        to_field="id",
        verbose_name="Observation",
        help_text="Observation that this FRB event was detected in.",
        on_delete=models.CASCADE,
    )
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
    id = models.AutoField(primary_key=True)
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
    gl = models.FloatField(verbose_name="Galactic Longitude (deg)")
    gb = models.FloatField(verbose_name="Galactic Latitude (deg)")

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


class VOEvent(models.Model):
    id = models.AutoField(primary_key=True)
    radio_measurement = models.ForeignKey(
        RadioMeasurement,
        to_field="id",
        verbose_name="FRB Radio Measurement",
        help_text="The measurement that created this VOEvent",
        on_delete=models.CASCADE,
    )
    xml_packet = models.CharField(max_length=10000)
    comet_log  = models.CharField(max_length=10000)
