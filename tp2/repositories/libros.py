# Se define el acceso a datos de libros

from typing import Sequence

from sqlmodel import col, select

from dependencies import SessionDep
from model.autores import Autor
from model.libros import Libro, LibroBase


class LibroRepository:
    def __init__(self, session: SessionDep):
        self.session = session

    def listar(self, offset: int = 0, limit: int = 100) -> Sequence[Libro]:
        statement = select(Libro).order_by(col(Libro.id)).offset(offset).limit(limit)
        return self.session.exec(statement).all()

    def obtener_por_id(self, libro_id: int) -> Libro | None:
        return self.session.get(Libro, libro_id)

    def obtener_por_isbn(self, isbn: str) -> Libro | None:
        statement = select(Libro).where(col(Libro.isbn) == isbn)
        return self.session.exec(statement).first()

    def crear(self, datos: LibroBase) -> Libro:
        libro = Libro.model_validate(datos)
        self.session.add(libro)
        self.session.commit()
        self.session.refresh(libro)
        return libro

    def actualizar(self, libro_id: int, datos: LibroBase) -> Libro | None:
        libro = self.session.get(Libro, libro_id)
        if libro is None:
            return None
        libro.titulo = datos.titulo
        libro.isbn = datos.isbn
        libro.stock = datos.stock
        libro.anio = datos.anio
        self.session.add(libro)
        self.session.commit()
        self.session.refresh(libro)
        return libro

    def eliminar(self, libro_id: int) -> bool:
        libro = self.session.get(Libro, libro_id)
        if libro is None:
            return False
        self.session.delete(libro)
        self.session.commit()
        return True

    def agregar_autor(self, libro: Libro, autor: Autor) -> Libro:
        if autor not in libro.autores:
            libro.autores.append(autor)
            self.session.add(libro)
            self.session.commit()
            self.session.refresh(libro)
        return libro
