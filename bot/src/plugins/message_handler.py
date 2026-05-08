"""
消息撤回处理插件
"""
from nonebot import on_notice
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    PrivateMessageEvent,
    Message,
    MessageSegment,
    NoticeEvent,
    GroupRecallNoticeEvent
)


message_recall = on_notice()


@message_recall.handle()
async def handle_recall(event: NoticeEvent):
    if isinstance(event, GroupRecallNoticeEvent):
        user_id = event.user_id
        group_id = event.group_id
        message_id = event.message_id


group_message = on_message(priority=5)


@group_message.handle()
async def handle_message(event: GroupMessageEvent):
    sender_id = str(event.user_id)
    group_id = str(event.group_id)
    content = event.message.extract_plain_text()
    message_id = event.message_id

    await cache_message(message_id, sender_id, group_id, content)


async def cache_message(message_id: str, sender_id: str, group_id: str, content: str):
    """缓存消息用于撤回恢复"""
    pass
