# Se define el modelo de socios

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class SocioBase(SQLModel):
    nombre: str = Field(index=True)
    email: EmailStr = Field(unique=True, index=True)
    activo: bool = True


class Socio(SocioBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
