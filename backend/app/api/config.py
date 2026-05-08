from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.schemas.config import ConfigResponse, ConfigListResponse, ConfigUpdate
from app.models.config import SystemConfig
from app.core.dependencies import get_current_user, require_admin, require_operator
from app.core.exceptions import ConfigNotFoundError
from app.models.user import AdminUser

router = APIRouter(prefix="/config", tags=["配置管理"])


@router.get("", response_model=ConfigListResponse)
async def list_configs(
    current_user: AdminUser = Depends(require_operator),
    db: Session = Depends(get_db)
):
    configs = db.query(SystemConfig).all()
    items = []
    for config in configs:
        items.append(ConfigResponse(
            key=config.key,
            value=config.value,
            description=config.description,
            updated_at=config.updated_at.isoformat() if config.updated_at else None,
            updated_by=config.updated_by
        ))
    return ConfigListResponse(items=items)


@router.get("/{config_key}", response_model=ConfigResponse)
async def get_config(
    config_key: str,
    current_user: AdminUser = Depends(require_operator),
    db: Session = Depends(get_db)
):
    config = db.query(SystemConfig).filter(SystemConfig.key == config_key).first()
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="配置项不存在")
    
    return ConfigResponse(
        key=config.key,
        value=config.value,
        description=config.description,
        updated_at=config.updated_at.isoformat() if config.updated_at else None,
        updated_by=config.updated_by
    )


@router.put("/{config_key}", response_model=ConfigResponse)
async def update_config(
    config_key: str,
    config_data: ConfigUpdate,
    current_user: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    config = db.query(SystemConfig).filter(SystemConfig.key == config_key).first()
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="配置项不存在")
    
    config.value = config_data.value
    config.updated_by = current_user.id
    
    db.commit()
    db.refresh(config)
    
    return ConfigResponse(
        key=config.key,
        value=config.value,
        description=config.description,
        updated_at=config.updated_at.isoformat() if config.updated_at else None,
        updated_by=config.updated_by
    )
