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

    # Q/A cache
    def get_answer(self, key: str):
        if self.use_redis:
            return self.client.get(f"qa:{key}")
        return _memory_cache.get(f"qa:{key}")

    def set_answer(self, key: str, value: str):
        if self.use_redis:
            self.client.set(f"qa:{key}", value, ex=3600)
        else:
            _memory_cache[f"qa:{key}"] = value

    # Conversation memory (last 10 turns)
    def get_history(self, session_id: str):
        if self.use_redis:
            data = self.client.lrange(f"history:{session_id}", 0, -1)
            return [json.loads(d) for d in data]
        return _memory_history.get(session_id, [])

    def add_to_history(self, session_id: str, role: str, content: str):
        item = json.dumps({"role": role, "content": content})
        if self.use_redis:
            self.client.rpush(f"history:{session_id}", item)
            self.client.ltrim(f"history:{session_id}", -20, -1)  # keep last 20 msgs (10 turns)
        else:
            history = _memory_history.get(session_id, [])
            history.append({"role": role, "content": content})
            _memory_history[session_id] = history[-20:]

    def clear_history(self, session_id: str):
        if self.use_redis:
            self.client.delete(f"history:{session_id}")
        else:
            _memory_history.pop(session_id, None)
