import os
from distutils.util import strtobool
from typing import Any, Dict

CONFIG: Dict[str, Any] = {
    "service": {
        "token_url": "/fast-crud/auth/token",
        "prod_mode": strtobool(os.getenv("PROD_MODE", "False")),
    },
    "db": {
        "file_name": os.environ["DATABASE_FILE_NAME"],
        "url": f"sqlite:///{os.environ['DATABASE_FILE_NAME']}",
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
