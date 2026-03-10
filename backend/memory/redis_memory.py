"""
File: redis_memory.py

Purpose:
Provides a simple Redis-backed memory interface for storing and retrieving
key-value data.

Key Functionalities:
- Initialize Redis client connection
- Set key-value pairs in Redis
- Get values by key from Redis

Inputs:
- String keys and associated values

Outputs:
- Stored values retrieved from Redis

Interacting Files / Modules:
- None
"""
import redis

client = redis.Redis(host="localhost", port=6379)

class RedisMemory:

    def set(self, key, value):
        client.set(key, value)

    def get(self, key):
        return client.get(key)
