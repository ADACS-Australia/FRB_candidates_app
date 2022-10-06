from django.db import models

class FRBEvent(models.Model):
    id = models.AutoField(primary_key=True)
    tns_name = models.CharField(max_length=64, blank=True, null=True, help_text="The name of the FRB from the Transient naming system.")
    dm = models.FloatField(blank=True, null=True, verbose_name="Dispersion Measure (pc cm^-3)")
    sn = models.FloatField(blank=True, null=True, verbose_name="Signal to noise ratio")
    width = models.FloatField(blank=True, null=True)

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

class Position(models.Model):
    frb = models.ForeignKey(
        FRBEvent,
        to_field="id",
        verbose_name="FRB Event",
        help_text="FRB event this position describes.",
        on_delete=models.CASCADE,
    )
    ra = models.FloatField()
    dec = models.FloatField()
    ra_hms = models.CharField(max_length=64)
    dec_dms = models.CharField(max_length=64)
    pos_error = models.FloatField()
    source = models.CharField(max_length=3, choices=POS_SOURCE_CHOICES, verbose_name="The source that was used to calculate the candidate position.")
