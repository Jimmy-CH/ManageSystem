
from celery import shared_task
from .rules.engine import apply_rules_to_event
from .ai.faiss_store import FaissStore
from .notify import send_fault_analysis_notification
from .models import Event


@shared_task
def analyze_fault_async(mal_id: str):
    try:
        event = Event.objects.get(mal_id=mal_id)

        # 1. 规则匹配
        result = apply_rules_to_event(event)

        # 2. FAISS 相似检索（若规则未命中）
        if result is None:
            store = FaissStore()
            similar = store.search_by_event(event, top_k=1)
            if similar:
                best = similar[0]
                result = {
                    "source": "ai_similarity",
                    "root_cause": best["root_cause"],
                    "suggestion": best["suggestion"],
                    "confidence": best["score"]
                }

        # 3. 兜底
        if result is None:
            result = {
                "source": "fallback",
                "root_cause": "未知原因",
                "suggestion": "建议人工介入排查。",
                "confidence": 0.5
            }

        # 4. 保存结果 & 向量
        from .ai.embedder import embed_event_text
        event.ai_root_cause = result["root_cause"]
        event.ai_suggestion = result["suggestion"]
        event.ai_confidence = result["confidence"]
        event.embedding = embed_event_text(event)
        event.save(update_fields=["ai_root_cause", "ai_suggestion", "ai_confidence", "embedding"])

        # 5. 推送通知
        send_fault_analysis_notification(event, result)

        # 6. 更新 FAISS（如果是高质量样本，可选）
        # 此处暂不自动加入，需人工确认后才加入（避免噪声）
        # 若需自动加入，可调用 store.add_event(event)

    except Exception as e:
        print(f"AI 分析故障 {mal_id} 失败: {e}")

