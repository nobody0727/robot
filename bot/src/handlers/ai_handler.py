from wechaty import Message
from bot.src.services.message_cache import MessageCache, ConversationContext
from bot.src.services.ai_service import AIService
from bot.src.services.message_store import MessageStore
from bot.src.utils.message_parser import MessageParser
from bot.src.config import settings
from datetime import datetime, time


class AIHandler:
    def __init__(self):
        self.cache = MessageCache()
        self.context = ConversationContext()
        self.ai = AIService()
        self.store = MessageStore()
        self.parser = MessageParser()
    
    async def init(self):
        await self.cache.connect()
        await self.context.connect()
    
    async def close(self):
        await self.cache.close()
        await self.context.close()
    
    async def handle_ai_message(self, msg: Message, room_id: str) -> str:
        if not await self._is_ai_active(room_id):
            return ""
        
        content = self.parser.get_content(msg)
        
        if content.strip() in ["帮助", "help", "Help"]:
            return self._get_help_text()
        
        if content.strip() in ["清空", "clear", "Clear"]:
            await self.context.clear_context("group", room_id)
            return "对话上下文已清空。"
        
        context = await self.context.get_context_with_limit(
            "group", room_id, settings.AI_CONTEXT_GROUP
        )
        
        response = await self.ai.generate_response(content, context)
        
        await self.context.add_message(
            "group", room_id, "user", content, settings.AI_CONTEXT_GROUP
        )
        await self.context.add_message(
            "group", room_id, "assistant", response, settings.AI_CONTEXT_GROUP
        )
        
        return response
    
    async def handle_private_ai_message(self, msg: Message, user_id: str) -> str:
        content = self.parser.get_content(msg)
        
        if content.strip() in ["帮助", "help", "Help"]:
            return self._get_private_help_text()
        
        if content.strip() in ["清空", "clear", "Clear"]:
            await self.context.clear_context("user", user_id)
            return "对话上下文已清空。"
        
        context = await self.context.get_context_with_limit(
            "user", user_id, settings.AI_CONTEXT_PRIVATE
        )
        
        response = await self.ai.generate_response(content, context)
        
        await self.context.add_message(
            "user", user_id, "user", content, settings.AI_CONTEXT_PRIVATE
        )
        await self.context.add_message(
            "user", user_id, "assistant", response, settings.AI_CONTEXT_PRIVATE
        )
        
        return response
    
    async def _is_ai_active(self, room_id: str) -> bool:
        try:
            group = await self.store.get_group_by_room_id(room_id)
            if group and not group.ai_enabled:
                return False
            
            now = datetime.now()
            current_time = now.time()
            
            sleep_start_str = group.ai_sleep_start if group else "23:00"
            sleep_end_str = group.ai_sleep_end if group else "07:00"
            
            sleep_start = time.fromisoformat(sleep_start_str)
            sleep_end = time.fromisoformat(sleep_end_str)
            
            if sleep_start <= sleep_end:
                if sleep_start <= current_time <= sleep_end:
                    return False
            else:
                if current_time >= sleep_start or current_time <= sleep_end:
                    return False
            
            return True
        
        except Exception:
            return True
    
    def _get_help_text(self) -> str:
        return """🤖 群聊AI助手使用指南：

• @我 + 问题：向我提问任何问题
• 帮助：查看帮助信息
• 清空：重置对话上下文

🌙 AI休眠时段：23:00-07:00"""
    
    def _get_private_help_text(self) -> str:
        return """🤖 私聊AI助手使用指南：

• 直接发送消息：与我对话
• 帮助：查看帮助信息
• 清空：重置对话上下文

💡 我会自动记住我们的对话内容（最近20轮）"""
