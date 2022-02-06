from datetime import datetime
from typing import Any

from fastapi import HTTPException, status
from sqlmodel import Session


def create(resource: Any, session: Session, current_user_id: str) -> Any:
    """Create a resource

    Args:
        resource (Any): A resource obj
        session (Session): A DB session
        current_user_id (str): User ID who executes the operation

    Returns:
        Any: Created resource
    """
    now = str(datetime.utcnow())

    resource.created_at = now
    resource.modified_at = now
    resource.created_by = current_user_id
    resource.modified_by = current_user_id

    session.add(resource)
    session.commit()
    session.refresh(resource)

    return resource


def update(current_user_id: str, resource: Any, request: Any, session: Session) -> Any:
    """Update/Upsert a resource

    Args:
        current_user_id (str): A user ID who executes the operation
        resource (Any): A resource obj
        request (Any): An update/upsert request obj
        session (Session): A DB session

    Returns:
        Any: Updated/Upserted resource
    """
    if resource.deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found"
        )

    for key, value in request.dict(exclude_unset=True).items():
        setattr(resource, key, value)

    resource.modified_at = str(datetime.utcnow())
    resource.modified_by = current_user_id

    session.add(resource)
    session.commit()
    session.refresh(resource)

    return resource


def delete(resource: Any, session: Session, current_user_id: str) -> None:
    """Soft-Delete a resource

    Args:
        resource (Any): A resource obj
        session (Session): A DB session
        current_user_id (str): Current user ID
    """
    now = str(datetime.utcnow())

    resource.deleted = True
    resource.deleted_at = now
    resource.deleted_by = current_user_id

    session.add(resource)
    session.commit()
    session.refresh(resource)
