from typing import Any, Dict, Optional, Type
from uuid import uuid4

from fast_users_service.api.rest.enums import PasswordPolicyStrength
from sqlmodel import Field, SQLModel
from sqlmodel.main import Relationship


class Auditable(SQLModel):
    created_at: Optional[str] = Field(
        description="The resource creation timestamp", default=None
    )
    modified_at: Optional[str] = Field(
        description="The resource last modification timestamp", default=None
    )
    created_by: Optional[str] = Field(
        description="The user who created the resource", default=None
    )
    modified_by: Optional[str] = Field(
        description="The user who last modified the resource", default=None
    )
    deleted: bool = Field(
        default=False, description="Whether resource has been deleted"
    )
    deleted_at: Optional[str] = Field(
        description="Timestamp when the resource was deleted", default=None
    )
    deleted_by: Optional[str] = Field(
        description="User ID who deleted the resource", default=None
    )


class ResourceTable(Auditable):
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid4()),
        primary_key=True,
    )


class ResourceTableDBResponse(SQLModel):
    id: str
    created_at: Optional[str] = Field(
        description="The resource creation timestamp", default=None
    )
    modified_at: Optional[str] = Field(
        description="The resource last modification timestamp", default=None
    )
    created_by: Optional[str] = Field(
        description="The user who created the resource", default=None
    )
    modified_by: Optional[str] = Field(
        description="The user who last modified the resource", default=None
    )


class UserBase(SQLModel):
    username: str = Field(
        description="User's email to use as username",
        sa_column_kwargs={"unique": True},
        index=True,
    )
    password: str = Field(description="User's password")
    name: str = Field(description="Full name of the user")
    first_name: Optional[str] = Field(description="First name", default=None)
    middle_name: Optional[str] = Field(description="Middle name", default=None)
    last_name: Optional[str] = Field(description="Last name", default=None)
    is_blocked: Optional[bool] = Field(
        default=False,
        description="Whether user is currently blocked",
    )
    last_access_at: Optional[str] = Field(
        description="Timestamp of last entry", default=None
    )
    is_admin: bool = Field(description="Whether user is admin", default=False)
    address_id: Optional[str] = Field(
        description="Client full-address", foreign_key="address.id"
    )


class UserCreate(UserBase):
    class Config:
        @staticmethod
        def schema_extra(schema: Dict[str, Any], model: Type["UserCreate"]) -> None:
            if "properties" in schema:
                # hide internal-use properties from public API
                schema["properties"].pop("is_admin")
                schema["properties"].pop("last_access_at")


class User(ResourceTable, UserBase, table=True):
    address: Optional["Address"] = Relationship(back_populates="user")


class UserUpdate(SQLModel):
    name: Optional[str] = Field(description="Full name of the user", default=None)
    password: str = Field(description="User's password")
    first_name: Optional[str] = Field(description="First name", default=None)
    middle_name: Optional[str] = Field(description="Middle name", default=None)
    last_name: Optional[str] = Field(description="Last name", default=None)
    is_blocked: Optional[bool] = Field(
        default=False,
        description="Whether user is currently blocked",
    )
    address_id: Optional[str] = Field(description="User's full-address")


class UserResponseBase(ResourceTableDBResponse):
    username: str = Field(
        description="User's email to use as username",
        sa_column_kwargs={"unique": True},
        index=True,
    )
    name: str = Field(description="Full name of the user")
    first_name: Optional[str] = Field(description="First name", default=None)
    middle_name: Optional[str] = Field(description="Middle name", default=None)
    last_name: Optional[str] = Field(description="Last name", default=None)
    is_blocked: Optional[bool] = Field(
        default=False,
        description="Whether user is currently blocked",
    )
    last_access_at: Optional[str] = Field(
        description="Timestamp of last entry", default=None
    )
    is_admin: bool = Field(description="Whether user is admin", default=False)
    address_id: Optional[str] = Field(description="Client full-address")


class UserResponse(UserResponseBase):
    pass


class ConfigurationBase(SQLModel):
    check_email_deliverability: Optional[bool] = Field(
        default=False,
        description="Whether to check email deliverability when creating/updating resources where an email address is present",  # noqa
    )
    password_policy_strength: PasswordPolicyStrength = Field(
        default=PasswordPolicyStrength.min,
        description="Password policy strength. 'min' refers to a password of length, at least, 8 chars; 'max' refers to a password of, at least, length 8 and 1 uppercase and 1 number",  # noqa
    )
    jwt_auto_refresh: Optional[bool] = Field(
        default=False, description="Whether to auto-refresh security token"
    )


class ConfigurationCreate(ConfigurationBase):
    pass


class ConfigurationUpdate(SQLModel):
    check_email_deliverability: Optional[bool] = Field(
        default=False,
        description="Whether to check email deliverability when creating/updating resources where an email address is present",  # noqa
    )
    password_policy_strength: Optional[PasswordPolicyStrength] = Field(
        default=None,
        description="Password policy strength. 'min' refers to a password of length, at least, 8 chars; 'max' refers to a password of, at least, length 8 and 1 uppercase and 1 number",  # noqa
    )


class Configuration(ResourceTable, Auditable, ConfigurationBase, table=True):
    pass


class ConfigurationResponseBase(ResourceTableDBResponse, ConfigurationBase):
    pass


class ConfigurationResponse(ConfigurationBase):
    pass


class AddressBase(SQLModel):
    postal_code: Optional[str] = Field(default=None, description="Postal code")
    address: str = Field(description="Full plain-text address")
    country: str = Field(description="Address' country")
    state: str = Field(description="Address' state")
    city: str = Field(description="Address' city")
    lat: Optional[float] = Field(default=None, description="Address' latitude")
    lon: Optional[float] = Field(default=None, description="Address' longitude")


class Address(ResourceTable, AddressBase, table=True):
    user: Optional["User"] = Relationship(back_populates="address")


class AddressCreate(AddressBase):
    pass


class AddressResponseBase(ResourceTableDBResponse, AddressBase):
    pass


class AddressUpdate(SQLModel):
    postal_code: Optional[str] = Field(default=None, description="Postal code")
    address: Optional[str] = Field(default=None, description="Full plain-text address")
    country: Optional[str] = Field(default=None, description="Address' country")
    state: Optional[str] = Field(default=None, description="Address' state")
    city: Optional[str] = Field(default=None, description="Address' city")
    lat: Optional[float] = Field(default=None, description="Address' latitude")
    lon: Optional[float] = Field(default=None, description="Address' longitude")


class AddressResponse(AddressResponseBase):
    pass
