from wechaty import Message
from bot.src.services.message_cache import MessageCache
from bot.src.services.message_store import MessageStore
from bot.src.utils.message_parser import MessageParser


class RecallHandler:
    def __init__(self):
        self.cache = MessageCache()
        self.store = MessageStore()
        self.parser = MessageParser()
    
    async def init(self):
        await self.cache.connect()
    
    async def close(self):
        await self.cache.close()
    
    async def handle_recall(self, msg: Message) -> bool:
        try:
            raw_msg_id = self.parser.parse_recall_info(msg)
            
            if not raw_msg_id:
                return False
            
            original_msg = await self.cache.get_and_delete_message(raw_msg_id)
            
            if not original_msg:
                return False
            
            room_id = original_msg.get("room_id")
            sender_name = original_msg.get("sender_name", "未知用户")
            content = original_msg.get("content", "")
            
            if room_id:
                recovery_text = f"🔔 消息被撤回，已恢复：👤 {sender_name} 说：{content}"
                
                room = msg.room()
                if room:
                    await room.say(recovery_text)
                    
                    await self.store.mark_message_recalled(raw_msg_id)
                    return True
            
            return False
        
        except Exception as e:
            print(f"Error handling recall: {e}")
            return False
