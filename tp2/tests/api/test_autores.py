from fastapi.testclient import TestClient


def test_crear_autor(client: TestClient):
    datos = {"nombre": "Jorge Luis Borges", "nacionalidad": "Argentina"}
    response = client.post("/autores", json=datos)
    assert response.status_code == 201
    autor = response.json()
    assert autor["id"] == 1
    assert autor["nombre"] == "Jorge Luis Borges"
    assert autor["nacionalidad"] == "Argentina"


def test_crear_autor_sin_nacionalidad(client: TestClient):
    response = client.post("/autores", json={"nombre": "Gabriel Garcia Marquez"})
    assert response.status_code == 422


def test_listar_autores(client: TestClient):
    client.post("/autores", json={"nombre": "Borges", "nacionalidad": "Argentina"})
    client.post("/autores", json={"nombre": "Cortazar", "nacionalidad": "Argentina"})

    response = client.get("/autores")
    assert response.status_code == 200
    autores = response.json()
    assert len(autores) == 2
    assert [a["id"] for a in autores] == [1, 2]

    # Limita la lista a un solo resultado
    response = client.get("/autores", params={"limit": 1})
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_listar_autores_vacio(client: TestClient):
    response = client.get("/autores")
    assert response.status_code == 200
    assert response.json() == []


def test_obtener_autor_por_id(client: TestClient):
    client.post("/autores", json={"nombre": "Borges", "nacionalidad": "Argentina"})

    response = client.get("/autores/1")
    assert response.status_code == 200
    assert response.json()["nombre"] == "Borges"


def test_obtener_autor_inexistente(client: TestClient):
    response = client.get("/autores/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Autor no encontrado"


def test_actualizar_autor(client: TestClient):
    client.post("/autores", json={"nombre": "Borges", "nacionalidad": "Argentina"})

    response = client.patch(
        "/autores/1", json={"nombre": "Jorge Luis Borges", "nacionalidad": "Uruguay"}
    )
    assert response.status_code == 200
    autor = response.json()
    assert autor["id"] == 1
    assert autor["nombre"] == "Jorge Luis Borges"
    assert autor["nacionalidad"] == "Uruguay"


def test_actualizar_autor_inexistente(client: TestClient):
    response = client.patch(
        "/autores/999", json={"nombre": "Nadie", "nacionalidad": "Ninguna"}
    )
    assert response.status_code == 404


def test_eliminar_autor(client: TestClient):
    client.post("/autores", json={"nombre": "Borges", "nacionalidad": "Argentina"})

    response = client.delete("/autores/1")
    assert response.status_code == 204

    # Ya no se puede obtener el autor eliminado
    assert client.get("/autores/1").status_code == 404
    assert client.get("/autores").json() == []


def test_eliminar_autor_inexistente(client: TestClient):
    response = client.delete("/autores/999")
    assert response.status_code == 404
