# 简单内存缓存实现，替代Redis
class MemoryCache:
    def __init__(self):
        self._cache = {}
    
    def get(self, key):
        return self._cache.get(key)
    
    def set(self, key, value, ex=None):
        self._cache[key] = value
        return True

# 全局缓存实例
redis_client = MemoryCache()
