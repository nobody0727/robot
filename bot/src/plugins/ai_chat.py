"""
AI 对话插件 - 处理群聊和私聊的 AI 对话请求
"""
import os
import httpx
import json
from nonebot import on_message, on_command, require
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent, Message, MessageSegment
from nonebot.typing import T_State
from nonebot.params import State
from datetime import datetime, time

scheduler = require("nonebot_plugin_apscheduler")

from ..utils.config import settings


class AIService:
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = settings.DEEPSEEK_BASE_URL
        self.model = settings.DEEPSEEK_MODEL
        self.temperature = settings.AI_TEMPERATURE
        self.max_tokens = settings.AI_MAX_TOKENS

    async def generate_response(self, prompt: str, context: list = None) -> str:
        """调用 DeepSeek API 生成回复"""
        if not self.api_key:
            return "AI 服务暂不可用，请联系管理员配置 API Key"

        messages = []
        if context:
            messages.extend(context)
        messages.append({"role": "user", "content": prompt})

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": self.temperature,
                        "max_tokens": self.max_tokens
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    return f"AI 服务错误: {response.status_code}"
        except Exception as e:
            return f"AI 服务暂不可用: {str(e)}"


ai_service = AIService()


def is_ai_active() -> bool:
    """检查当前时间是否在 AI 休眠时段"""
    current_time = datetime.now().time()
    sleep_start = time(23, 0)
    sleep_end = time(7, 0)

    if sleep_start <= sleep_end:
        return not (sleep_start <= current_time <= sleep_end)
    else:
        return not (current_time >= sleep_start or current_time <= sleep_end)


ai_chat = on_message(rule=lambda _: True, priority=10)


@ai_chat.handle()
async def handle_ai(event: GroupMessageEvent, state: State = State()):
    user_id = str(event.user_id)
    group_id = str(event.group_id)
    content = event.message.extract_plain_text().strip()

    if not content:
        return

    if not is_ai_active():
        return

    context = await get_conversation_context(group_id, user_id)

    response = await ai_service.generate_response(content, context)

    await save_conversation_context(group_id, user_id, content, response)

    await ai_chat.finish(Message([MessageSegment.text(response)]))


ai_help = on_command("帮助", aliases={"help", "Help"})
ai_clear = on_command("清空", aliases={"clear", "Clear"})
ai_status = on_command("AI状态", aliases={"status"})


@ai_help.handle()
async def handle_help(event: GroupMessageEvent | PrivateMessageEvent):
    help_text = """🤖 QQ AI 助手使用指南：

• 直接发送消息：与我对话
• @我 + 问题：在群聊中提问
• 帮助：查看帮助信息
• 清空：重置对话上下文

🌙 AI 休眠时段：23:00-07:00"""
    await ai_help.finish(Message([MessageSegment.text(help_text)]))


@ai_clear.handle()
async def handle_clear(event: GroupMessageEvent | PrivateMessageEvent):
    user_id = str(event.user_id)
    group_id = str(event.group_id) if isinstance(event, GroupMessageEvent) else user_id
    await clear_conversation_context(group_id, user_id)
    await ai_clear.finish("对话上下文已清空。")


@ai_status.handle()
async def handle_status(event: GroupMessageEvent | PrivateMessageEvent):
    status = "在线" if is_ai_active() else "休眠中"
    await ai_status.finish(f"AI 状态: {status}")


async def get_conversation_context(group_id: str, user_id: str, limit: int = 10) -> list:
    """获取对话上下文"""
    return []


async def save_conversation_context(group_id: str, user_id: str, user_msg: str, ai_response: str):
    """保存对话上下文"""
    pass


async def clear_conversation_context(group_id: str, user_id: str):
    """清空对话上下文"""
    pass
