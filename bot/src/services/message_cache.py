import redis.asyncio as redis
import json
from typing import Optional, Dict
from bot.src.config import settings


class MessageCache:
    def __init__(self, ttl: int = None):
        self.redis: Optional[redis.Redis] = None
        self.ttl = ttl or settings.MESSAGE_CACHE_TTL
    
    async def connect(self):
        if not self.redis:
            self.redis = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
    
    async def close(self):
        if self.redis:
            await self.redis.close()
            self.redis = None
    
    async def set_message(self, msg_id: str, data: Dict):
        key = f"msg_cache:{msg_id}"
        await self.redis.setex(key, self.ttl, json.dumps(data, ensure_ascii=False))
    
    async def get_message(self, msg_id: str) -> Optional[Dict]:
        key = f"msg_cache:{msg_id}"
        data = await self.redis.get(key)
        if data:
            return json.loads(data)
        return None
    
    async def delete_message(self, msg_id: str):
        key = f"msg_cache:{msg_id}"
        await self.redis.delete(key)
    
    async def get_and_delete_message(self, msg_id: str) -> Optional[Dict]:
        key = f"msg_cache:{msg_id}"
        pipe = self.redis.pipeline()
        pipe.get(key)
        pipe.delete(key)
        results = await pipe.execute()
        if results[0]:
            return json.loads(results[0])
        return None


class ConversationContext:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        self.group_ttl = 86400
        self.private_ttl = 86400
    
    async def connect(self):
        if not self.redis:
            self.redis = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
    
    async def close(self):
        if self.redis:
            await self.redis.close()
            self.redis = None
    
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
    
    async def get_context_with_limit(self, type_: str, id_: str, limit: int = 10) -> list:
        messages = await self.get_context(type_, id_)
        return messages[-limit * 2:] if len(messages) > limit * 2 else messages
