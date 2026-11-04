# Nivel de API

from sqlmodel import SQLModel

from model.autores import AutorBase


class CrearAutor(AutorBase):
    pass


class ActualizarAutor(AutorBase):
    pass


class AutorResponse(AutorBase):
    id: int
