from datetime import datetime, timedelta
from typing import Callable, List, Optional

from email_validator import EmailNotValidError, validate_email
from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from loguru import logger
from fast_users_service.api.configurations import get as get_config
from fast_users_service.api.rest.enums import PasswordPolicyStrength
from fast_users_service.api.rest.models import TokenData
from fast_users_service.config import CONFIG
from fast_users_service.db.engine import ENGINE, get_session
from fast_users_service.db.models import Configuration, User, UserCreate, UserUpdate
from fast_users_service.db.transactions import create as create_
from fast_users_service.db.transactions import delete as delete_
from fast_users_service.db.transactions import update as update_
from password_strength import PasswordPolicy
from sqlmodel import Session, select

CREDS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl=CONFIG["service"]["token_url"])


def create(
    user: UserCreate,
    session: Session,
    current_user_id: str,
    hash_func: Callable,
    admin: Optional[bool] = False,
) -> User:
    """Create user

    Args:
        user (UserCreate): Set of user properties
        session (Session): A DB session
        hash_func (Callable): A hash function

    Returns:
        UserResponse: Created user
    """
    # retrieve service configs
    config: Configuration = get_config(session)

    if config.password_policy_strength == PasswordPolicyStrength.min:
        pwd_policy = PasswordPolicy.from_names(length=8)
    else:
        pwd_policy = PasswordPolicy.from_names(length=8, uppercase=1, numbers=1)

    if not pwd_policy.test(user.password) == []:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password not strong enough: must have at least 8 chars (1 uppercase letter, and 1 number)"
            if config.password_policy_strength == PasswordPolicyStrength.max
            else "Password not strong enough: must have at least 8 chars",
        )

    if not admin:  # TODO: review this
        try:
            validate_email(
                user.username, check_deliverability=config.check_email_deliverability
            )
        except EmailNotValidError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
            )

    user.password = hash_func(user.password)

    user_: User = User.from_orm(user)

    if admin:  # TODO: review this
        user_.id = current_user_id  # replace auto-generated ID

    result: User = create_(user_, session, current_user_id)

    return result


def get_all(
    session: Session,
    start: Optional[int] = None,
    end: Optional[int] = None,
    show_deleted_records: Optional[bool] = False,
) -> List[User]:
    """Get users based on given query params

    Args:
        session (Session): A DB session
        start (Optional[int], optional): Start index. Defaults to None.
        end (Optional[int], optional): End index. Defaults to None.
        show_deleted_records (Optional[bool], optional): Whether to respond with deleted records.
        Defaults to False.

    Raises:
        HTTPException: In case invalid query params are given

    Returns:
        List[User]: A list of users
    """
    if end and start and end < start:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid query params"
        )

    stmt = select(User).where(User.deleted == show_deleted_records)
    results = session.exec(stmt)
    users = results.all()

    if not start:
        start = 0

    return users[start : start + end] if end else users[start:]  # noqa


def get(id: str, session: Session) -> User:
    """Retrieve a user by its ID

    Args:
        id (str): An ID
        session (Session): A DB session

    Returns:
        User: A user
    """
    user = session.get(User, id)

    if not user or user and user.deleted:
        logger.info("Not found username ID = {}", id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


def update(
    id: str,
    request: UserUpdate,
    session: Session,
    hash_func: Callable,
    current_user_id: str,
) -> User:
    """Update a user by its ID

    Args:
        id (str): User ID
        request (UserUpdate): A user update request
        session (Session): A DB session
        hash_func (Callable): A hashing function
        current_user_id (str): Current user ID

    Returns:
        User: A user
    """
    if id == CONFIG["users"]["default_admin"]["id"]:
        logger.error("Tried to udate admin user ID")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="'admin' user cannot be updated",
        )

    user = get(id, session)

    if request.password:
        request.password = hash_func(request.password)

    result: User = update_(current_user_id, user, request, session)

    return result


def delete(id: str, session: Session, current_user_id: str) -> None:
    """Delete a user by its ID

    Args:
        id (str): A user ID
        session (Session): A DB session
        current_user_id (str): Current user ID

    Raises:
        HTTPException: In case current user tries to delete himself
    """
    if id == CONFIG["users"]["default_admin"]["id"]:
        logger.error("Tried to udate admin user ID")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="'admin' user cannot be deleted",
        )

    if id == current_user_id:
        logger.info("Tried to delete self, user ID = {}", current_user_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete current user"
        )

    user = get(id, session)

    delete_(user, session, current_user_id)


def create_admin(hash_func: Callable) -> bool:
    """Create admin if it has not been created
    before

    Args:
        hash_func (Callable): A hashing function

    Raises:
        exc: In case somthing wrong happens when
        creating user

    Returns:
        bool: False, in case admin has been created
        beforehand; True, in case admin had to be
        created
    """
    with Session(ENGINE) as session:
        users = get_all(session)

        admin_search = list(
            filter(
                lambda user: user.username
                == CONFIG["users"]["default_admin"]["username"],
                users,
            )
        )

        if admin_search:  # root admin has been previously created
            return False

        user = UserCreate(
            **{
                "username": CONFIG["users"]["default_admin"]["username"],
                "name": CONFIG["users"]["default_admin"]["username"],
                "password": CONFIG["users"]["default_admin"]["password"],
                "is_admin": True,
            }
        )

        try:
            create(
                user,
                session,
                CONFIG["users"]["default_admin"]["id"],
                hash_func,
                admin=True,
            )

            return True
        except Exception as exc:
            # logger.exception(
            #     "An exc. ocurred when trying to create admin user = {}", str(exc)
            # )
            raise exc


def get_current_user(
    token: str = Depends(OAUTH2_SCHEME), session: Session = Depends(get_session)
) -> User:
    """Get current user

    Args:
        token (str, optional): Security token. Defaults to Depends(OAUTH2_SCHEME).
        session (Session, optional): A DB session. Defaults to Depends(get_session).

    Raises:
        creds_exception: In case credentials fail

    Returns:
        User: A user
    """
    # retrieve service configs
    config: Configuration = get_config(session)

    try:
        payload = jwt.decode(
            token,
            CONFIG["security"]["jwt"]["secret_key"],
            algorithms=["HS256"],
        )
        username: str = payload.get("sub")
        user_id: str = payload.get("id")
        token_expires_at = payload.get("exp")
        token_iat = payload.get("iat")

        if username is None or user_id is None:  # FIXME: bad constructed predicate
            raise CREDS_EXCEPTION

        # check token expiration
        if token_expires_at is None:
            raise CREDS_EXCEPTION
        if (
            int(datetime.utcnow().timestamp()) > token_expires_at
        ):  # TODO: review this block
            raise CREDS_EXCEPTION

        token_data = TokenData(
            username=username, id=user_id, exp=token_expires_at, iat=token_iat
        )

    except ExpiredSignatureError:  # TODO: review this block
        if config.jwt_auto_refresh:
            logger.warning("JWT token expired, but refreshing...")
            token_data = TokenData(
                username=username,
                id=user_id,
                exp=datetime.utcnow() + timedelta(minutes=15),
            )
        else:
            raise CREDS_EXCEPTION
    except JWTError as exc:
        logger.error("A JWT error occurred = {}", str(exc))
        raise CREDS_EXCEPTION

    try:
        user = get(token_data.id, session)
    except Exception as exc:
        logger.exception(
            "An exc. occurred when trying to get user from DB = {}", str(exc)
        )
        raise CREDS_EXCEPTION

    # update last access ts
    user.last_access_at = str(datetime.utcnow())
    session.add(user)
    session.commit()
    session.refresh(user)

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Check whether current user is active. In case it is blocked, raise an exc

    Args:
        current_user (User, optional): Current user. Defaults to Depends(get_current_user).

    Raises:
        HTTPException: In case current user is blocked

    Returns:
        User: Current user
    """
    if current_user.is_blocked:
        logger.info("Current user ID is not active = {}", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    return current_user
