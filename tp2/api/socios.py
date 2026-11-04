# Router de socios

from typing import Annotated, Sequence

from fastapi import APIRouter, HTTPException, Query

from api.model.socios import ActualizarSocio, CrearSocio, SocioResponse
from dependencies import SocioServiceDep
from model.socios import Socio
from services.exceptions import DuplicadoError

router = APIRouter(prefix="/socios", tags=["Socios"])


@router.get("", response_model=Sequence[SocioResponse])
def listar_socios(
    service: SocioServiceDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> Sequence[Socio]:
    return service.listar(offset, limit)


@router.get("/{socio_id}", response_model=SocioResponse)
def obtener_socio_por_id(socio_id: int, service: SocioServiceDep) -> Socio:
    socio = service.obtener_por_id(socio_id)
    if socio is None:
        raise HTTPException(status_code=404, detail="Socio no encontrado")
    return socio


@router.post("", response_model=SocioResponse, status_code=201)
def crear_socio(datos: CrearSocio, service: SocioServiceDep) -> Socio:
    try:
        return service.crear(datos)
    except DuplicadoError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e


@router.patch("/{socio_id}", response_model=SocioResponse)
def actualizar_socio(
    socio_id: int, datos: ActualizarSocio, service: SocioServiceDep
) -> Socio:
    try:
        socio = service.actualizar(socio_id, datos)
    except DuplicadoError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    if socio is None:
        raise HTTPException(status_code=404, detail="Socio no encontrado")
    return socio


@router.delete("/{socio_id}", status_code=204)
def eliminar_socio(socio_id: int, service: SocioServiceDep) -> None:
    if not service.eliminar(socio_id):
        raise HTTPException(status_code=404, detail="Socio no encontrado")
