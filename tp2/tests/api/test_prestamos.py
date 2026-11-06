from datetime import date, timedelta

from fastapi.testclient import TestClient

SOCIO = {"nombre": "Ana Gomez", "email": "ana@email.com"}
LIBRO = {"titulo": "Ficciones", "isbn": "9789875664070", "stock": 5, "anio": 1944}
FECHA = "2026-06-01"  # vencimiento 2026-06-15


def crear_socio(client: TestClient, **cambios) -> dict:
    response = client.post("/socios", json=SOCIO | cambios)
    assert response.status_code == 201, response.text
    return response.json()


def crear_libro(client: TestClient, **cambios) -> dict:
    response = client.post("/libros", json=LIBRO | cambios)
    assert response.status_code == 201, response.text
    return response.json()


def prestar(client: TestClient, socio_id: int, libro_id: int) -> dict:
    response = client.post(
        "/prestamos", json={"socio_id": socio_id, "libro_id": libro_id, "fecha_prestamo": FECHA}
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_registrar_prestamo(client: TestClient):
    socio = crear_socio(client)
    libro = crear_libro(client)

    response = client.post(
        "/prestamos", json={"socio_id": socio["id"], "libro_id": libro["id"], "fecha_prestamo": FECHA}
    )
    assert response.status_code == 201, response.text
    prestamo = response.json()
    assert prestamo["socio_id"] == socio["id"]
    assert prestamo["libro_id"] == libro["id"]
    assert prestamo["fecha_prestamo"] == FECHA
    # Regla 4: vencimiento a 14 días
    assert prestamo["fecha_vencimiento"] == "2026-06-15"
    assert prestamo["fecha_devolucion"] is None
    assert prestamo["multa"] == 0


def test_registrar_prestamo_sin_fecha_usa_hoy(client: TestClient):
    socio = crear_socio(client)
    libro = crear_libro(client)

    response = client.post("/prestamos", json={"socio_id": socio["id"], "libro_id": libro["id"]})
    assert response.status_code == 201, response.text
    prestamo = response.json()
    hoy = date.today()
    assert prestamo["fecha_prestamo"] == hoy.isoformat()
    vence = hoy + timedelta(days=14)
    assert prestamo["fecha_vencimiento"] == vence.isoformat()


def test_registrar_prestamo_socio_inexistente(client: TestClient):
    libro = crear_libro(client)
    response = client.post(
        "/prestamos", json={"socio_id": 999, "libro_id": libro["id"], "fecha_prestamo": FECHA}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Socio no encontrado"


def test_registrar_prestamo_libro_inexistente(client: TestClient):
    socio = crear_socio(client)
    response = client.post(
        "/prestamos", json={"socio_id": socio["id"], "libro_id": 999, "fecha_prestamo": FECHA}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Libro no encontrado"


def test_registrar_prestamo_socio_inactivo(client: TestClient):
    # Regla 3: socio inactivo
    socio = crear_socio(client, activo=False)
    libro = crear_libro(client)
    response = client.post(
        "/prestamos", json={"socio_id": socio["id"], "libro_id": libro["id"], "fecha_prestamo": FECHA}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Un socio inactivo no puede pedir préstamos"


def test_registrar_prestamo_libro_sin_stock(client: TestClient):
    # Regla 2: sin stock
    socio = crear_socio(client)
    libro = crear_libro(client, stock=0)
    response = client.post(
        "/prestamos", json={"socio_id": socio["id"], "libro_id": libro["id"], "fecha_prestamo": FECHA}
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "El libro Ficciones no tiene stock disponible"


def test_prestamo_descuenta_stock(client: TestClient):
    # Regla 2: al prestar se descuenta 1
    socio = crear_socio(client)
    libro = crear_libro(client, stock=3)
    prestar(client, socio["id"], libro["id"])

    libro_actualizado = client.get(f"/libros/{libro['id']}").json()
    assert libro_actualizado["stock"] == 2


def test_max_tres_prestamos_activos(client: TestClient):
    # Regla 1: máx. 3 activos
    socio = crear_socio(client)
    libros = [
        crear_libro(client, isbn=str(9780000000000 + n), stock=1) for n in range(1, 5)
    ]
    for libro in libros[:3]:
        prestar(client, socio["id"], libro["id"])

    response = client.post(
        "/prestamos",
        json={"socio_id": socio["id"], "libro_id": libros[3]["id"], "fecha_prestamo": FECHA},
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "El socio ya tiene el máximo de 3 préstamos activos"


def test_limite_cuenta_solo_prestamos_activos(client: TestClient):
    socio = crear_socio(client)
    libros = [
        crear_libro(client, isbn=str(9780000000000 + n), stock=1) for n in range(1, 4)
    ]
    prestamo_devuelto = prestar(client, socio["id"], libros[0]["id"])
    prestar(client, socio["id"], libros[1]["id"])

    # Al devolver uno, se vuelve a abrir lugar para otro préstamo (stock repuesto)
    response = client.post(f"/prestamos/{prestamo_devuelto['id']}/devolucion")
    assert response.status_code == 200

    response = client.post(
        "/prestamos",
        json={"socio_id": socio["id"], "libro_id": libros[0]["id"], "fecha_prestamo": FECHA},
    )
    assert response.status_code == 201, response.text


def test_devolver_prestamo_con_multa(client: TestClient):
    # Regla 5: $100 por día de atraso
    socio = crear_socio(client)
    libro = crear_libro(client, stock=1)
    prestamo = prestar(client, socio["id"], libro["id"])

    response = client.post(
        f"/prestamos/{prestamo['id']}/devolucion", json={"fecha_devolucion": "2026-06-18"}
    )
    assert response.status_code == 200, response.text
    devuelto = response.json()
    assert devuelto["fecha_devolucion"] == "2026-06-18"
    assert devuelto["multa"] == 300

    # Al devolver se repone el stock
    libro_actualizado = client.get(f"/libros/{libro['id']}").json()
    assert libro_actualizado["stock"] == 1


def test_devolver_prestamo_a_tiempo_no_genera_multa(client: TestClient):
    socio = crear_socio(client)
    libro = crear_libro(client)
    prestamo = prestar(client, socio["id"], libro["id"])

    response = client.post(
        f"/prestamos/{prestamo['id']}/devolucion", json={"fecha_devolucion": "2026-06-10"}
    )
    assert response.status_code == 200
    assert response.json()["multa"] == 0


def test_registrar_devolucion_sin_body_usa_hoy(client: TestClient):
    socio = crear_socio(client)
    libro = crear_libro(client)
    # Préstamo vencido hace 6 días: 20 - 14
    client.post(
        "/prestamos",
        json={
            "socio_id": socio["id"],
            "libro_id": libro["id"],
            "fecha_prestamo": (date.today() - timedelta(days=20)).isoformat(),
        },
    )
    prestamo = client.get(f"/socios/{socio['id']}/prestamos").json()[0]

    response = client.post(f"/prestamos/{prestamo['id']}/devolucion")
    assert response.status_code == 200
    assert response.json()["fecha_devolucion"] == date.today().isoformat()
    assert response.json()["multa"] == 600


def test_devolver_prestamo_inexistente(client: TestClient):
    response = client.post("/prestamos/999/devolucion")
    assert response.status_code == 404
    assert response.json()["detail"] == "Préstamo no encontrado"


def test_devolver_prestamo_ya_devuelto(client: TestClient):
    # Regla 6: no se devuelve dos veces
    socio = crear_socio(client)
    libro = crear_libro(client)
    prestamo = prestar(client, socio["id"], libro["id"])
    client.post(f"/prestamos/{prestamo['id']}/devolucion")

    response = client.post(f"/prestamos/{prestamo['id']}/devolucion")
    assert response.status_code == 409
    assert response.json()["detail"] == "El préstamo ya fue devuelto"


def test_listar_prestamos_del_socio(client: TestClient):
    socio = crear_socio(client)
    otro = crear_socio(client, email="beto@email.com")
    libro_a = crear_libro(client)
    libro_b = crear_libro(client, isbn="9789500727303")
    prestar(client, socio["id"], libro_a["id"])
    prestar(client, socio["id"], libro_b["id"])
    prestar(client, otro["id"], libro_b["id"])

    # Solo los préstamos del socio pedido
    response = client.get(f"/socios/{socio['id']}/prestamos")
    assert response.status_code == 200
    prestamos = response.json()
    assert len(prestamos) == 2
    assert [p["libro_id"] for p in prestamos] == [libro_a["id"], libro_b["id"]]

    # Filtro activos=false devuelve solo el devuelto
    client.post(f"/prestamos/{prestamos[0]['id']}/devolucion")
    response = client.get(f"/socios/{socio['id']}/prestamos", params={"activos": "false"})
    assert response.status_code == 200
    assert [p["id"] for p in response.json()] == [prestamos[0]["id"]]


def test_listar_prestamos_del_socio_filtro_activos(client: TestClient):
    socio = crear_socio(client)
    libro_a = crear_libro(client)
    libro_b = crear_libro(client, isbn="9789500727303")
    prestar(client, socio["id"], libro_a["id"])
    prestar(client, socio["id"], libro_b["id"])

    response = client.get(f"/socios/{socio['id']}/prestamos", params={"activos": "true"})
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_listar_prestamos_socio_inexistente(client: TestClient):
    response = client.get("/socios/999/prestamos")
    assert response.status_code == 404
    assert response.json()["detail"] == "Socio no encontrado"
