from typing import Optional

from fast_users_service.api.rest.enums import (
    DBStatus,
    TokenType,
)
from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str = Field(description="Access token")
    token_type: TokenType = Field(description="Token type")


class TokenData(BaseModel):
    username: str = Field(description="Username")
    id: str = Field(description="User ID")
    expires_at: Optional[int] = Field(description="Token expires at")
    iat: int = Field(description="Token issued at")


class HealthResponse(BaseModel):
    db_status: DBStatus = Field(description="Whether DB is active")
