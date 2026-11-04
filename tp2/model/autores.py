# Se define el modelo de autores

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from model.libros import LibroAutor

if TYPE_CHECKING:
    from model.libros import Libro


class AutorBase(SQLModel):
    nombre: str = Field(index=True)
    nacionalidad: str


class Autor(AutorBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    libros: list["Libro"] = Relationship(back_populates="autores", link_model=LibroAutor)
