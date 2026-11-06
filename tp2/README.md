# TP2: Sistema de biblioteca (FastAPI + SQLModel)

API REST para administrar el catálogo de una biblioteca y sus socios:
entidades **Autor**, **Libro** y **Socio** con CRUD completo, validaciones de
negocio y una base de datos SQLite.

- 📄 Consigna: [`consigna.md`](./consigna.md)


> Modelo de datos actual:
>
> | Entidad | Campos |
> |---|---|
> | `Autor` | id, nombre, nacionalidad |
> | `Libro` | id, titulo, isbn (único), stock (≥ 0), anio (0-2100) |
> | `Socio` | id, nombre, email (único), activo (default `true`) |
> | `LibroAutor` | libro_id, autor_id (tabla intermedia de la relación N-N) |
> | `Prestamo` | id, socio_id, libro_id, fecha_prestamo, fecha_vencimiento, fecha_devolucion (nullable), multa |
>
> Relaciones: **Libro N-N Autor** (un libro puede tener varios autores y un
> autor varios libros; las respuestas de `/libros` incluyen la lista de
> `autores` de cada libro) y **Prestamo N-1 Socio** / **Prestamo N-1 Libro**.

## Crear el entorno virtual (venv)

Desde esta carpeta (`tp2/`):

```bash
python3 -m venv .venv
```

Activar el entorno virtual:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

## Instalar los requerimientos

Con el entorno virtual activado:

```bash
pip install -r requirements.txt
```

## Ejecutar la aplicación

```bash
uvicorn main:app --reload
```

La API queda disponible en `http://127.0.0.1:8000` y la documentación
interactiva en `http://127.0.0.1:8000/docs`.

## Endpoints disponibles

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/autores` | Lista autores (con paginación `offset` / `limit`) |
| GET | `/autores/{id}` | Obtiene un autor |
| POST | `/autores` | Crea un autor |
| PATCH | `/autores/{id}` | Reemplaza los datos de un autor |
| DELETE | `/autores/{id}` | Elimina un autor |
| GET | `/libros` | Lista libros |
| GET | `/libros/{id}` | Obtiene un libro |
| POST | `/libros` | Crea un libro |
| PATCH | `/libros/{id}` | Reemplaza los datos de un libro |
| DELETE | `/libros/{id}` | Elimina un libro |
| POST | `/libros/{id}/autores/{autor_id}` | Asocia un autor a un libro |
| GET | `/socios` | Lista socios |
| GET | `/socios/{id}` | Obtiene un socio |
| POST | `/socios` | Crea un socio |
| PATCH | `/socios/{id}` | Reemplaza los datos de un socio |
| DELETE | `/socios/{id}` | Elimina un socio |
| GET | `/socios/{id}/prestamos` | Préstamos del socio (filtro `activos=true|false`) |
| POST | `/prestamos` | Registra un préstamo |
| POST | `/prestamos/{id}/devolucion` | Registra la devolución (fecha opcional) |

Un préstamo sin `fecha_prestamo` (o una devolución sin `fecha_devolucion`)
usa la fecha de hoy.

### Reglas de negocio de préstamos

| # | Regla | Error |
|---|---|---|
| 1 | Máximo 3 préstamos activos por socio | 409 |
| 2 | No se presta un libro sin stock; al prestar se descuenta 1 | 409 |
| 3 | Un socio inactivo no puede pedir préstamos | 403 |
| 4 | Plazo de 14 días (`fecha_vencimiento = fecha_prestamo + 14`) | n/a |
| 5 | Al devolver se repone el stock y se multa $100 por día de atraso | n/a |
| 6 | No se puede devolver un préstamo ya devuelto | 409 |

### Códigos de respuesta y errores

- `201` en la creación de cualquier recurso.
- `204` al eliminar.
- `403` cuando un socio inactivo intenta pedir un préstamo.
- `404` cuando el recurso no existe (también con el detalle específico si
  falta el libro o el autor al asociar).
- `409` cuando el ISBN de un libro o el email de un socio ya se usó, si el
  autor ya estaba asociado al libro, si no hay stock, si el socio llegó al
  máximo de préstamos activos o si el préstamo ya fue devuelto.
- `422` cuando los datos violan los modelos (stock negativo, año fuera de
  rango, email inválido, etc.).

### Ejemplos de uso

Ejemplo de JSON de cada entidad en `POST` / `PATCH`:

```bash
curl -X POST http://127.0.0.1:8000/autores -H 'Content-Type: application/json' -d '{"nombre": "Borges", "nacionalidad": "Argentina"}'
curl -X POST http://127.0.0.1:8000/libros -H 'Content-Type: application/json' -d '{"titulo": "Ficciones", "isbn": "9789875664070", "stock": 5, "anio": 1944}'
curl -X POST http://127.0.0.1:8000/socios -H 'Content-Type: application/json' -d '{"nombre": "Ana Gomez", "email": "ana@email.com"}'
```

La forma más sencilla de probar todas las operaciones es abrir `/docs`,
seleccionar un endpoint, pulsar **Try it out**, completar los datos y ejecutar
la solicitud.

## Correr los tests

```bash
pytest
```

Con coverage:

```bash
pytest --cov=api --cov=model --cov=services --cov=repositories --cov-report=term-missing
```

Los tests usan en `tests/conftest.py` una base de datos SQLite **en memoria**
(`sqlite://` + `StaticPool`) que no toca `database.db`; la sesión del
repositorio se reemplaza con `dependency_overrides`. La forma más sencilla de
probar todas las operaciones manualmente es abrir `/docs`, seleccionar un
endpoint, pulsar **Try it out**, completar los datos y ejecutar la solicitud.

## Estructura del proyecto

```
tp2/
├── consigna.md                # Enunciado del trabajo
├── README.md
├── requirements.txt           # Dependencias (versionadas)
├── setup.cfg                  # Config de pycodestyle (PEP 8)
├── pyrightconfig.json         # Config de pyright (chequeo de tipos)
├── main.py                    # App FastAPI: lifespan (crea tablas) + routers
├── dependencies.py            # Deps compartidas: SessionDep, RepoDep, ServiceDep
├── model/                     # Tablas SQLModel (nivel DB)
│   ├── autores.py             #   AutorBase / Autor
│   ├── libros.py              #   LibroBase / Libro / LibroAutor
│   ├── socios.py              #   SocioBase / Socio
│   └── prestamos.py           #   Prestamo
├── api/                       # Routers (capa HTTP, delgados)
│   ├── autores.py
│   ├── libros.py
│   ├── socios.py
│   ├── prestamos.py
│   └── model/                 # Schemas de entrada/salida (nivel API)
│       ├── autores.py         #   CrearAutor / ActualizarAutor / AutorResponse
│       ├── libros.py
│       ├── socios.py
│       └── prestamos.py       #   CrearPrestamo / RegistrarDevolucion / PrestamoResponse
├── services/                  # Lógica de negocio (reglas de la consigna)
│   ├── autores.py             #   AutorServiceInterface + AutorService
│   ├── libros.py
│   ├── socios.py
│   ├── prestamos.py           #   plazos, stock, límite de préstamos, multas
│   └── exceptions.py          #   RecursoInexistenteError / DuplicadoError / ConflictoError / NoPermitidoError
├── repositories/              # Acceso a datos con SQLModel
│   ├── database.py            #   engine SQLite, create_db_and_tables, get_session
│   ├── autores.py
│   ├── libros.py
│   ├── socios.py
│   └── prestamos.py
└── tests/                     # pytest + SQLite en memoria (StaticPool)
    ├── conftest.py
    └── api/
        ├── test_autores.py
        ├── test_libros.py
        ├── test_socios.py
        └── test_prestamos.py
```

Cada caso de un flujo con las **capas** del ejemplo `clase-1-sqlmodel`:

```
HTTP -> api/ (router) -> services/ (negocio) -> repositories/ (datos) -> SQLite
```

## Lint y chequeo de tipos

- **[`setup.cfg`](./setup.cfg)**: configuración de [`pycodestyle`](https://pycodestyle.pycqa.org/) (estilo PEP 8, `max-line-length = 130`, excluye `.venv` y `__pycache__`).
- **[`pyrightconfig.json`](./pyrightconfig.json)**: configuración de [`pyright`](https://microsoft.github.io/pyright/). Apunta al entorno virtual local (`.venv`).

`pyright` ya está incluido en `requirements.txt`. `pycodestyle` no, así que hay
que instalarlo aparte. Con el entorno virtual activado, correr:

```bash
pip install pycodestyle
python -m pycodestyle .
pyright
```
