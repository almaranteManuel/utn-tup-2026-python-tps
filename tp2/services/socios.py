from abc import ABC, abstractmethod
from typing import Sequence

from dependencies import SocioRepositoryDep
from model.socios import Socio, SocioBase
from services.exceptions import DuplicadoError


class SocioServiceInterface(ABC):
    @abstractmethod
    def listar(self, offset: int = 0, limit: int = 100) -> Sequence[Socio]:
        ...

    @abstractmethod
    def obtener_por_id(self, socio_id: int) -> Socio | None:
        ...

    @abstractmethod
    def crear(self, datos: SocioBase) -> Socio:
        ...

    @abstractmethod
    def actualizar(self, socio_id: int, datos: SocioBase) -> Socio | None:
        ...

    @abstractmethod
    def eliminar(self, socio_id: int) -> bool:
        ...


class SocioService(SocioServiceInterface):
    def __init__(self, repo: SocioRepositoryDep):
        self.repo = repo

    def listar(self, offset: int = 0, limit: int = 100) -> Sequence[Socio]:
        return self.repo.listar(offset, limit)

    def obtener_por_id(self, socio_id: int) -> Socio | None:
        return self.repo.obtener_por_id(socio_id)

    def crear(self, datos: SocioBase) -> Socio:
        self._validar_email_disponible(datos.email)
        return self.repo.crear(datos)

    def actualizar(self, socio_id: int, datos: SocioBase) -> Socio | None:
        existente = self.repo.obtener_por_email(datos.email)
        if existente is not None and existente.id != socio_id:
            raise DuplicadoError(f"Ya existe un socio con el email {datos.email}")
        return self.repo.actualizar(socio_id, datos)

    def eliminar(self, socio_id: int) -> bool:
        return self.repo.eliminar(socio_id)

    def _validar_email_disponible(self, email: str) -> None:
        existente = self.repo.obtener_por_email(email)
        if existente is not None:
            raise DuplicadoError(f"Ya existe un socio con el email {email}")
