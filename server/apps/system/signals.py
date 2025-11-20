
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import SystemConfig, Menu
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone


@receiver(post_save, sender=SystemConfig)
def broadcast_config_update(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "config_updates",
        {
            "type": "config_update",
            "message": {
                "id": instance.id,
                "key": instance.key,
                "value": instance.value,
                "action": "updated" if kwargs.get('created') is False else "created"
            }
        }
    )


def send_menu_update(action, menu_id=None):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "menu_updates",
        {
            "type": "menu.changed",  # 对应 consumer 中的方法名（下划线转点）
            "action": action,
            "menu_id": menu_id,
            "timestamp": timezone.now().isoformat(),
        }
    )


@receiver(post_save, sender=Menu)
def menu_post_save(sender, instance, created, **kwargs):
    action = 'create' if created else 'update'
    send_menu_update(action, instance.id)


@receiver(post_delete, sender=Menu)
def menu_post_delete(sender, instance, **kwargs):
    send_menu_update('delete', instance.id)
