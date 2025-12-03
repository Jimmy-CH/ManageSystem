
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Event
from .tasks import analyze_fault_async
from .ai.faiss_store import FaissStore


# ========== 1. 新建故障 → 触发 AI 分析 ==========
@receiver(post_save, sender=Event)
def trigger_ai_analysis_on_new_event(sender, instance: Event, created: bool, **kwargs):
    """
    当新故障被创建时，异步触发 AI 根因分析。
    """
    if created:
        # 异步分析（非阻塞）
        analyze_fault_async.delay(instance.mal_id)


# ========== 2. 故障被标注（含根因+建议）→ 加入 FAISS ==========
@receiver(post_save, sender=Event)
def add_annotated_event_to_faiss(sender, instance: Event, created: bool, **kwargs):
    """
    当故障被人工或 AI 标注了根因和处理建议后，加入 FAISS 向量库。
    注意：此逻辑在 analyze_fault_async 执行完保存 ai_* 字段时也会触发。
    """
    # 只收录明确标注的样本
    if not (instance.ai_root_cause and instance.ai_suggestion):
        return

    # 防止在 analyze_fault_async 内部保存时反复调用（非必须，但安全）
    # 此处不做 created 判断，因为标注可能发生在创建之后（如人工修正）

    try:
        store = FaissStore()
        # 【可选】简单去重：检查是否已存在（基于 mal_id）
        existing_ids = {item["mal_id"] for item in store.meta}
        if instance.mal_id not in existing_ids:
            store.add_event(instance)
    except Exception as e:
        print(f"[FAISS] 添加故障 {instance.mal_id} 失败: {e}")


