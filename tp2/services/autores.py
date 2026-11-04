# acá defino la lógica de negocio de autores

from abc import ABC, abstractmethod
from typing import Sequence

from dependencies import AutorRepositoryDep
from model.autores import Autor, AutorBase


class AutorServiceInterface(ABC):
    @abstractmethod
    def listar(self, offset: int = 0, limit: int = 100) -> Sequence[Autor]:
        ...

    @abstractmethod
    def obtener_por_id(self, autor_id: int) -> Autor | None:
        ...

    @abstractmethod
    def crear(self, datos: AutorBase) -> Autor:
        ...

    @abstractmethod
    def actualizar(self, autor_id: int, datos: AutorBase) -> Autor | None:
        ...

    @abstractmethod
    def eliminar(self, autor_id: int) -> bool:
        ...


class AutorService(AutorServiceInterface):
    def __init__(self, repo: AutorRepositoryDep):
        self.repo = repo

    def listar(self, offset: int = 0, limit: int = 100) -> Sequence[Autor]:
        return self.repo.listar(offset, limit)

    def obtener_por_id(self, autor_id: int) -> Autor | None:
        return self.repo.obtener_por_id(autor_id)

    def crear(self, datos: AutorBase) -> Autor:
        return self.repo.crear(datos)

    def actualizar(self, autor_id: int, datos: AutorBase) -> Autor | None:
        return self.repo.actualizar(autor_id, datos)

    def eliminar(self, autor_id: int) -> bool:
        return self.repo.eliminar(autor_id)
