import httpx
from wechaty import Message
from bot.src.services.message_store import MessageStore
from bot.src.services.ai_service import AIService
from bot.src.utils.message_parser import MessageParser
from bot.src.config import settings


class SearchHandler:
    def __init__(self):
        self.store = MessageStore()
        self.ai = AIService()
        self.parser = MessageParser()
        self.backend_url = settings.BACKEND_URL
    
    async def handle_search(self, msg: Message, query: str, room_id: str) -> str:
        try:
            group = await self.store.get_group_by_room_id(room_id)
            if not group:
                return "无法在未知群聊中搜索。"
            
            expanded = await self.ai.expand_query(query)
            keywords = expanded.get("keywords", [query])
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.backend_url}/api/search/semantic",
                    json={
                        "query": query,
                        "group_id": group.id,
                        "top_k": 10,
                        "include_context": True
                    }
                )
                
                if response.status_code != 200:
                    return "搜索服务暂时不可用。"
                
                data = response.json()
                results = data.get("results", [])
                
                if not results:
                    return f"未找到与「{query}」相关的消息。"
                
                reply_lines = [f"📋 搜索「{query}」的相关消息：\n"]
                
                for i, result in enumerate(results[:5], 1):
                    sender = result.get("sender_name", "未知用户")
                    content = result.get("content", "")[:50]
                    similarity = result.get("similarity", 0)
                    
                    reply_lines.append(f"{i}. 👤 {sender}：{content}...")
                
                reply_lines.append(f"\n共找到 {len(results)} 条相关消息")
                
                return "\n".join(reply_lines)
        
        except Exception as e:
            print(f"Error handling search: {e}")
            return "搜索过程中发生错误。"
