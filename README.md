# Trabajos Prácticos — UTN TUP 2026 (Python / FastAPI)

Repo con los trabajos prácticos de la materia, hechos con **FastAPI** y
**Pydantic**. Cada TP vive en su propia carpeta con su consigna, su README, sus
dependencias y su entorno virtual.

| Carpeta | TP | Descripción |
|---|---|---|
| [`tp1/`](./tp1/) | TP1 — ABM de usuarios y equipos | API con CRUD en memoria (FastAPI + Pydantic) |
| [`tp2/`](./tp2/) | TP2 — Sistema de biblioteca | API con entidades relacionadas (FastAPI + SQLModel). *En construcción.* |

## Cómo correr un TP

Cada TP es autocontenido: se arma su entorno virtual y se instala su
`requirements.txt` desde la carpeta del TP. Las instrucciones completas están
en el README de cada uno:

- [`tp1/README.md`](./tp1/README.md)
- [`tp2/README.md`](./tp2/README.md)

Estructura de cada carpeta:

```
tpX/
├── consigna.md        # Enunciado del trabajo
├── README.md          # Cómo correr / probar este TP
├── requirements.txt   # Dependencias del TP
├── main.py            # (TP2 aún no tiene código)
├── models/
└── routers/
```

## Lint y chequeo de tipos

Cada TP incluye la misma configuración:

- **`setup.cfg`**: configuración de [`pycodestyle`](https://pycodestyle.pycqa.org/) (estilo PEP 8, `max-line-length = 130`, excluye `.venv` y `__pycache__`).
- **`pyrightconfig.json`**: configuración de [`pyright`](https://microsoft.github.io/pyright/) (chequeo de tipos), apunta al venv propio del TP.

`pyright` ya está en el `requirements.txt` de cada TP. `pycodestyle` hay que
instalarlo aparte. Desde la carpeta del TP, con el venv activado:

```bash
pip install pycodestyle
python -m pycodestyle .
pyright
```
