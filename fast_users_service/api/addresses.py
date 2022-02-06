from typing import List, Optional

from fastapi import HTTPException, status
from loguru import logger
from fast_users_service.db.models import Address, AddressCreate, AddressUpdate, User
from fast_users_service.db.transactions import create as create_
from fast_users_service.db.transactions import delete as delete_
from fast_users_service.db.transactions import update as update_
from sqlmodel import Session, select


def create(address: AddressCreate, session: Session, current_user_id: str) -> Address:
    """Create an address

    Args:
        address (AddressCreate): An address request
        session (Session): A DB session
        current_user_id (str): Current user ID

    Raises:
        HTTPException: In case request carries incomplete lat/lon coords

    Returns:
        Address: An address
    """
    if any([address.lat, address.lon]):
        if not all([address.lat, address.lon]):
            logger.info("Found incomplete lat/lon coords when creating address")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incomplete coordinate values",
            )

    address_: Address = Address.from_orm(address)

    result: Address = create_(address_, session, current_user_id)

    return result


def get_all(
    session: Session,
    start: Optional[int] = None,
    end: Optional[int] = None,
    show_deleted_records: Optional[bool] = False,
) -> List[Address]:
    """Get addresses based on given query params

    Args:
        session (Session): A DB session
        start (Optional[int], optional): Start index. Defaults to None.
        end (Optional[int], optional): End index. Defaults to None.
        show_deleted_records (Optional[bool], optional): Whether to respond with deleted records.
        Defaults to False.

    Raises:
        HTTPException: In case invalid query params are given

    Returns:
        List[Address]: A list of addresses
    """
    if end and start and end < start:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid query params"
        )

    stmt = select(Address).where(Address.deleted == show_deleted_records)
    results = session.exec(stmt)
    addresses = results.all()

    if not start:
        start = 0

    return addresses[start : start + end] if end else addresses[start:]  # noqa


def get(
    id: str,
    session: Session,
    current_user: User,
) -> Address:
    """Get address by its ID

    Args:
        id (str): An address ID
        session (Session): A DB session
        current_user (User): Current user

    Raises:
        HTTPException: In case address does not exist, or
        current user cannot access it due to privileges

    Returns:
        Address: An address
    """

    address = session.get(Address, id)

    if not address or address and address.deleted:
        logger.info("Not found address ID = {}", id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Address not found"
        )

    if not any([current_user.is_admin, address.created_by == current_user.id]):
        logger.info(
            "Current user ID = {} not allowed to retrive address given by ID = {}",
            current_user.id,
            id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not allowed to retrive address",
        )

    return address


def update(
    id: str, request: AddressUpdate, session: Session, current_user: User
) -> Address:
    """Update address by its ID

    Args:
        id (str): An address ID
        request (AddressUpdate): An address update request
        session (Session): A DB session
        current_user (User): Current user

    Raises:
        HTTPException: In case address does not exists,
        or current user does not own the address

    Returns:
        Address: An address
    """
    address = get(id, session, current_user)

    if not address:
        logger.info("Not found address ID = {}", id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Address not found"
        )

    if not any([current_user.is_admin, address.created_by == current_user.id]):
        logger.info(
            "Current user ID = {} not allowed to update address ID = {}",
            current_user.id,
            id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not allowed to update address",
        )

    result: Address = update_(current_user.id, address, request, session)  # type: ignore

    return result


def delete(id: str, session: Session, current_user: User) -> None:
    """Delete an address given by its ID

    Args:
        id (str): An address ID
        session (Session): A DB session
        current_user (User): Current user

    Raises:
        HTTPException: In case address does not exist, or
        current user cannot access to it due to privileges
    """
    address = get(id, session, current_user)

    if not address:
        logger.info("Not found address ID = {}", id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Address not found"
        )

    if not any([current_user.is_admin, address.created_by == current_user.id]):
        logger.info(
            "User ID = {} not allowed not delete address ID = {}", current_user.id, id
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not allowed to delete address",
        )

    delete_(address, session, current_user.id)  # type: ignore
