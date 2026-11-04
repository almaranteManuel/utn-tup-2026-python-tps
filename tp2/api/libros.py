# Router de libros

from typing import Annotated, Sequence

from fastapi import APIRouter, HTTPException, Query

from api.model.libros import ActualizarLibro, CrearLibro, LibroResponse
from dependencies import LibroServiceDep
from model.libros import Libro
from services.exceptions import DuplicadoError, RecursoInexistenteError

router = APIRouter(prefix="/libros", tags=["Libros"])


@router.get("", response_model=Sequence[LibroResponse])
def listar_libros(
    service: LibroServiceDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> Sequence[Libro]:
    return service.listar(offset, limit)


@router.get("/{libro_id}", response_model=LibroResponse)
def obtener_libro_por_id(libro_id: int, service: LibroServiceDep) -> Libro:
    libro = service.obtener_por_id(libro_id)
    if libro is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return libro


@router.post("", response_model=LibroResponse, status_code=201)
def crear_libro(datos: CrearLibro, service: LibroServiceDep) -> Libro:
    try:
        return service.crear(datos)
    except DuplicadoError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e


@router.patch("/{libro_id}", response_model=LibroResponse)
def actualizar_libro(
    libro_id: int, datos: ActualizarLibro, service: LibroServiceDep
) -> Libro:
    try:
        libro = service.actualizar(libro_id, datos)
    except DuplicadoError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    if libro is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return libro


@router.post("/{libro_id}/autores/{autor_id}", response_model=LibroResponse)
def agregar_autor_a_libro(
    libro_id: int, autor_id: int, service: LibroServiceDep
) -> Libro:
    try:
        return service.agregar_autor(libro_id, autor_id)
    except RecursoInexistenteError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except DuplicadoError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e


@router.delete("/{libro_id}", status_code=204)
def eliminar_libro(libro_id: int, service: LibroServiceDep) -> None:
    if not service.eliminar(libro_id):
        raise HTTPException(status_code=404, detail="Libro no encontrado")
