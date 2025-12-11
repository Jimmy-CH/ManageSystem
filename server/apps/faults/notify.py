
import requests
from django.conf import settings


def send_dingtalk_message(title: str, text: str):
    webhook = getattr(settings, "DINGTALK_WEBHOOK", None)
    if not webhook:
        return
    msg = {"msgtype": "markdown", "markdown": {"title": title, "text": text}}
    requests.post(webhook, json=msg, timeout=5)


def send_fault_analysis_notification(event, analysis_result):
    text = f"""
### 故障ID: {event.mal_id}
- **分类**: {event.first_level} / {event.third_level}
- **描述**: {event.description[:100]}...
- **AI 初步根因**: {analysis_result['root_cause']}
- **置信度**: {analysis_result['confidence']:.0%}
- **建议**: {analysis_result['suggestion']}
- **来源**: {analysis_result['source']}
    """.strip()
    send_dingtalk_message("【星辰】故障智能分析提醒", text)

