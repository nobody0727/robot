import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from wechaty import Wechaty
from wechaty.user import Contact, Room
from wechaty.plugin import WechatyPlugin

from bot.src.handlers.message_handler import MessageHandler
from bot.src.handlers.ai_handler import AIHandler
from bot.src.handlers.recall_handler import RecallHandler
from bot.src.handlers.room_handler import RoomHandler
from bot.src.handlers.search_handler import SearchHandler
from bot.src.services.whitelist_checker import WhitelistChecker
from bot.src.utils.message_parser import MessageParser
from bot.src.config import settings


class WeChatBot(Wechaty):
    def __init__(self):
        super().__init__()
        self.message_handler = MessageHandler()
        self.ai_handler = AIHandler()
        self.recall_handler = RecallHandler()
        self.room_handler = RoomHandler()
        self.search_handler = SearchHandler()
        self.whitelist_checker = WhitelistChecker()
        self.parser = MessageParser()
    
    async def init_plugin(self):
        await self.message_handler.init()
        await self.ai_handler.init()
        await self.recall_handler.init()
        self.use(WhitelistPlugin())
    
    async def on_message(self, msg: Message):
        try:
            if msg.is_self():
                return
            
            msg_type = self.parser.get_message_type(msg)
            
            if msg_type == "recall":
                await self.recall_handler.handle_recall(msg)
                return
            
            if not self.parser.is_text_message(msg):
                await self.message_handler.handle_message(msg)
                return
            
            room = msg.room()
            sender_id = self.parser.get_sender_id(msg)
            content = self.parser.get_content(msg)
            
            if room:
                room_id = room.room_id
                
                if self.parser.is_mentioned_bot(msg):
                    if "搜索" in content or "查找" in content:
                        query = content.replace("@", "").replace("搜索", "").replace("查找", "").strip()
                        response = await self.search_handler.handle_search(msg, query, room_id)
                        await room.say(response)
                    else:
                        response = await self.ai_handler.handle_ai_message(msg, room_id)
                        if response:
                            await room.say(response)
                
                await self.message_handler.handle_message(msg)
            
            else:
                is_whitelisted = await self.whitelist_checker.check_whitelist(sender_id)
                
                if is_whitelisted:
                    response = await self.ai_handler.handle_private_ai_message(msg, sender_id)
                    await msg.say(response)
                else:
                    reject_msg = "您暂无权限使用此功能，请联系管理员添加白名单。"
                    await msg.say(reject_msg)
        
        except Exception as e:
            print(f"Error processing message: {e}")
    
    async def on_room_join(self, room: Room, invitee_list: list, inviter: Contact):
        try:
            inviter_id = inviter.contact_id if inviter else None
            
            if inviter_id:
                has_permission = await self.whitelist_checker.check_group_invite_permission(inviter_id)
                
                if not has_permission:
                    await room.say("您暂无权限邀请我入群，请联系管理员。")
                    return
            
            await self.room_handler.handle_room_join(room, invitee_list, inviter)
        
        except Exception as e:
            print(f"Error handling room join event: {e}")
    
    async def on_room_leave(self, room: Room, leaver_list: list, remover: Contact):
        try:
            await self.room_handler.handle_room_leave(room, leaver_list, remover)
        except Exception as e:
            print(f"Error handling room leave event: {e}")
    
    async def on_login(self, contact: Contact):
        print(f"Bot logged in as: {contact.name}")


async def main():
    bot = WeChatBot()
    
    if settings.WECHATY_TOKEN:
        await bot.start(token=settings.WECHATY_TOKEN)
    else:
        print("Please set WECHATY_TOKEN environment variable")
        return


if __name__ == "__main__":
    asyncio.run(main())
