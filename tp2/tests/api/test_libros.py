from fastapi.testclient import TestClient

LIBRO = {
    "titulo": "Ficciones",
    "isbn": "9789875664070",
    "stock": 5,
    "anio": 1944,
}

AUTOR = {"nombre": "Jorge Luis Borges", "nacionalidad": "Argentina"}


def crear_libro(client: TestClient, **cambios) -> dict:
    response = client.post("/libros", json=LIBRO | cambios)
    assert response.status_code == 201, response.text
    return response.json()


def crear_autor(client: TestClient, **cambios) -> dict:
    response = client.post("/autores", json=AUTOR | cambios)
    assert response.status_code == 201, response.text
    return response.json()


def test_crear_libro(client: TestClient):
    response = client.post("/libros", json=LIBRO)
    assert response.status_code == 201
    libro = response.json()
    assert libro["id"] == 1
    assert libro["titulo"] == "Ficciones"
    assert libro["isbn"] == LIBRO["isbn"]
    assert libro["stock"] == 5
    assert libro["anio"] == 1944


def test_crear_libro_stock_negativo(client: TestClient):
    datos = LIBRO | {"stock": -1}
    response = client.post("/libros", json=datos)
    assert response.status_code == 422


def test_crear_libro_anio_invalido(client: TestClient):
    datos = LIBRO | {"anio": 2200}
    response = client.post("/libros", json=datos)
    assert response.status_code == 422


def test_crear_libro_isbn_duplicado(client: TestClient):
    client.post("/libros", json=LIBRO)

    response = client.post("/libros", json=LIBRO | {"titulo": "Otra edicion"})
    assert response.status_code == 409
    assert response.json()["detail"] == (
        f"Ya existe un libro con el ISBN {LIBRO['isbn']}"
    )


def test_listar_libros(client: TestClient):
    client.post("/libros", json=LIBRO)
    client.post("/libros", json=LIBRO | {"isbn": "9789500727303"})

    response = client.get("/libros")
    assert response.status_code == 200
    libros = response.json()
    assert len(libros) == 2
    assert [lib["id"] for lib in libros] == [1, 2]


def test_listar_libros_vacio(client: TestClient):
    response = client.get("/libros")
    assert response.status_code == 200
    assert response.json() == []


def test_obtener_libro_por_id(client: TestClient):
    client.post("/libros", json=LIBRO)

    response = client.get("/libros/1")
    assert response.status_code == 200
    assert response.json()["titulo"] == "Ficciones"


def test_obtener_libro_inexistente(client: TestClient):
    response = client.get("/libros/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Libro no encontrado"


def test_actualizar_libro(client: TestClient):
    client.post("/libros", json=LIBRO)

    datos = LIBRO | {"titulo": "Ficciones (ed. sudamericana)", "stock": 3}
    response = client.patch("/libros/1", json=datos)
    assert response.status_code == 200
    libro = response.json()
    assert libro["titulo"] == "Ficciones (ed. sudamericana)"
    assert libro["stock"] == 3
    assert libro["isbn"] == LIBRO["isbn"]


def test_actualizar_libro_mismo_isbn(client: TestClient):
    client.post("/libros", json=LIBRO)

    # Reemplazar definitivamente un libro, aunque el ISBN propio no cambia, no da error
    response = client.patch("/libros/1", json=LIBRO | {"stock": 0})
    assert response.status_code == 200
    assert response.json()["stock"] == 0


def test_actualizar_libro_isbn_de_otro(client: TestClient):
    client.post("/libros", json=LIBRO)
    client.post("/libros", json=LIBRO | {"isbn": "9789500727303"})

    response = client.patch("/libros/1", json=LIBRO | {"isbn": "9789500727303"})
    assert response.status_code == 409
    assert response.json()["detail"] == "Ya existe un libro con el ISBN 9789500727303"


def test_actualizar_libro_stock_negativo(client: TestClient):
    client.post("/libros", json=LIBRO)

    response = client.patch("/libros/1", json=LIBRO | {"stock": -1})
    assert response.status_code == 422


def test_actualizar_libro_inexistente(client: TestClient):
    response = client.patch("/libros/999", json=LIBRO)
    assert response.status_code == 404


def test_eliminar_libro(client: TestClient):
    client.post("/libros", json=LIBRO)

    response = client.delete("/libros/1")
    assert response.status_code == 204

    # Ya no se puede obtener el libro eliminado
    assert client.get("/libros/1").status_code == 404
    assert client.get("/libros").json() == []


def test_eliminar_libro_inexistente(client: TestClient):
    response = client.delete("/libros/999")
    assert response.status_code == 404


def test_libro_nuevo_no_tiene_autores(client: TestClient):
    libro = crear_libro(client)
    assert libro["autores"] == []


def test_agregar_autor_a_libro(client: TestClient):
    libro = crear_libro(client)
    autor = crear_autor(client)

    response = client.post(f"/libros/{libro['id']}/autores/{autor['id']}")
    assert response.status_code == 200, response.text
    autores = response.json()["autores"]
    assert len(autores) == 1
    assert autores[0]["nombre"] == "Jorge Luis Borges"

    # GET refleja la misma relación
    libro_feteched = client.get(f"/libros/{libro['id']}").json()
    assert libro_feteched["autores"] == autores


def test_agregar_varios_autores_a_libro(client: TestClient):
    libro = crear_libro(client)
    autor_1 = crear_autor(client)
    autor_2 = crear_autor(client, **{"nombre": "Adolfo Bioy Casares"})

    client.post(f"/libros/{libro['id']}/autores/{autor_1['id']}")
    response = client.post(f"/libros/{libro['id']}/autores/{autor_2['id']}")
    assert response.status_code == 200

    autores = [a["id"] for a in response.json()["autores"]]
    assert set(autores) == {autor_1["id"], autor_2["id"]}


def test_agregar_autor_a_libro_inexistente(client: TestClient):
    autor = crear_autor(client)

    response = client.post(f"/libros/999/autores/{autor['id']}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Libro no encontrado"


def test_agregar_autor_inexistente_a_libro(client: TestClient):
    libro = crear_libro(client)

    response = client.post(f"/libros/{libro['id']}/autores/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Autor no encontrado"


def test_agregar_autor_duplicado_a_libro(client: TestClient):
    libro = crear_libro(client)
    autor = crear_autor(client)
    client.post(f"/libros/{libro['id']}/autores/{autor['id']}")

    # No se puede asociar dos veces el mismo autor al mismo libro
    response = client.post(f"/libros/{libro['id']}/autores/{autor['id']}")
    assert response.status_code == 409
    assert response.json()["detail"] == (
        "El autor Jorge Luis Borges ya está asociado al libro Ficciones"
    )


def test_listar_libros_incluye_autores(client: TestClient):
    libro_1 = crear_libro(client)
    libro_2 = crear_libro(client, **{"titulo": "El Aleph", "isbn": "9789871138344"})
    autor = crear_autor(client)
    client.post(f"/libros/{libro_1['id']}/autores/{autor['id']}")

    response = client.get("/libros")
    assert response.status_code == 200
    libros = response.json()
    assert libros[0]["autores"][0]["id"] == autor["id"]
    assert libros[1]["autores"] == []


def test_actualizar_libro_mantiene_autores(client: TestClient):
    libro = crear_libro(client)
    autor = crear_autor(client)
    client.post(f"/libros/{libro['id']}/autores/{autor['id']}")

    response = client.patch(f"/libros/{libro['id']}", json=LIBRO | {"stock": 0})
    assert response.status_code == 200
    assert response.json()["autores"] == [
        {
            "id": autor["id"],
            "nombre": "Jorge Luis Borges",
            "nacionalidad": "Argentina",
        }
    ]
