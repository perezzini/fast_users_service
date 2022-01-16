from fastapi import FastAPI
from fastapi_health import health
from fast_users_service.api.rest import (
    addresses,
    auth,
    configurations,
    users,
)
from fast_users_service.api.rest.models import HealthResponse
from fast_users_service.db.engine import is_db_online


def setup(app: FastAPI) -> None:
    app.include_router(auth.ROUTER, prefix="/fast-crud/auth", tags=["Auth"])
    app.include_router(
        addresses.ROUTER, prefix="/fast-crud/addresses", tags=["Addresses"]
    )
    app.include_router(users.ROUTER, prefix="/fast-crud/users", tags=["Users"])
    app.include_router(
        configurations.ROUTER,
        prefix="/fast-crud/configurations",
        tags=["Service configs"],
    )
    app.add_api_route(  # NOTE: review this
        "/fast-crud/health",
        health([is_db_online]),
        tags=["Health"],
        response_model=HealthResponse,
    )
