from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fast_users_service.api.auth import login as login_user
from fast_users_service.api.rest.models import Token
from fast_users_service.db.engine import get_session
from sqlmodel import Session

ROUTER = APIRouter()


@ROUTER.post("/token", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
) -> Token:
    return login_user(form_data.username, form_data.password, session)
