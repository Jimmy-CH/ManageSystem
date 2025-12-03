# ai_engine.py

from django.db.models import Q
from apps.faults.models import Event, EventDeviceInfo
import jieba
from collections import Counter


def extract_keywords(text):
    """简单关键词提取（可替换为 NLP 模型）"""
    return set(jieba.cut_for_search(text))


def find_similar_events(new_event: Event, top_k=3):
    """
    基于分类、部件、描述关键词匹配历史事件
    返回 [(event, score), ...]
    """
    # 构建基础查询条件：相同分类层级
    base_q = Q(
        first_level=new_event.first_level,
        subdivision=new_event.subdivision,
        third_level=new_event.third_level,
        fourth_level=new_event.fourth_level,
        level=new_event.level,
        mal_result__in=[3, 5]  # 已结束或历史事件
    )

    # 获取新事件的关键词
    desc_keywords = extract_keywords(new_event.description or "")
    reason_keywords = extract_keywords(new_event.mal_reason or "")
    all_keywords = desc_keywords | reason_keywords

    if not all_keywords:
        return []

    # 获取所有满足基础条件的历史事件
    candidates = Event.objects.filter(base_q).exclude(mal_id=new_event.mal_id)

    scored_events = []
    for ev in candidates:
        ev_keywords = extract_keywords(ev.description or "") | extract_keywords(ev.mal_reason or "")
        overlap = len(all_keywords & ev_keywords)
        if overlap > 0:
            score = overlap / len(all_keywords)  # 简单 Jaccard 相似度
            scored_events.append((ev, score))

    # 按分数降序
    scored_events.sort(key=lambda x: x[1], reverse=True)
    return scored_events[:top_k]

