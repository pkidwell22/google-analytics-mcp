# analytics_mcp/utils/cache.py
import time
import functools
from typing import Any, Callable, Dict, Tuple, Optional

class TTLCache:
    def __init__(self, maxsize: int = 1024, ttl: float = 600.0):
        self.maxsize = maxsize
        self.ttl = ttl
        self._store: Dict[Any, Tuple[float, Any]] = {}

    def _evict_if_needed(self):
        if len(self._store) <= self.maxsize:
            return
        # evict oldest by expiry time
        oldest_key = min(self._store, key=lambda k: self._store[k][0])
        self._store.pop(oldest_key, None)

    def get(self, key: Any) -> Optional[Any]:
        now = time.time()
        rec = self._store.get(key)
        if not rec:
            return None
        expiry, value = rec
        if now > expiry:
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: Any, value: Any):
        now = time.time()
        self._store[key] = (now + self.ttl, value)
        self._evict_if_needed()

def _freeze(obj):
    # make args/kwargs hashable for cache key
    if isinstance(obj, dict):
        return tuple(sorted((k, _freeze(v)) for k, v in obj.items()))
    if isinstance(obj, (list, tuple, set)):
        return tuple(_freeze(x) for x in obj)
    return obj

def ttl_memoize(cache: TTLCache):
    def deco(fn: Callable):
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            key = (fn.__module__, fn.__name__, _freeze(args), _freeze(kwargs))
            hit = cache.get(key)
            if hit is not None:
                return hit, True  # (value, cached?)
            value = await fn(*args, **kwargs)
            cache.set(key, value)
            return value, False
        return wrapper
    return deco
