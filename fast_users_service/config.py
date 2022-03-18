import os
from distutils.util import strtobool
from typing import Any, Dict

CONFIG: Dict[str, Any] = {
    "service": {
        "token_url": "/fast-users/auth/token",
        "prod_mode": strtobool(os.getenv("PROD_MODE", "False")),
    },
    "db": {
        "url": f"postgresql://{os.environ['POSTGRES_USERNAME']}:{os.environ['POSTGRES_PSW']}@{os.environ['POSTGRES_SERVER']}:{os.getenv('POSTGRES_PORT', '5432')}/users",  # noqa
    },
    "security": {
        "jwt": {
            "secret_key": os.environ["JWT_SECRET_KEY"],
            "ttl": os.getenv("JWT_TTL", 30),
        }
    },
    "users": {
        "default_admin": {
            "id": "admin",
            "username": "admin",
            "password": os.environ["ADMIN_PSW"],
        }
    },
}
