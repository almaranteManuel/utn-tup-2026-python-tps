# TP2: Sistema de biblioteca (FastAPI + SQLModel)

API REST para gestionar el catálogo de una biblioteca y sus préstamos:
entidades con relaciones, reglas de negocio y códigos HTTP correctos.

- 📄 Consigna: [`consigna.md`](./consigna.md)

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

> El `requirements.txt` de este TP incluye **FastAPI** y **SQLModel**, la
> base de datos que pide la consigna. A medida que el TP avance se agregan
> las dependencias nuevas ahí.

## Ejecutar la aplicación

Cuando exista el código (`main.py`), se corre igual que en el TP1:

```bash
fastapi dev main.py
```

La API queda disponible en `http://127.0.0.1:8000` y la documentación
interactiva en `http://127.0.0.1:8000/docs`.

## Chequeo previo de la consigna

Lo primero del TP es leer la consigna completa: modelo de datos
(`Autor`, `Libro`, `LibroAutor`, `Socio`, `Prestamo`), endpoints mínimos y
reglas de negocio con sus códigos de error.
