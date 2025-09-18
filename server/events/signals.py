
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone


def handle_incident_update(instance, is_responded, is_resolved):
    channel_layer = get_channel_layer()

    if is_responded:
        target_users = {instance.reporter.id}
        if instance.assignee:
            target_users.add(instance.assignee.id)
        message = f"🛎️ 事件「{instance.title}」已被响应"
        action = "responded"

        for uid in target_users:
            if uid:
                async_to_sync(channel_layer.group_send)(
                    f"user_{uid}",
                    {
                        "type": "send_notification",
                        "message": message,
                        "incident_id": instance.id,
                        "action": action,
                        "timestamp": timezone.now().isoformat(),
                    }
                )

    elif is_resolved:
        target_users = {instance.reporter.id}
        if instance.assignee:
            target_users.add(instance.assignee.id)
        message = f"✅ 事件「{instance.title}」已解决"
        action = "resolved"

        for uid in target_users:
            if uid:
                async_to_sync(channel_layer.group_send)(
                    f"user_{uid}",
                    {
                        "type": "send_notification",
                        "message": message,
                        "incident_id": instance.id,
                        "action": action,
                        "timestamp": timezone.now().isoformat(),
                    }
                )
