# TP2: Sistema de biblioteca (FastAPI + SQLModel)

API REST para administrar el catálogo de una biblioteca y sus socios:
entidades **Autor**, **Libro** y **Socio** con CRUD completo, validaciones de
negocio y una base de datos SQLite.

- 📄 Consigna: [`consigna.md`](./consigna.md)

- 🚧 **Estado - Etapas 1 y 2 completadas: "CRUD y modelos" + "Relaciones".**
  Restan: préstamos con sus reglas de negocio y la cobertura de tests de
  negocio. Préstamos y autenticación no se implementan todavía.

> Modelo de datos actual:
>
> | Entidad | Campos |
> |---|---|
> | `Autor` | id, nombre, nacionalidad |
> | `Libro` | id, titulo, isbn (único), stock (≥ 0), anio (0-2100) |
> | `Socio` | id, nombre, email (único), activo (default `true`) |
> | `LibroAutor` | libro_id, autor_id (tabla intermedia de la relación N-N) |
>
> Relación: **Libro N-N Autor** — un libro puede tener varios autores y un
> autor varios libros. Las respuestas de `/libros` incluyen la lista de
> `autores` de cada libro.

## Notas de esta etapa

- La base de datos es SQLite (`database.db`), creada con todas sus tablas al
  arrancar la aplicación.
- Los tests usan SQLite **en memoria** (`StaticPool`) para no tocar el archivo
  `database.db` del entorno.

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

### Códigos de respuesta y errores

- `201` en la creación de cualquier recurso.
- `204` al eliminar.
- `404` cuando el recurso no existe (también con el detalle específico si
  falta el libro o el autor al asociar).
- `409` cuando el ISBN de un libro o el email de un socio ya se usó, o si el
  autor ya estaba asociado al libro.
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
│   ├── libros.py              #   LibroBase / Libro
│   └── socios.py              #   SocioBase / Socio
├── api/                       # Routers (capa HTTP, delgados)
│   ├── autores.py
│   ├── libros.py
│   ├── socios.py
│   └── model/                 # Schemas de entrada/salida (nivel API)
│       ├── autores.py         #   CrearAutor / ActualizarAutor / AutorResponse
│       ├── libros.py
│       └── socios.py
├── services/                  # Lógica de negocio (chequeo de duplicados: 409)
│   ├── autores.py             #   AutorServiceInterface + AutorService
│   ├── libros.py
│   ├── socios.py
│   └── exceptions.py          #   DuplicadoError
├── repositories/              # Acceso a datos con SQLModel
│   ├── database.py            #   engine SQLite, create_db_and_tables, get_session
│   ├── autores.py
│   ├── libros.py
│   └── socios.py
└── tests/                     # pytest + SQLite en memoria (StaticPool)
    ├── conftest.py
    └── api/
        ├── test_autores.py
        ├── test_libros.py
        └── test_socios.py
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

## Próximas etapas (según la consigna)

3. **Préstamos:** reglas de negocio en la capa `services`.
4. **Tests de negocio:** pytest con base en memoria, cobertura ≥ 80 %.
5. **Opcional:** roles `bibliotecario` y `socio`.
