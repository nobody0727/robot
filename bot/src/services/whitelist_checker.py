import httpx
from typing import Optional
from bot.src.config import settings


class WhitelistChecker:
    def __init__(self):
        self.backend_url = settings.BACKEND_URL
        self.cache: dict = {}
        self.cache_ttl = 300
    
    async def check_whitelist(self, user_id: str) -> bool:
        if user_id in self.cache:
            return self.cache[user_id]
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.backend_url}/api/whitelist/check",
                    json={"user_id": user_id}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    is_whitelisted = data.get("is_whitelisted", False)
                    self.cache[user_id] = is_whitelisted
                    return is_whitelisted
        except Exception:
            pass
        
        return False
    
    def invalidate_cache(self, user_id: str):
        if user_id in self.cache:
            del self.cache[user_id]
    
    async def check_group_invite_permission(self, inviter_id: str) -> bool:
        return await self.check_whitelist(inviter_id)
