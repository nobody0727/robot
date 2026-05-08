from sqlalchemy.orm import Session
from sqlalchemy import or_, func, text
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from app.models.message import GroupMessage
from app.models.group import BotGroup
from app.services.ai_service import AIService
from app.core.exceptions import MessageNotFoundError
import json


class SearchService:
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIService()

    async def semantic_search(
        self,
        query: str,
        group_id: Optional[int] = None,
        top_k: int = 10,
        include_context: bool = True
    ) -> dict:
        start_time = datetime.now()
        
        expanded = await self.ai_service.expand_query(query)
        keywords = expanded.get("keywords", [query])
        
        query_vector = await self.ai_service.get_embedding(query)
        query_vector_str = json.dumps(query_vector)
        
        base_query = self.db.query(GroupMessage).filter(
            GroupMessage.is_recalled == False,
            GroupMessage.content.isnot(None)
        )
        
        if group_id:
            base_query = base_query.filter(GroupMessage.group_id == group_id)
        
        vector_sql = f"""
            1 - (content_vector <=> '{query_vector_str}'::vector)
        """
        
        keyword_patterns = [f"%{kw}%" for kw in keywords]
        
        results = []
        for msg in base_query.all():
            keyword_score = 0
            for pattern in keyword_patterns:
                if pattern.replace("%", "") in msg.content:
                    keyword_score += 1
            keyword_score = keyword_score / len(keyword_patterns) if keyword_patterns else 0
            
            semantic_score = 0.0
            if msg.content_vector:
                try:
                    stored_vector = json.loads(msg.content_vector)
                    semantic_score = self._cosine_similarity(query_vector, stored_vector)
                except:
                    pass
            
            combined_score = semantic_score * 0.7 + keyword_score * 0.3
            
            if combined_score > 0.1:
                results.append({
                    "id": msg.id,
                    "content": msg.content,
                    "sender_name": msg.sender_name,
                    "sender_id": msg.sender_id,
                    "group_id": msg.group_id,
                    "group_name": msg.group.room_name if msg.group else None,
                    "created_at": msg.created_at.isoformat() if msg.created_at else None,
                    "similarity": round(combined_score, 4),
                    "semantic_score": round(semantic_score, 4),
                    "keyword_score": round(keyword_score, 4)
                })
        
        results.sort(key=lambda x: x["similarity"], reverse=True)
        results = results[:top_k]
        
        search_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return {
            "query": query,
            "expanded_keywords": keywords,
            "synonyms": expanded.get("synonyms", []),
            "results": results,
            "total": len(results),
            "search_time_ms": round(search_time, 2)
        }

    def keyword_search(
        self,
        keyword: str,
        group_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        query = self.db.query(GroupMessage).filter(
            GroupMessage.is_recalled == False,
            GroupMessage.content.ilike(f"%{keyword}%")
        )
        
        if group_id:
            query = query.filter(GroupMessage.group_id == group_id)
        
        total = query.count()
        
        messages = query.order_by(GroupMessage.created_at.desc()) \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .all()
        
        items = []
        for msg in messages:
            items.append({
                "id": msg.id,
                "content": msg.content,
                "sender_name": msg.sender_name,
                "sender_id": msg.sender_id,
                "group_id": msg.group_id,
                "group_name": msg.group.room_name if msg.group else None,
                "created_at": msg.created_at.isoformat() if msg.created_at else None,
                "msg_type": msg.msg_type
            })
        
        return {
            "keyword": keyword,
            "results": items,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        if len(vec1) != len(vec2) or len(vec1) == 0:
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
