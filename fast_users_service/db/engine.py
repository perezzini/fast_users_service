from typing import Any, Dict, Iterator

from fastapi import Depends
from fast_users_service.api.rest.enums import DBStatus
from fast_users_service.config import CONFIG
from fast_users_service.db import models  # noqa
from sqlmodel import Session, SQLModel, create_engine, select

# NOTE: "echo" param must be set to False when in production mode
ENGINE = create_engine(
    CONFIG["db"]["url"],
    echo=not CONFIG["service"]["prod_mode"],
    # connect_args={"check_same_thread": False},  # NOTE: only works in SQLite
)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(ENGINE)


def get_session() -> Iterator[Session]:
    with Session(ENGINE) as session:
        yield session


def is_db_healthy(session: Session = Depends(get_session)) -> Dict[str, Any]:
    """Database health check status

    Args:
        session (Session, optional): A DB session. Defaults to Depends(get_session).

    Returns:
        Dict[str, Any]: Health check result
    """
    stmt = select(1)  # NOTE: trivial
    result = session.exec(stmt)

    return {"db_status": DBStatus.active if result else DBStatus.inactive}
