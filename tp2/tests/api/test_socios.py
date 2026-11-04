# Tests del CRUD de socios

from fastapi.testclient import TestClient

SOCIO = {"nombre": "Ana Gomez", "email": "ana@email.com"}


def test_crear_socio(client: TestClient):
    response = client.post("/socios", json=SOCIO)
    assert response.status_code == 201
    socio = response.json()
    assert socio["id"] == 1
    assert socio["nombre"] == "Ana Gomez"
    assert socio["email"] == SOCIO["email"]
    # El socio queda activo de forma predeterminada
    assert socio["activo"] is True


def test_crear_socio_inactivo(client: TestClient):
    response = client.post("/socios", json=SOCIO | {"activo": False})
    assert response.status_code == 201
    assert response.json()["activo"] is False


def test_crear_socio_email_invalido(client: TestClient):
    response = client.post("/socios", json=SOCIO | {"email": "no-es-email"})
    assert response.status_code == 422


def test_crear_socio_email_duplicado(client: TestClient):
    client.post("/socios", json=SOCIO)

    response = client.post("/socios", json=SOCIO | {"nombre": "Otro"})
    assert response.status_code == 409
    assert response.json()["detail"] == f"Ya existe un socio con el email {SOCIO['email']}"


def test_listar_socios(client: TestClient):
    client.post("/socios", json=SOCIO)
    client.post("/socios", json=SOCIO | {"email": "beto@email.com"})

    response = client.get("/socios")
    assert response.status_code == 200
    socios = response.json()
    assert len(socios) == 2
    assert [s["id"] for s in socios] == [1, 2]


def test_listar_socios_vacio(client: TestClient):
    response = client.get("/socios")
    assert response.status_code == 200
    assert response.json() == []


def test_obtener_socio_por_id(client: TestClient):
    client.post("/socios", json=SOCIO)

    response = client.get("/socios/1")
    assert response.status_code == 200
    assert response.json()["nombre"] == "Ana Gomez"


def test_obtener_socio_inexistente(client: TestClient):
    response = client.get("/socios/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Socio no encontrado"


def test_actualizar_socio(client: TestClient):
    client.post("/socios", json=SOCIO)

    datos = SOCIO | {"nombre": "Ana I Gomez", "email": "ana2@email.com", "activo": False}
    response = client.patch("/socios/1", json=datos)
    assert response.status_code == 200
    socio = response.json()
    assert socio["nombre"] == "Ana I Gomez"
    assert socio["email"] == "ana2@email.com"
    assert socio["activo"] is False


def test_actualizar_socio_mismo_email(client: TestClient):
    client.post("/socios", json=SOCIO)

    # Renombrar el socio, aunque mantenga su email, no da error
    response = client.patch("/socios/1", json=SOCIO | {"nombre": "Ana I Gomez"})
    assert response.status_code == 200


def test_actualizar_socio_email_de_otro(client: TestClient):
    client.post("/socios", json=SOCIO)
    client.post("/socios", json=SOCIO | {"email": "beto@email.com"})

    response = client.patch("/socios/1", json=SOCIO | {"email": "beto@email.com"})
    assert response.status_code == 409
    assert response.json()["detail"] == "Ya existe un socio con el email beto@email.com"


def test_actualizar_socio_inexistente(client: TestClient):
    response = client.patch("/socios/999", json=SOCIO)
    assert response.status_code == 404


def test_eliminar_socio(client: TestClient):
    client.post("/socios", json=SOCIO)

    response = client.delete("/socios/1")
    assert response.status_code == 204

    # Ya no se puede obtener el socio eliminado
    assert client.get("/socios/1").status_code == 404
    assert client.get("/socios").json() == []


def test_eliminar_socio_inexistente(client: TestClient):
    response = client.delete("/socios/999")
    assert response.status_code == 404
