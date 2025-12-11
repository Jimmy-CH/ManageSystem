
from .ai_engine import find_similar_events
from thirds.dingtalk import ding
from apps.faults.models import Event


def analyze_and_notify(event_id):
    """
    对新创建的 Event 进行 AI 分析，并推送钉钉消息
    """
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return

    similar_events = find_similar_events(event, top_k=3)

    if similar_events:
        best_match = similar_events[0][0]
        ai_root_cause = best_match.mal_reason[:256]
        ai_suggestion = best_match.solution or "参考历史处理方案"
        ai_confidence = round(similar_events[0][1] * 100, 2)  # 转为百分比
    else:
        ai_root_cause = "未匹配到相似故障"
        ai_suggestion = "建议人工介入分析"
        ai_confidence = 0.0

    # 保存 AI 分析结果（可选：只在为空时写入，避免覆盖人工修改）
    if not event.ai_root_cause:
        event.ai_root_cause = ai_root_cause
        event.ai_suggestion = ai_suggestion
        event.ai_confidence = ai_confidence

        # 可选：生成 embedding（此处留空，实际可用 sentence-transformers）
        # event.embedding = generate_embedding(event.description or "")

        event.save(update_fields=['ai_root_cause', 'ai_suggestion', 'ai_confidence', 'embedding'])

    # 推送钉钉
    message = f"""
📌 **故障智能分析提醒**

- 故障ID：{event.mal_id}
- 登记人：{event.registrant}
- 摘要：{event.description[:100] if event.description else '无'}
- 🔍 AI初步根因：{ai_root_cause}
- 💡 处理建议：{ai_suggestion}
- 📊 置信度：{ai_confidence}%
    """.strip()

    ding.send_text_message(recipient_id=event.registrant, content=message)

