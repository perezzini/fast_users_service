from typing import Any, Dict, Iterator

from fastapi import Depends
from fast_users_service.api.rest.enums import DBStatus
from fast_users_service.config import CONFIG
from fast_users_service.db import models  # noqa
from sqlmodel import Session, SQLModel, create_engine

ENGINE = create_engine(
    CONFIG["db"]["url"],
    echo=not CONFIG["service"]["prod_mode"],
    connect_args={"check_same_thread": False},
)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(ENGINE)


def get_session() -> Iterator[Session]:
    with Session(ENGINE) as session:
        yield session


def is_db_online(session: Session = Depends(get_session)) -> Dict[str, Any]:
    """Database health check status

    Args:
        session (Session, optional): A DB session. Defaults to Depends(get_session).

    Returns:
        Dict[str, Any]: Health check result
    """
    if session.is_active:
        return {"db_status": DBStatus.active}

    return {"db_status": DBStatus.inactive}
