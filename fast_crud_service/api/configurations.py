from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from fastapi import status
from fastapi.exceptions import HTTPException
from loguru import logger
from fast_users_service.config import CONFIG
from fast_users_service.db.engine import ENGINE
from fast_users_service.db.models import Configuration, ConfigurationUpdate
from fast_users_service.db.transactions import update as update_
from sqlmodel import Session, select


def get_all(
    session: Session,
    start: Optional[int] = None,
    end: Optional[int] = None,
    show_deleted_records: Optional[bool] = False,
) -> List[Configuration]:
    """Get list of configuration resources

    Args:
        session (Session): A DB session
        start (Optional[int], optional): Start index. Defaults to None.
        end (Optional[int], optional): End index. Defaults to None.
        show_deleted_records (Optional[bool], optional): Whether to respond with deleted records.
        Defaults to False.

    Raises:
        HTTPException: In case of invalid query params

    Returns:
        List[Configuration]: A list of configuration resources
    """
    if end and start and end < start:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid query params"
        )

    stmt = select(Configuration).where(Configuration.deleted == show_deleted_records)
    results = session.exec(stmt)
    configs = results.all()

    if not start:
        start = 0

    return configs[start : start + end] if end else configs[start:]  # noqa


def get(session: Session) -> Configuration:
    """Get configuration resource

    Args:
        session (Session): A DB session

    Raises:
        HTTPException: In case more than one resource is found

    Returns:
        Configuration: A configuration resource
    """
    configs = get_all(session)

    if not configs or len(configs) > 1:
        logger.error("Found more than one, or none, configuration resource")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Found more than one, or none, configuration resource",
        )

    return configs[0]


def update(
    current_user_id: str, request: ConfigurationUpdate, session: Session
) -> Configuration:
    """Update service configuration resource

    Args:
        current_user_id (str): Current user ID
        request (ConfigurationUpdate): An update resource
        session (Session): A DB session

    Returns:
        Configuration: A configuration resource
    """
    configs = get(session)

    result: Configuration = update_(current_user_id, configs, request, session)

    return result


def create_default_config() -> bool:
    """Create default service configuration resource

    Raises:
        exc: In case an unexpected error happens

    Returns:
        bool: Whether operation terminated OK
    """
    with Session(ENGINE) as session:
        configs = get_all(session)

        if len(configs) > 0:  # config table has been previously created
            return False

        now = str(datetime.utcnow())

        config = Configuration(
            created_at=now,
            created_by=CONFIG["users"]["default_admin"]["username"],
            modified_at=now,
            modified_by=CONFIG["users"]["default_admin"]["username"],
            id=str(uuid4()),
            check_email_deliverability=False,
        )

        try:
            session.add(config)
            session.commit()
            session.refresh(config)

            return True
        except Exception as exc:
            logger.exception(
                "An exc. ocurred when trying to create default service configurations = {}",
                str(exc),
            )
            raise exc
