from fastapi import FastAPI
from fastapi_health import health
from fast_users_service.api.rest import (
    addresses,
    auth,
    configurations,
    users,
)
from fast_users_service.api.rest.models import HealthResponse
from fast_users_service.db.engine import is_db_healthy


def setup(app: FastAPI) -> None:
    """Set up routers

    Args:
        app (FastAPI): A fastAPI object
    """
    app.include_router(auth.ROUTER, prefix="/fast-users/auth", tags=["Auth"])
    app.include_router(
        addresses.ROUTER, prefix="/fast-users/addresses", tags=["Addresses"]
    )
    app.include_router(users.ROUTER, prefix="/fast-users/users", tags=["Users"])
    app.include_router(
        configurations.ROUTER,
        prefix="/fast-users/configurations",
        tags=["Service configs"],
    )
    app.add_api_route(  # NOTE: review this
        "/fast-users/health",
        health([is_db_healthy]),
        tags=["Health"],
        response_model=HealthResponse,
    )
