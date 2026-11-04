# Router de autores

from typing import Annotated, Sequence

from fastapi import APIRouter, HTTPException, Query

from api.model.autores import ActualizarAutor, AutorResponse, CrearAutor
from dependencies import AutorServiceDep
from model.autores import Autor
from services.exceptions import DuplicadoError

router = APIRouter(prefix="/autores", tags=["Autores"])


@router.get("", response_model=Sequence[AutorResponse])
def listar_autores(
    service: AutorServiceDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> Sequence[Autor]:
    return service.listar(offset, limit)


@router.get("/{autor_id}", response_model=AutorResponse)
def obtener_autor_por_id(autor_id: int, service: AutorServiceDep) -> Autor:
    autor = service.obtener_por_id(autor_id)
    if autor is None:
        raise HTTPException(status_code=404, detail="Autor no encontrado")
    return autor


@router.post("", response_model=AutorResponse, status_code=201)
def crear_autor(datos: CrearAutor, service: AutorServiceDep) -> Autor:
    try:
        return service.crear(datos)
    except DuplicadoError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e


@router.patch("/{autor_id}", response_model=AutorResponse)
def actualizar_autor(
    autor_id: int, datos: ActualizarAutor, service: AutorServiceDep
) -> Autor:
    try:
        autor = service.actualizar(autor_id, datos)
    except DuplicadoError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    if autor is None:
        raise HTTPException(status_code=404, detail="Autor no encontrado")
    return autor


@router.delete("/{autor_id}", status_code=204)
def eliminar_autor(autor_id: int, service: AutorServiceDep) -> None:
    if not service.eliminar(autor_id):
        raise HTTPException(status_code=404, detail="Autor no encontrado")
