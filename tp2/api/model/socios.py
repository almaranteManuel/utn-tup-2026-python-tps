from sqlmodel import SQLModel

from model.socios import SocioBase


class CrearSocio(SocioBase):
    pass


class ActualizarSocio(SocioBase):
    pass


class SocioResponse(SocioBase):
    id: int
