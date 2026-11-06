from abc import ABC, abstractmethod
from typing import Sequence

from dependencies import AutorRepositoryDep, LibroRepositoryDep
from model.libros import Libro, LibroBase
from model.autores import Autor
from services.exceptions import DuplicadoError, RecursoInexistenteError


class LibroServiceInterface(ABC):
    @abstractmethod
    def listar(self, offset: int = 0, limit: int = 100) -> Sequence[Libro]:
        ...

    @abstractmethod
    def obtener_por_id(self, libro_id: int) -> Libro | None:
        ...

    @abstractmethod
    def crear(self, datos: LibroBase) -> Libro:
        ...

    @abstractmethod
    def actualizar(self, libro_id: int, datos: LibroBase) -> Libro | None:
        ...

    @abstractmethod
    def eliminar(self, libro_id: int) -> bool:
        ...

    @abstractmethod
    def agregar_autor(self, libro_id: int, autor_id: int) -> Libro:
        ...


class LibroService(LibroServiceInterface):
    def __init__(self, repo: LibroRepositoryDep, repo_autores: AutorRepositoryDep):
        self.repo = repo
        self.repo_autores = repo_autores

    def listar(self, offset: int = 0, limit: int = 100) -> Sequence[Libro]:
        return self.repo.listar(offset, limit)

    def obtener_por_id(self, libro_id: int) -> Libro | None:
        return self.repo.obtener_por_id(libro_id)

    def crear(self, datos: LibroBase) -> Libro:
        self._validar_isbn_disponible(datos.isbn)
        return self.repo.crear(datos)

    def actualizar(self, libro_id: int, datos: LibroBase) -> Libro | None:
        existente = self.repo.obtener_por_isbn(datos.isbn)
        if existente is not None and existente.id != libro_id:
            raise DuplicadoError(f"Ya existe un libro con el ISBN {datos.isbn}")
        return self.repo.actualizar(libro_id, datos)

    def eliminar(self, libro_id: int) -> bool:
        return self.repo.eliminar(libro_id)

    def agregar_autor(self, libro_id: int, autor_id: int) -> Libro:
        libro = self.repo.obtener_por_id(libro_id)
        if libro is None:
            raise RecursoInexistenteError("Libro no encontrado")

        autor = self.repo_autores.obtener_por_id(autor_id)
        if autor is None:
            raise RecursoInexistenteError("Autor no encontrado")

        if autor in libro.autores:
            raise DuplicadoError(
                f"El autor {autor.nombre} ya está asociado al libro {libro.titulo}"
            )
        return self.repo.agregar_autor(libro, autor)

    def _validar_isbn_disponible(self, isbn: str) -> None:
        existente = self.repo.obtener_por_isbn(isbn)
        if existente is not None:
            raise DuplicadoError(f"Ya existe un libro con el ISBN {isbn}")
