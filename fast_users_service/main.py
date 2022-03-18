import uvicorn
from fastapi import FastAPI
from loguru import logger

from fast_users_service.api.configurations import create_default_config
from fast_users_service.api.rest.router import setup as setup_routers
from fast_users_service.api.security import get_password_hash
from fast_users_service.api.users import create_admin
from fast_users_service.config import CONFIG
from fast_users_service.db.engine import create_db_and_tables
from fast_users_service.logger import configure
from fast_users_service.middleware import configure_cors

APP = FastAPI(title="FastUSERS API")


@APP.on_event("startup")
def startup() -> None:
    logger.info("Cofiguring CORS middleware...")
    configure_cors(APP)

    logger.info("Creating DB and tables...")
    create_db_and_tables()

    if create_default_config():
        logger.info(
            "Default configuration properties created. username = {}",
            CONFIG["users"]["default_admin"]["username"],
        )
    else:
        logger.info(
            "Default configuration properties already created. username = {}",
            CONFIG["users"]["default_admin"]["username"],
        )

    if create_admin(get_password_hash):
        logger.info(
            "Admin created. username = {}", CONFIG["users"]["default_admin"]["username"]
        )
    else:
        logger.info(
            "Admin already created. username = {}",
            CONFIG["users"]["default_admin"]["username"],
        )

    logger.info("Setting-up routers...")
    setup_routers(APP)

    logger.info("Service has been started")


def main() -> None:
    configure()

    logger.info("Starting-up API services...")
    # start-up web server
    uvicorn.run(
        "fast_users_service.main:APP",
        host="0.0.0.0",
        port=8000,
    )
    logger.info("Started API services")


if __name__ == "__main__":
    main()
