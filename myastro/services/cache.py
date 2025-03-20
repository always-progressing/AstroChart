# 正确的 cache.py 示例
import redis
import json
import os

# 从环境变量获取 Redis 配置
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# 初始化 Redis 客户端
_redis = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    db=REDIS_DB,
    decode_responses=True
)

class RedisClient:
    def __init__(self, redis_instance):
        self._redis = redis_instance
    
    def get(self, key):
        # 使用 self._redis 而不是递归调用自己
        data = self._redis.get(key)
        if data:
            return json.loads(data)
        return None
    
    def set(self, key, value, ex=None):
        # 使用 self._redis 而不是递归调用自己
        return self._redis.set(key, json.dumps(value), ex=ex)

# 创建一个全局实例
redis_client = RedisClient(_redis)



    
    
    
