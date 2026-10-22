from sqlmodel import Field, SQLModel
from sqlalchemy.orm import registry


class UserCenterBase(SQLModel, registry=registry()):
    pass


class Account(UserCenterBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, index=True, unique=True)
