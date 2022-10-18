from django.db.models.signals import post_save
from django.dispatch import receiver, Signal

from .models import FRBEvent
from .views import slack_event_post

@receiver(post_save, sender=FRBEvent)
def group_trigger(sender, instance, **kwargs):
    """Each time an event is created, send a slack notification.
    """
    print(f"posting {instance.id}")
    slack_event_post(instance.id)