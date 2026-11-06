from sqlmodel import SQLModel

from api.model.autores import AutorResponse
from model.libros import LibroBase


class CrearLibro(LibroBase):
    pass


class ActualizarLibro(LibroBase):
    pass


class LibroResponse(LibroBase):
    id: int
    autores: list[AutorResponse] = []
