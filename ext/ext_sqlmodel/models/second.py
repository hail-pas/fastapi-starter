from sqlmodel import Field, SQLModel

from sqlalchemy.orm import registry

class SecondBase(SQLModel, registry=registry()):
    pass

class SecondTable1(SecondBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    a: str = Field(nullable=False, index=True, unique=True)
