from datetime import date

from sqlmodel import SQLModel


class CrearPrestamo(SQLModel):
    socio_id: int
    libro_id: int
    # Sin fecha se usa la fecha de hoy.
    fecha_prestamo: date | None = None


class RegistrarDevolucion(SQLModel):
    # Sin fecha se usa la fecha de hoy.
    fecha_devolucion: date | None = None


class PrestamoResponse(SQLModel):
    id: int
    socio_id: int
    libro_id: int
    fecha_prestamo: date
    fecha_vencimiento: date
    fecha_devolucion: date | None
    multa: int
