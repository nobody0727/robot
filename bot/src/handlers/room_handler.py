from bot.src.services.message_store import MessageStore


class RoomHandler:
    def __init__(self):
        self.store = MessageStore()
    
    async def handle_room_join(self, room, invitee_list, inviter):
        try:
            room_id = room.room_id
            room_name = room.topic
            
            group = await self.store.create_or_update_group(
                room_id=room_id,
                room_name=room_name
            )
            
            if not group.welcome_enabled:
                return None
            
            for contact in invitee_list:
                name = contact.name or contact.contact_id
                welcome_msg = group.welcome_message or "欢迎 {name} 加入群聊！"
                welcome_msg = welcome_msg.replace("{name}", name)
                
                await room.say(welcome_msg)
            
            return True
        
        except Exception as e:
            print(f"Error handling room join: {e}")
            return None
    
    async def handle_room_leave(self, room, leaver_list, remover):
        try:
            room_id = room.room_id
            room_name = room.topic
            
            owner = await room.owner()
            owner_id = owner.contact_id if owner else None
            
            if owner_id:
                for leaver in leaver_list:
                    leaver_id = leaver.contact_id
                    if leaver_id == owner_id:
                        leave_msg = f"⚠️ 群主 {leaver.name or leaver_id} 已退出群聊"
                        
                        if remover:
                            await remover.say(leave_msg)
            
            return True
        
        except Exception as e:
            print(f"Error handling room leave: {e}")
            return False
