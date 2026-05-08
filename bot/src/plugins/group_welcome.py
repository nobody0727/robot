"""
入群欢迎插件
"""
from nonebot import on_notice
from nonebot.adapters.onebot.v11 import (
    GroupIncreaseNoticeEvent,
    GroupDecreaseNoticeEvent,
    Message,
    MessageSegment,
    NoticeEvent
)


group_welcome = on_notice()


@group_welcome.handle()
async def handle_group_increase(event: NoticeEvent):
    if isinstance(event, GroupIncreaseNoticeEvent):
        user_id = event.user_id
        group_id = event.group_id
        self_id = event.self_id

        if user_id == self_id:
            return

        welcome_msg = await get_welcome_message(group_id)
        if welcome_msg:
            user_info = await get_user_info(user_id)
            msg = welcome_msg.format(name=user_info.get("nickname", "新成员"))
            await group_welcome.send(Message([MessageSegment.text(msg)]))


group_goodbye = on_notice()


@group_goodbye.handle()
async def handle_group_decrease(event: NoticeEvent):
    if isinstance(event, GroupDecreaseNoticeEvent):
        user_id = event.user_id
        group_id = event.group_id
        self_id = event.self_id

        if user_id == self_id:
            return


async def get_welcome_message(group_id: str) -> str:
    """获取群组的欢迎语"""
    return "欢迎 {name} 加入群聊！"


async def get_user_info(user_id: int) -> dict:
    """获取用户信息"""
    return {"nickname": f"用户{user_id}"}
