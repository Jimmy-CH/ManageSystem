
import os
import faiss
import numpy as np
import pickle
from django.conf import settings

FAISS_INDEX_PATH = getattr(settings, "FAISS_INDEX_PATH", "data/faiss_index.bin")
FAISS_META_PATH = getattr(settings, "FAISS_META_PATH", "data/faiss_meta.pkl")
os.makedirs(os.path.dirname(FAISS_INDEX_PATH), exist_ok=True)


class FaissStore:
    def __init__(self):
        self.dim = 384
        self.index = None
        self.meta = []
        self._load()

    def _load(self):
        if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(FAISS_META_PATH):
            self.index = faiss.read_index(FAISS_INDEX_PATH)
            with open(FAISS_META_PATH, "rb") as f:
                self.meta = pickle.load(f)
        else:
            self.index = faiss.IndexFlatIP(self.dim)
            self.meta = []

    def add_event(self, event):
        if not (event.ai_root_cause and event.ai_suggestion):
            return
        from .embedder import embed_event_text
        vec = np.array(embed_event_text(event)).astype("float32")
        faiss.normalize_L2(vec)
        vec = vec.reshape(1, -1)
        self.index.add(vec)
        self.meta.append({
            "mal_id": event.mal_id,
            "root_cause": event.ai_root_cause,
            "suggestion": event.ai_suggestion,
        })
        self._save()

    def search_by_event(self, event, top_k=3, min_score=0.7):
        from .embedder import embed_event_text
        query_vec = np.array(embed_event_text(event)).astype("float32")
        faiss.normalize_L2(query_vec)
        query_vec = query_vec.reshape(1, -1)
        D, I = self.index.search(query_vec, top_k)
        results = []
        for score, idx in zip(D[0], I[0]):
            if idx == -1 or score < min_score:
                continue
            meta = self.meta[idx]
            results.append({
                "score": float(score),
                "root_cause": meta["root_cause"],
                "suggestion": meta["suggestion"],
            })
        return results

    def _save(self):
        faiss.write_index(self.index, FAISS_INDEX_PATH)
        with open(FAISS_META_PATH, "wb") as f:
            pickle.dump(self.meta, f)



