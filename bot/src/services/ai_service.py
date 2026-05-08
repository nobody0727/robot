import httpx
from typing import Optional, List, Dict
from bot.src.config import settings


class AIService:
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = settings.DEEPSEEK_BASE_URL
        self.model = settings.DEEPSEEK_MODEL
        self.temperature = settings.AI_TEMPERATURE
        self.max_tokens = settings.AI_MAX_TOKENS
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        if not self.api_key:
            return "AI服务未配置，请联系管理员。"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    return "AI服务暂时不可用，请稍后再试。"
                
                data = response.json()
                
                if "choices" not in data or len(data["choices"]) == 0:
                    return "AI服务响应异常。"
                
                return data["choices"][0]["message"]["content"]
        
        except httpx.TimeoutException:
            return "AI服务响应超时，请稍后再试。"
        except Exception:
            return "AI服务连接失败，请稍后再试。"
    
    async def generate_response(self, user_message: str, context: List[Dict[str, str]] = None) -> str:
        system_prompt = """你是一个友善的微信群助手。请用简洁、有趣的方式回答问题。
注意：
1. 回答要简短，一般不超过200字
2. 如果不知道答案，直接说不知道，不要编造
3. 保持友好和帮助的态度
4. 不要重复用户的问题"""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if context:
            messages.extend(context)
        
        messages.append({"role": "user", "content": user_message})
        
        return await self.chat(messages)
    
    async def expand_query(self, query: str) -> Dict[str, List[str]]:
        if not self.api_key:
            return {"keywords": [query], "synonyms": []}
        
        prompt = f"""分析以下搜索查询，提取关键词。

查询：{query}

返回JSON格式：{{"keywords": ["关键词1", "关键词2"]}}
只返回JSON，不要其他内容。"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 200
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    return {"keywords": [query], "synonyms": []}
                
                data = response.json()
                content = data["choices"][0]["message"]["content"].strip()
                content = content.strip("```json").strip("```").strip()
                
                import json
                result = json.loads(content)
                return {
                    "keywords": result.get("keywords", [query]),
                    "synonyms": result.get("synonyms", [])
                }
        except Exception:
            return {"keywords": [query], "synonyms": []}
