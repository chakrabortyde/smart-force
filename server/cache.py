import os
import json
import redis

# In-memory fallback
_memory_cache = {}
_memory_history = {}

class CacheManager:
    def __init__(self, redis_url="redis://localhost:6379/0"):
        self.use_redis = False
        try:
            self.client = redis.Redis.from_url(redis_url, decode_responses=True)
            self.client.ping()
            self.use_redis = True
            print("✅ Redis connected.")
        except Exception:
            print("⚠️ Redis not available, using in-memory cache.")

    # ---------------- Q/A CACHE ----------------
    def get_answer(self, key: str):
        raw = None
        if self.use_redis:
            raw = self.client.get(f"qa:{key}")
        else:
            raw = _memory_cache.get(f"qa:{key}")
        return json.loads(raw) if raw else None

    def set_answer(self, key: str, answer: str, sources: list[str]):
        value = json.dumps({"answer": answer, "sources": sources})
        if self.use_redis:
            self.client.set(f"qa:{key}", value, ex=3600)
        else:
            _memory_cache[f"qa:{key}"] = value

    def has_answer(self, key: str) -> bool:
        if self.use_redis:
            return self.client.exists(f"qa:{key}") > 0
        return f"qa:{key}" in _memory_cache

    # ---------------- CONVERSATION HISTORY ----------------
    def get_history(self, session_id: str):
        """Return the last 10 turns as [{'user':..., 'assistant':..., 'sources': [...]}, ...]"""
        raw_messages = []
        if self.use_redis:
            raw_messages = self.client.lrange(f"history:{session_id}", -40, -1)
            history = [json.loads(m) for m in raw_messages]
        else:
            history = _memory_history.get(session_id, [])

        # Pair user + assistant into turns
        turns = []
        for i in range(0, len(history) - 1, 2):
            if history[i]["role"] == "user" and history[i+1]["role"] == "assistant":
                turns.append({
                    "user": history[i]["content"],
                    "assistant": history[i+1]["content"],
                    "sources": history[i+1].get("sources", [])
                })

        return turns[-10:]  # keep only last 10 turns

    def add_to_history(self, session_id: str, role: str, content: str, sources: list[str] = None):
        """Store a message in history. Sources only apply to assistant."""
        entry = {"role": role, "content": content}
        if role == "assistant" and sources:
            entry["sources"] = sources

        item = json.dumps(entry)
        if self.use_redis:
            self.client.rpush(f"history:{session_id}", item)
            self.client.ltrim(f"history:{session_id}", -40, -1)  # 20 messages = 10 turns
        else:
            history = _memory_history.get(session_id, [])
            history.append(entry)
            _memory_history[session_id] = history[-40:]

    def clear_history(self, session_id: str):
        if self.use_redis:
            self.client.delete(f"history:{session_id}")
        else:
            _memory_history.pop(session_id, None)
