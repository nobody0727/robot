import httpx
from typing import Optional, List, Dict
from app.config import settings
from app.core.exceptions import AIServiceUnavailableError, AIRateLimitError, AIInvalidResponseError
import json


class AIService:
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = settings.DEEPSEEK_BASE_URL
        self.model = settings.DEEPSEEK_MODEL
        self.embedding_model = settings.DEEPSEEK_EMBEDDING_MODEL
        self.temperature = settings.AI_TEMPERATURE
        self.max_tokens = settings.AI_MAX_TOKENS

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        if not self.api_key:
            raise AIServiceUnavailableError("DeepSeek API Key未配置")
        
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
                
                if response.status_code == 401:
                    raise AIServiceUnavailableError("DeepSeek API认证失败")
                
                if response.status_code == 429:
                    raise AIRateLimitError()
                
                if response.status_code != 200:
                    raise AIServiceUnavailableError(f"DeepSeek API错误: {response.status_code}")
                
                data = response.json()
                
                if "choices" not in data or len(data["choices"]) == 0:
                    raise AIInvalidResponseError()
                
                return data["choices"][0]["message"]["content"]
        
        except httpx.TimeoutException:
            raise AIServiceUnavailableError("AI服务响应超时")
        except httpx.RequestError:
            raise AIServiceUnavailableError("AI服务连接失败")

    async def expand_query(self, query: str) -> Dict[str, List[str]]:
        if not self.api_key:
            raise AIServiceUnavailableError("DeepSeek API Key未配置")
        
        prompt = f"""请分析以下搜索查询，提取关键词和近义词。

查询：{query}

请以JSON格式返回：
{{"keywords": ["关键词1", "关键词2", ...], "synonyms": ["近义词1", "近义词2", ...]}}

要求：
- keywords: 从查询中提取的核心关键词（3-5个）
- synonyms: 与关键词相关的近义词或扩展词（3-5个）
- 只返回JSON，不要其他内容"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 500
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
                content = data["choices"][0]["message"]["content"]
                
                content = content.strip().strip("```json").strip("```").strip()
                
                result = json.loads(content)
                return {
                    "keywords": result.get("keywords", [query]),
                    "synonyms": result.get("synonyms", [])
                }
        
        except Exception:
            return {"keywords": [query], "synonyms": []}

    async def get_embedding(self, text: str) -> List[float]:
        if not self.api_key:
            raise AIServiceUnavailableError("DeepSeek API Key未配置")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.embedding_model,
            "input": text
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/embeddings",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    return [0.0] * 1536
                
                data = response.json()
                return data["data"][0]["embedding"]
        
        except Exception:
            return [0.0] * 1536
