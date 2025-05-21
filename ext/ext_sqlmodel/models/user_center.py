from sqlalchemy.orm import registry
from sqlmodel import Field, SQLModel


class UserCenterBase(SQLModel, registry=registry()):
    pass


class Account(UserCenterBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, index=True, unique=True)
