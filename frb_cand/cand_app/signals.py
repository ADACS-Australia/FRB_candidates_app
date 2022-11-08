from django.db.models.signals import post_save
from django.dispatch import receiver, Signal

from .models import FRBEvent, RadioMeasurement
from .views import slack_event_post, submit_frb_to_tns

import logging
logger = logging.getLogger(__name__)

@receiver(post_save, sender=FRBEvent)
def slack_trigger(sender, instance, **kwargs):
    """Each time an event is created, send a slack notification.
    """
    print(f"posting {instance.id}")
    slack_event_post(instance.id)

@receiver(post_save, sender=RadioMeasurement)
def tns_trigger(sender, instance, **kwargs):
    """Each time the first position is uploaded, send it to the Tranisent Name Server.
    """
    logger.debug(f"Checking {instance.frb}")
    frb_mes = RadioMeasurement.objects.filter(frb=instance.frb)
    if len(frb_mes) == 1:
        # This is the first postion so upload it
        tns_name = submit_frb_to_tns(instance.frb.id)
        print(f"tns_name: {tns_name}")
        # Grab FRB event and update TNS name
        # do it this way to prevent a save triggering another slack trigger
        FRBEvent.objects.filter(id=instance.frb.id).update(tns_name=tns_name)