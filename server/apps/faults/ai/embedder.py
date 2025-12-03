from sentence_transformers import SentenceTransformer

_model = None


def get_embedder():
    global _model
    if _model is None:
        _model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    return _model


def embed_event_text(event) -> list:
    """将故障描述文本向量化"""
    text = " ".join([
        event.first_level or "",
        event.third_level or "",
        event.mal_reason or "",
        event.description or "",
    ]).strip()
    if not text:
        text = "无描述"
    model = get_embedder()
    vec = model.encode(text, convert_to_numpy=False)
    return vec.tolist()


