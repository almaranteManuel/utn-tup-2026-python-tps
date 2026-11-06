# Router de préstamos

from typing import Sequence

from fastapi import APIRouter, HTTPException

from api.model.prestamos import RegistrarDevolucion, CrearPrestamo, PrestamoResponse
from dependencies import PrestamoServiceDep
from model.prestamos import Prestamo
from services.exceptions import (
    ConflictoError,
    DuplicadoError,
    NoPermitidoError,
    RecursoInexistenteError,
)

router = APIRouter(tags=["Préstamos"])


@router.post("/prestamos", response_model=PrestamoResponse, status_code=201)
def registrar_prestamo(datos: CrearPrestamo, service: PrestamoServiceDep) -> Prestamo:
    try:
        return service.prestar(datos.socio_id, datos.libro_id, datos.fecha_prestamo)
    except RecursoInexistenteError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except NoPermitidoError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e
    except (DuplicadoError, ConflictoError) as e:
        raise HTTPException(status_code=409, detail=str(e)) from e


@router.post(
    "/prestamos/{prestamo_id}/devolucion", response_model=PrestamoResponse
)
def registrar_devolucion(
    prestamo_id: int,
    service: PrestamoServiceDep,
    datos: RegistrarDevolucion | None = None,
) -> Prestamo:
    fecha = datos.fecha_devolucion if datos is not None else None
    try:
        return service.devolver(prestamo_id, fecha)
    except RecursoInexistenteError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except DuplicadoError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e


@router.get(
    "/socios/{socio_id}/prestamos", response_model=Sequence[PrestamoResponse]
)
def listar_prestamos_del_socio(
    socio_id: int,
    service: PrestamoServiceDep,
    activos: bool | None = None,
) -> Sequence[Prestamo]:
    try:
        return service.listar_del_socio(socio_id, activos)
    except RecursoInexistenteError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
