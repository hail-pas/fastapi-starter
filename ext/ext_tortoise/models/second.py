from tortoise import fields

from ext.ext_tortoise.main import ConnectionNameEnum
from ext.ext_tortoise.base.models import BaseModel


class SecondTable1(BaseModel):
    a = fields.CharField(max_length=10, description="a")
    b = fields.CharField(max_length=10, description="b")

    class Meta:
        table_description = "Second Table 1"
        ordering = ["-id"]
        app = ConnectionNameEnum.second.value
