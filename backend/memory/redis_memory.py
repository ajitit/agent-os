import redis

client = redis.Redis(host="localhost", port=6379)

class RedisMemory:

    def set(self, key, value):
        client.set(key, value)

    def get(self, key):
        return client.get(key)
