import redis.asyncio as redis
from app.config import settings
from typing import Optional
import json

redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=50
        )
    return redis_client


async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None


class MessageCache:
    def __init__(self, redis_conn: redis.Redis, ttl: int = 120):
        self.redis = redis_conn
        self.ttl = ttl
    
    async def set_message(self, msg_id: str, data: dict):
        key = f"msg_cache:{msg_id}"
        await self.redis.setex(key, self.ttl, json.dumps(data, ensure_ascii=False))
    
    async def get_message(self, msg_id: str) -> Optional[dict]:
        key = f"msg_cache:{msg_id}"
        data = await self.redis.get(key)
        if data:
            return json.loads(data)
        return None
    
    async def delete_message(self, msg_id: str):
        key = f"msg_cache:{msg_id}"
        await self.redis.delete(key)


class ConversationContext:
    def __init__(self, redis_conn: redis.Redis):
        self.redis = redis_conn
        self.group_ttl = 86400
        self.private_ttl = 86400
    
    def _get_key(self, type_: str, id_: str) -> str:
        return f"chat:{type_}:{id_}"
    
    async def add_message(self, type_: str, id_: str, role: str, content: str, max_messages: int = 10):
        key = self._get_key(type_, id_)
        ttl = self.group_ttl if "group" in type_ else self.private_ttl
        
        messages = await self.get_context(type_, id_)
        messages.append({"role": role, "content": content})
        
        max_items = max_messages * 2
        if len(messages) > max_items:
            messages = messages[-max_items:]
        
        await self.redis.setex(key, ttl, json.dumps(messages, ensure_ascii=False))
    
    async def get_context(self, type_: str, id_: str) -> list:
        key = self._get_key(type_, id_)
        data = await self.redis.get(key)
        if data:
            return json.loads(data)
        return []
    
    async def clear_context(self, type_: str, id_: str):
        key = self._get_key(type_, id_)
        await self.redis.delete(key)


class WhitelistCache:
    def __init__(self, redis_conn: redis.Redis, ttl: int = 300):
        self.redis = redis_conn
        self.ttl = ttl
    
    async def set_whitelist(self, user_id: str, is_whitelisted: bool):
        key = f"whitelist:{user_id}"
        await self.redis.setex(key, self.ttl, "1" if is_whitelisted else "0")
    
    async def get_whitelist(self, user_id: str) -> Optional[bool]:
        key = f"whitelist:{user_id}"
        data = await self.redis.get(key)
        if data:
            return data == "1"
        return None
    
    async def invalidate(self, user_id: str):
        key = f"whitelist:{user_id}"
        await self.redis.delete(key)


def get_message_cache(redis_conn: redis.Redis) -> MessageCache:
    return MessageCache(redis_conn, settings.MESSAGE_CACHE_TTL)


def get_conversation_context(redis_conn: redis.Redis) -> ConversationContext:
    return ConversationContext(redis_conn)


def get_whitelist_cache(redis_conn: redis.Redis) -> WhitelistCache:
    return WhitelistCache(redis_conn)
