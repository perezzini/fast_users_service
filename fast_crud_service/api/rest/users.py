from typing import Any, List, Optional

from fastapi import APIRouter, Depends, status
from fast_users_service.api.security import get_password_hash, is_admin
from fast_users_service.api.users import create
from fast_users_service.api.users import delete as delete_
from fast_users_service.api.users import get as get_
from fast_users_service.api.users import get_all, get_current_active_user, get_session
from fast_users_service.api.users import update as update_
from fast_users_service.db.models import User, UserCreate, UserResponse, UserUpdate
from sqlmodel import Session
from starlette.responses import Response

ROUTER = APIRouter()


@ROUTER.post(
    "",
    response_model=UserResponse,
    response_model_exclude_none=True,
    dependencies=[Depends(is_admin)],
)
def create_user(
    user: UserCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Create a user. Only admin users can execute this operation"""
    return create(user, session, current_user.id, get_password_hash)  # type: ignore


@ROUTER.get(
    "",
    response_model=List[UserResponse],
    response_model_exclude_none=True,
    dependencies=[Depends(is_admin)],
)
def get_users(
    session: Session = Depends(get_session),
    start: Optional[int] = 0,
    end: Optional[int] = 50,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get all users. Only admin users can execute this operation"""
    return get_all(session, start, end)


@ROUTER.get(
    "/me",
    response_model=UserResponse,
    response_model_exclude_none=True,
)
def get_me(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get current user"""
    return current_user


@ROUTER.patch(
    "/me",
    response_model=UserResponse,
    response_model_exclude_none=True,
)
def update_me(
    request: UserUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Update current user"""
    return update_(current_user.id, request, session, get_password_hash, current_user.id)  # type: ignore


@ROUTER.get(
    "/{id}",
    response_model=UserResponse,
    response_model_exclude_none=True,
    dependencies=[Depends(is_admin)],
)
def get(
    id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get user resource given by its ID. Only admin users can execute this
    operation"""
    return get_(id, session)


@ROUTER.patch(
    "/{id}",
    response_model=UserResponse,
    response_model_exclude_none=True,
    dependencies=[Depends(is_admin)],
)
def update(
    id: str,
    request: UserUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Update a user resource given by its ID. Only admin
    users can execute this operation"""
    return update_(id, request, session, get_password_hash, current_user.id)  # type: ignore


@ROUTER.delete("/{id}", dependencies=[Depends(is_admin)])
def delete(
    id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Delete a user resource given by its ID. Only admin users
    can execute this operation"""
    delete_(id, session, current_user.id)  # type: ignore

    return Response(status_code=status.HTTP_204_NO_CONTENT)
