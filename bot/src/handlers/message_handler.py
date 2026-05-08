from wechaty import Message
from bot.src.services.message_cache import MessageCache
from bot.src.services.message_store import MessageStore
from bot.src.utils.message_parser import MessageParser


class MessageHandler:
    def __init__(self):
        self.cache = MessageCache()
        self.store = MessageStore()
        self.parser = MessageParser()
    
    async def init(self):
        await self.cache.connect()
    
    async def close(self):
        await self.cache.close()
    
    async def handle_message(self, msg: Message) -> bool:
        msg_type = self.parser.get_message_type(msg)
        
        if msg_type == "text":
            return await self._handle_text_message(msg)
        elif msg_type == "recall":
            return await self._handle_recall_message(msg)
        
        return False
    
    async def _handle_text_message(self, msg: Message) -> bool:
        try:
            msg_id = self.parser.get_message_id(msg)
            sender_id = self.parser.get_sender_id(msg)
            sender_name = self.parser.get_sender_name(msg)
            content = self.parser.get_content(msg)
            room_id = self.parser.get_room_id(msg)
            extra_data = self.parser.get_extra_data(msg)
            
            if room_id:
                group = await self.store.get_group_by_room_id(room_id)
                if group and group.is_active:
                    await self.store.create_message(
                        group_id=group.id,
                        sender_id=sender_id,
                        content=content,
                        msg_type="text",
                        sender_name=sender_name,
                        raw_msg_id=msg_id,
                        extra_data=extra_data
                    )
                    
                    await self.cache.set_message(msg_id, {
                        "sender_id": sender_id,
                        "sender_name": sender_name,
                        "content": content,
                        "room_id": room_id,
                        "msg_type": "text"
                    })
                    
                    await self.store.update_group_activity(room_id)
            
            return True
        
        except Exception as e:
            print(f"Error handling text message: {e}")
            return False
    
    async def _handle_recall_message(self, msg: Message) -> bool:
        return True
    
    async def handle_room_join(self, room, invitee_list, inviter) -> bool:
        try:
            room_id = room.room_id
            room_name = room.topic
            
            for contact in invitee_list:
                await self.store.create_message(
                    group_id=None,
                    sender_id=inviter.contact_id if inviter else "system",
                    content=f"{contact.name or contact.contact_id} 加入了群聊",
                    msg_type="join",
                    sender_name=inviter.name if inviter else "系统"
                )
            
            return True
        
        except Exception as e:
            print(f"Error handling room join: {e}")
            return False
    
    async def handle_room_leave(self, room, leaver_list, remover) -> bool:
        try:
            room_id = room.room_id
            room_name = room.topic
            
            for contact in leaver_list:
                await self.store.create_message(
                    group_id=None,
                    sender_id=remover.contact_id if remover else "system",
                    content=f"{contact.name or contact.contact_id} 退出了群聊",
                    msg_type="leave",
                    sender_name=remover.name if remover else "系统"
                )
            
            return True
        
        except Exception as e:
            print(f"Error handling room leave: {e}")
            return False
