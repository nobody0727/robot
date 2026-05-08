from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.services.search_service import SearchService
from app.core.dependencies import get_current_user, require_operator
from app.models.user import AdminUser

router = APIRouter(prefix="/search", tags=["智能搜索"])


class SemanticSearchRequest(BaseModel):
    query: str
    group_id: Optional[int] = None
    top_k: int = 10
    include_context: bool = True


class KeywordSearchRequest(BaseModel):
    keyword: str
    group_id: Optional[int] = None
    page: int = 1
    page_size: int = 20


@router.post("/semantic")
async def semantic_search(
    request: SemanticSearchRequest,
    current_user: AdminUser = Depends(require_operator),
    db = Depends(get_db)
):
    from sqlalchemy.orm import Session
    db_session = db
    
    search_service = SearchService(db_session)
    result = await search_service.semantic_search(
        query=request.query,
        group_id=request.group_id,
        top_k=request.top_k,
        include_context=request.include_context
    )
    
    return result


@router.post("/keyword")
async def keyword_search(
    request: KeywordSearchRequest,
    current_user: AdminUser = Depends(require_operator),
    db = Depends(get_db)
):
    from sqlalchemy.orm import Session
    db_session = db
    
    search_service = SearchService(db_session)
    result = search_service.keyword_search(
        keyword=request.keyword,
        group_id=request.group_id,
        page=request.page,
        page_size=request.page_size
    )
    
    return result
