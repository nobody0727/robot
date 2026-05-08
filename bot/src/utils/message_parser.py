import json
from typing import Optional, Dict, Any
from wechaty import Message, MessageType


class MessageParser:
    @staticmethod
    def get_message_id(msg: Message) -> str:
        return msg.message_id
    
    @staticmethod
    def get_sender_id(msg: Message) -> str:
        talker = msg.talker()
        return talker.contact_id if talker else ""
    
    @staticmethod
    def get_sender_name(msg: Message) -> str:
        talker = msg.talker()
        if talker:
            return talker.name or talker.contact_id
        return ""
    
    @staticmethod
    def get_room_id(msg: Message) -> Optional[str]:
        room = msg.room()
        return room.room_id if room else None
    
    @staticmethod
    def get_room_name(msg: Message) -> Optional[str]:
        room = msg.room()
        if room:
            return room.topic
        return None
    
    @staticmethod
    def get_content(msg: Message) -> str:
        return msg.text or ""
    
    @staticmethod
    def get_message_type(msg: Message) -> str:
        msg_type = msg.type()
        type_mapping = {
            MessageType.TEXT: "text",
            MessageType.IMAGE: "image",
            MessageType.VIDEO: "video",
            MessageType.VOICE: "voice",
            MessageType.EMOTICON: "emoticon",
            MessageType.LOCATION: "location",
            MessageType.MINIPROGRAM: "miniprogram",
            MessageType.RECALL: "recall",
            MessageType.UNKNOWN: "unknown"
        }
        return type_mapping.get(msg_type, "unknown")
    
    @staticmethod
    def is_text_message(msg: Message) -> bool:
        return msg.type() == MessageType.TEXT
    
    @staticmethod
    def is_recall_message(msg: Message) -> bool:
        return msg.type() == MessageType.Recalled
    
    @staticmethod
    def is_from_room(msg: Message) -> bool:
        return msg.room() is not None
    
    @staticmethod
    def is_mentioned_bot(msg: Message) -> bool:
        try:
            mention_self = msg.is_self()
            return mention_self
        except:
            return False
    
    @staticmethod
    def parse_recall_info(msg: Message) -> Optional[str]:
        try:
            extra_data = msg.payload.get("extra_data", {})
            if isinstance(extra_data, str):
                extra_data = json.loads(extra_data)
            
            if extra_data:
                return extra_data.get("original_msg_id") or extra_data.get("msgId")
        except:
            pass
        return None
    
    @staticmethod
    def get_extra_data(msg: Message) -> Dict[str, Any]:
        try:
            payload = msg.payload
            return {
                "type": str(msg.type()),
                "from_id": msg.talker().contact_id if msg.talker() else None,
                "room_id": msg.room().room_id if msg.room() else None,
                "timestamp": payload.get("timestamp")
            }
        except:
            return {}
