# Se define el acceso a datos de autores

from typing import Sequence

from sqlmodel import col, select

from dependencies import SessionDep
from model.autores import Autor, AutorBase


class AutorRepository:
    def __init__(self, session: SessionDep):
        self.session = session

    def listar(self, offset: int = 0, limit: int = 100) -> Sequence[Autor]:
        statement = select(Autor).order_by(col(Autor.id)).offset(offset).limit(limit)
        return self.session.exec(statement).all()

    def obtener_por_id(self, autor_id: int) -> Autor | None:
        return self.session.get(Autor, autor_id)

    def crear(self, datos: AutorBase) -> Autor:
        autor = Autor.model_validate(datos)
        self.session.add(autor)
        self.session.commit()
        self.session.refresh(autor)
        return autor

    def actualizar(self, autor_id: int, datos: AutorBase) -> Autor | None:
        autor = self.session.get(Autor, autor_id)
        if autor is None:
            return None
        autor.nombre = datos.nombre
        autor.nacionalidad = datos.nacionalidad
        self.session.add(autor)
        self.session.commit()
        self.session.refresh(autor)
        return autor

    def eliminar(self, autor_id: int) -> bool:
        autor = self.session.get(Autor, autor_id)
        if autor is None:
            return False
        self.session.delete(autor)
        self.session.commit()
        return True
