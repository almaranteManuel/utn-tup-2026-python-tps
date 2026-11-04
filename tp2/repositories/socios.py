# Se define el acceso a datos de socios

from typing import Sequence

from sqlmodel import col, select

from dependencies import SessionDep
from model.socios import Socio, SocioBase


class SocioRepository:
    def __init__(self, session: SessionDep):
        self.session = session

    def listar(self, offset: int = 0, limit: int = 100) -> Sequence[Socio]:
        statement = select(Socio).order_by(col(Socio.id)).offset(offset).limit(limit)
        return self.session.exec(statement).all()

    def obtener_por_id(self, socio_id: int) -> Socio | None:
        return self.session.get(Socio, socio_id)

    def obtener_por_email(self, email: str) -> Socio | None:
        statement = select(Socio).where(col(Socio.email) == email)
        return self.session.exec(statement).first()

    def crear(self, datos: SocioBase) -> Socio:
        socio = Socio.model_validate(datos)
        self.session.add(socio)
        self.session.commit()
        self.session.refresh(socio)
        return socio

    def actualizar(self, socio_id: int, datos: SocioBase) -> Socio | None:
        socio = self.session.get(Socio, socio_id)
        if socio is None:
            return None
        socio.nombre = datos.nombre
        socio.email = datos.email
        socio.activo = datos.activo
        self.session.add(socio)
        self.session.commit()
        self.session.refresh(socio)
        return socio

    def eliminar(self, socio_id: int) -> bool:
        socio = self.session.get(Socio, socio_id)
        if socio is None:
            return False
        self.session.delete(socio)
        self.session.commit()
        return True
