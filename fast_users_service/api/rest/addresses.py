from typing import Any, List, Optional

from fastapi import APIRouter, Depends, Response, status
from fast_users_service.api.addresses import create
from fast_users_service.api.addresses import delete as delete_
from fast_users_service.api.addresses import get as get_
from fast_users_service.api.addresses import get_all
from fast_users_service.api.addresses import update as update_
from fast_users_service.api.security import is_admin
from fast_users_service.api.users import get_current_active_user, get_session
from fast_users_service.db.models import (
    AddressCreate,
    AddressResponse,
    AddressUpdate,
    User,
)
from sqlmodel import Session

ROUTER = APIRouter()


@ROUTER.post(
    "",
    response_model=AddressResponse,
    response_model_exclude_none=True,
)
def create_address(
    address: AddressCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Create an address"""
    return create(address, session, current_user.id)  # type: ignore


@ROUTER.get(
    "",
    response_model=List[AddressResponse],
    response_model_exclude_none=True,
    dependencies=[Depends(is_admin)],
)
def get_addresses(
    session: Session = Depends(get_session),
    start: Optional[int] = 0,
    end: Optional[int] = 50,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get all addresses. Only admin users can execute this operation"""
    return get_all(session, start, end)


@ROUTER.get(
    "/{id}",
    response_model=AddressResponse,
    response_model_exclude_none=True,
)
def get(
    id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get address resource by its ID. Only admin users or the user who
    created the address can execute this operation"""
    return get_(id, session, current_user)


@ROUTER.patch(
    "/{id}",
    response_model=AddressUpdate,
    response_model_exclude_none=True,
)
def update(
    id: str,
    request: AddressUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Update address resource. Only admin users or the user who
    created the address can execute this operation"""
    return update_(id, request, session, current_user)


@ROUTER.delete("/{id}")
def delete(
    id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Delete address resource. Only admin users or the user who
    created this address can execute this operation"""
    delete_(id, session, current_user)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
