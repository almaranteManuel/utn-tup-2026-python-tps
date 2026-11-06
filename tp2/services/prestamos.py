from abc import ABC, abstractmethod
from datetime import date, timedelta
from typing import Sequence

from dependencies import LibroRepositoryDep, PrestamoRepositoryDep, SocioRepositoryDep
from model.prestamos import Prestamo
from services.exceptions import (
    ConflictoError,
    DuplicadoError,
    NoPermitidoError,
    RecursoInexistenteError,
)

# Reglas de negocio de la consigna
PLAZO_DIAS = 14
MULTA_DIARIA = 100
MAX_PRESTAMOS_ACTIVOS = 3


class PrestamoServiceInterface(ABC):
    @abstractmethod
    def prestar(
        self, socio_id: int, libro_id: int, fecha_prestamo: date | None = None
    ) -> Prestamo:
        ...

    @abstractmethod
    def devolver(
        self, prestamo_id: int, fecha_devolucion: date | None = None
    ) -> Prestamo:
        ...

    @abstractmethod
    def listar_del_socio(
        self, socio_id: int, activos: bool | None = None
    ) -> Sequence[Prestamo]:
        ...


class PrestamoService(PrestamoServiceInterface):
    def __init__(
        self,
        repo_prestamos: PrestamoRepositoryDep,
        repo_libros: LibroRepositoryDep,
        repo_socios: SocioRepositoryDep,
    ):
        self.repo_prestamos = repo_prestamos
        self.repo_libros = repo_libros
        self.repo_socios = repo_socios

    # Regla 4: el plazo es de 14 días desde fecha_prestamo.
    def prestar(
        self, socio_id: int, libro_id: int, fecha_prestamo: date | None = None
    ) -> Prestamo:
        socio = self.repo_socios.obtener_por_id(socio_id)
        if socio is None:
            raise RecursoInexistenteError("Socio no encontrado")

        # Regla 3: un socio inactivo no puede pedir préstamos.
        if not socio.activo:
            raise NoPermitidoError("Un socio inactivo no puede pedir préstamos")

        libro = self.repo_libros.obtener_por_id(libro_id)
        if libro is None:
            raise RecursoInexistenteError("Libro no encontrado")

        # Regla 1: un socio no puede tener más de 3 préstamos activos.
        activos = self.repo_prestamos.contar_activos(socio_id)
        if activos >= MAX_PRESTAMOS_ACTIVOS:
            raise ConflictoError(
                f"El socio ya tiene el máximo de {MAX_PRESTAMOS_ACTIVOS} préstamos activos"
            )

        # Regla 2: no se presta un libro sin stock.
        if libro.stock <= 0:
            raise ConflictoError(f"El libro {libro.titulo} no tiene stock disponible")

        fecha = fecha_prestamo or date.today()
        prestamo = Prestamo(
            socio_id=socio_id,
            libro_id=libro_id,
            fecha_prestamo=fecha,
            fecha_vencimiento=fecha + timedelta(days=PLAZO_DIAS),
        )
        return self.repo_prestamos.crear(prestamo, libro)

    def devolver(
        self, prestamo_id: int, fecha_devolucion: date | None = None
    ) -> Prestamo:
        prestamo = self.repo_prestamos.obtener_por_id(prestamo_id)
        if prestamo is None:
            raise RecursoInexistenteError("Préstamo no encontrado")

        # Regla 6: no se puede devolver un préstamo ya devuelto.
        if prestamo.fecha_devolucion is not None:
            raise DuplicadoError("El préstamo ya fue devuelto")

        fecha = fecha_devolucion or date.today()

        # Regla 5: multa de $100 por cada día de atraso (0 si llegó a tiempo).
        atraso = (fecha - prestamo.fecha_vencimiento).days
        multa = max(0, atraso) * MULTA_DIARIA
        return self.repo_prestamos.devolver(prestamo, fecha, multa)

    def listar_del_socio(
        self, socio_id: int, activos: bool | None = None
    ) -> Sequence[Prestamo]:
        socio = self.repo_socios.obtener_por_id(socio_id)
        if socio is None:
            raise RecursoInexistenteError("Socio no encontrado")
        return self.repo_prestamos.listar_del_socio(socio_id, activos)
