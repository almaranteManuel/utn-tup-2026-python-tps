from datetime import date
from typing import Sequence

from sqlmodel import col, select

from dependencies import SessionDep
from model.libros import Libro
from model.prestamos import Prestamo


class PrestamoRepository:
    def __init__(self, session: SessionDep):
        self.session = session

    def listar_del_socio(
        self, socio_id: int, activos: bool | None = None
    ) -> Sequence[Prestamo]:
        statement = (
            select(Prestamo)
            .where(col(Prestamo.socio_id) == socio_id)
            .order_by(col(Prestamo.id))
        )
        if activos is True:
            statement = statement.where(col(Prestamo.fecha_devolucion).is_(None))
        if activos is False:
            statement = statement.where(col(Prestamo.fecha_devolucion).is_not(None))
        return self.session.exec(statement).all()

    def contar_activos(self, socio_id: int) -> int:
        statement = (
            select(Prestamo)
            .where(col(Prestamo.socio_id) == socio_id)
            .where(col(Prestamo.fecha_devolucion).is_(None))
        )
        return len(self.session.exec(statement).all())

    def obtener_por_id(self, prestamo_id: int) -> Prestamo | None:
        return self.session.get(Prestamo, prestamo_id)

    def crear(self, prestamo: Prestamo, libro: Libro) -> Prestamo:
        # Al prestar se descuenta 1 del stock del libro.
        libro.stock -= 1
        self.session.add(prestamo)
        self.session.add(libro)
        self.session.commit()
        self.session.refresh(prestamo)
        self.session.refresh(libro)
        return prestamo

    def devolver(self, prestamo: Prestamo, fecha_devolucion: date, multa: int) -> Prestamo:
        # Al devolver se repone el stock del libro.
        prestamo.fecha_devolucion = fecha_devolucion
        prestamo.multa = multa
        libro = self.session.get(Libro, prestamo.libro_id)
        if libro is not None:
            libro.stock += 1
            self.session.add(libro)
        self.session.add(prestamo)
        self.session.commit()
        self.session.refresh(prestamo)
        self.session.refresh(libro)
        return prestamo
