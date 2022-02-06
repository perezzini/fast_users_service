from datetime import timedelta
from typing import Union

from fastapi import HTTPException, status
from loguru import logger
from fast_users_service.api.rest.enums import TokenType
from fast_users_service.api.rest.models import Token
from fast_users_service.api.security import create_access_token, verify_password
from fast_users_service.api.users import get_all
from fast_users_service.config import CONFIG
from fast_users_service.db.models import User
from sqlmodel import Session


def authenticate_user(
    username: str, password: str, session: Session
) -> Union[bool, User]:
    """Verify username and password match

    Args:
        username (str): A username
        password (str): A plain-text password
        session (Session): A DB session

    Returns:
        Union[User, bool]: User in case username and password matches,
        or False in case username it is not found or
    """
    users = get_all(session)
    user = list(filter(lambda obj: obj.username == username, users))

    if not user:
        return False

    if not verify_password(password, user[0].password):
        return False

    return user[0]


def login(username: str, password: str, session: Session) -> Token:
    """Login user by its username and password, creating an
    access token

    Args:
        username (str): A username
        password (str): A password
        session (Session): A DB session

    Raises:
        HTTPException: In case user is not athenticated

    Returns:
        Token: An access token
    """
    user = authenticate_user(username, password, session)

    if not user:
        logger.warning("Unauthorized login attempt for username = {}", username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=int(CONFIG["security"]["jwt"]["ttl"]))
    access_token = create_access_token(
        data={"sub": user.username, "id": user.id}, expires_delta=access_token_expires  # type: ignore
    )

    return Token(access_token=access_token, token_type=TokenType.bearer)
