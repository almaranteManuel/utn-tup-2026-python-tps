# Clase FastAPI

Clase para aprender **FastAPI** y **Pydantic**.

## Crear el entorno virtual (venv)

Desde esta carpeta (`clase-fastapi`):

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
fastapi dev main.py
```

La API quedará disponible en `http://127.0.0.1:8000` y la documentación
interactiva en `http://127.0.0.1:8000/docs`.

## Endpoints disponibles

Los datos se guardan en memoria, por lo que se reinician al detener la
aplicación.

### Usuarios

- `GET /user`: lista todos los usuarios.
- `GET /user?is_active=true` o `GET /user?is_active=false`: filtra por estado.
- `GET /user/{id}`: obtiene un usuario.
- `POST /user`: crea un usuario.
- `PUT /user/{id}`: reemplaza los datos de un usuario.
- `DELETE /user/{id}`: elimina un usuario.

Ejemplo de usuario para `POST /user`:

```json
{
  "id": 3,
  "name": "Ana Gomez",
  "is_active": true
}
```

### Equipos de fútbol

`Equipo` tiene cinco campos: `id`, `name`, `city`, `stadium` y
`founded_year`.

- `GET /team`: lista todos los equipos.
- `GET /team?city=Buenos%20Aires`: filtra por ciudad, sin distinguir
  mayúsculas y minúsculas.
- `GET /team/{id}`: obtiene un equipo.
- `POST /team`: crea un equipo.
- `PUT /team/{id}`: reemplaza los datos de un equipo.
- `DELETE /team/{id}`: elimina un equipo.

Ejemplo de equipo para `POST /team`:

```json
{
  "id": 3,
  "name": "Belgrano",
  "city": "Cordoba",
  "stadium": "Julio Cesar Villagra",
  "founded_year": 1905
}
```

La forma más sencilla de probar todas las operaciones es abrir `/docs`,
seleccionar un endpoint, pulsar **Try it out**, completar los datos y ejecutar
la solicitud.

## Lint y chequeo de tipos

El proyecto incluye configuración local para dos herramientas:

- **[`setup.cfg`](./setup.cfg)**: configuración de [`pycodestyle`](https://pycodestyle.pycqa.org/) (chequeo de estilo PEP 8). Define `max-line-length = 79` y excluye `.venv` y `__pycache__` del análisis.
- **[`pyrightconfig.json`](./pyrightconfig.json)**: configuración de [`pyright`](https://microsoft.github.io/pyright/) (chequeo de tipos). Apunta al entorno virtual local (`.venv`) para resolver las dependencias instaladas y excluye `.venv` y `__pycache__`.

`pyright` ya está incluido en `requirements.txt`. `pycodestyle` no, así que hay que instalarlo aparte.

Con el entorno virtual activado, correr:

```bash
pip install pycodestyle
python -m pycodestyle .
```

```bash
pyright
```