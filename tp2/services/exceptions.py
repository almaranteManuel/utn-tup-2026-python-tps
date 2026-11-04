# acá defino las excepciones de la capa de servicios

class DuplicadoError(Exception):
    pass


# La entidad solicitada no existe (libro, autor, socio, etc.).
class RecursoInexistenteError(Exception):
    pass
