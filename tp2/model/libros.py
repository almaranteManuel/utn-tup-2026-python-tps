# Se define el modelo de libros

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel


class LibroBase(SQLModel):
    titulo: str = Field(index=True)
    isbn: str = Field(unique=True, index=True)
    stock: int = Field(ge=0)
    anio: int = Field(ge=0, le=2100)


class LibroAutor(SQLModel, table=True):
    libro_id: int | None = Field(default=None, foreign_key="libro.id", primary_key=True)
    autor_id: int | None = Field(default=None, foreign_key="autor.id", primary_key=True)


class Libro(LibroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    autores: list["Autor"] = Relationship(back_populates="libros", link_model=LibroAutor)


if TYPE_CHECKING:
    from model.autores import Autor
