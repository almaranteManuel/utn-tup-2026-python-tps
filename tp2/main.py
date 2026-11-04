import model.autores  # noqa: F401
import model.libros  # noqa: F401
import model.socios  # noqa: F401
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api import autores, libros, socios
from repositories.database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Al iniciar la aplicación se crean las tablas en SQLite.
    create_db_and_tables()
    yield


app = FastAPI(title="TP2 - Sistema de Biblioteca", lifespan=lifespan)

app.include_router(autores.router)
app.include_router(libros.router)
app.include_router(socios.router)


# Define a GET route for the root URL
@app.get("/")
def read_root():
    mensaje = "Sistema de biblioteca con FastAPI y SQLModel"
    return {"message": mensaje}
