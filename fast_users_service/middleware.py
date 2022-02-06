from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def configure_cors(app: FastAPI) -> None:
    """Configure CORS middleware

    Args:
        app (FastAPI): A FastAPI app
    """
    # TODO: properties allow_* must be review'd
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # all origins
        allow_credentials=True,
        allow_methods=["*"],  # all methods
        allow_headers=["*"],  # all headers
    )
