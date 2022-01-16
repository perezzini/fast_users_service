from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, status
from jose import jwt
from loguru import logger
from fast_users_service.api.users import get_current_active_user
from fast_users_service.config import CONFIG
from fast_users_service.db.models import User
from passlib.context import CryptContext
from fast_users_service.utils import is_valid_uuid

PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain: str, hashed: str) -> Any:
    """Verify plain and hashed passwords

    Args:
        plain (str): A plain-text password
        hashed (str): A hashed password

    Returns:
        Any: Whether inputs match
    """
    return PWD_CONTEXT.verify(plain, hashed)


def get_password_hash(plain: str) -> str:
    """Hash plain password

    Args:
        plain (str): Plain-text password

    Returns:
        str: Hashed password
    """
    return PWD_CONTEXT.hash(plain)  # type: ignore


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Create access token

    Args:
        data (Dict[str, Any]): Payload data
        expires_delta (Optional[timedelta], optional): Exp delta. Defaults to None.

    Returns:
        str: A JWT
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=15
        )  # NOTE: add 15 mins as default

    to_encode.update(
        {"exp": int(expire.timestamp()), "iat": int(datetime.utcnow().timestamp())}
    )

    encoded_jwt = jwt.encode(
        to_encode,
        CONFIG["security"]["jwt"]["secret_key"],
        algorithm="HS256",
    )

    return encoded_jwt  # type: ignore


def is_admin(user: User = Depends(get_current_active_user)) -> None:
    """Checks whether user is admin

    Args:
        user (User, optional): A user. Defaults to Depends(get_current_active_user).

    Raises:
        HTTPException: In case user is not admin
    """
    if not user.is_admin:
        logger.warning(
            "Unauthorized operation execution for non admin user ID = {}",
            user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Operation not allowed for current user",
        )


def validate_db_key(value: str, exc_msg: Optional[str] = "Bad request") -> None:
    """Validate a DB pk or fk

    Args:
        value (str): A value representing a UUID to validate
        exc_msg (Optional[str], optional): Exception message. Defaults to "Bad request".

    Raises:
        HTTPException: [description]
    """
    if not is_valid_uuid(value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc_msg,
        )


def impersonate_admin_user() -> str:
    """Impersonate default admin user

    Returns:
        str: A JWT
    """
    access_token_expires = timedelta(minutes=int(CONFIG["security"]["jwt"]["ttl"]))
    access_token = create_access_token(
        data={
            "sub": CONFIG["users"]["default_admin"]["username"],
            "id": CONFIG["users"]["default_admin"]["id"],
        },
        expires_delta=access_token_expires,  # noqa
    )

    return access_token
