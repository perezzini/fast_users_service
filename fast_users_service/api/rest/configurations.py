from typing import Any

from fastapi import APIRouter, Depends
from fast_users_service.api.configurations import get as get_
from fast_users_service.api.configurations import update as update_
from fast_users_service.api.security import is_admin
from fast_users_service.api.users import get_current_active_user, get_session
from fast_users_service.db.models import (
    ConfigurationResponse,
    ConfigurationUpdate,
    User,
)
from sqlmodel import Session

ROUTER = APIRouter()


@ROUTER.get(
    "",
    response_model=ConfigurationResponse,
    response_model_exclude_none=True,
    dependencies=[Depends(is_admin)],
)
def get(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get current service configurations properties. Only admin users can execute this operation"""
    return get_(session)


@ROUTER.patch(
    "",
    response_model=ConfigurationResponse,
    response_model_exclude_none=True,
    dependencies=[Depends(is_admin)],
)
def update(
    request: ConfigurationUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Update current service configurations properties. Only admin users can execute this operation"""
    return update_(current_user.id, request, session)  # type: ignore
