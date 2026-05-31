# ==============================================================================
# RF-04: Búsqueda de Eventos
# ==============================================================================

def test_rf04_pe_bus_01_search_by_existing_title(client):
    """
    PE-BUS-01:
    Búsqueda por título existente.
    Resultado esperado: Retorna eventos coincidentes.
    """
    response = client.get("/?q=Rock")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Rock Test 2026" in html
    assert "Tech Conference" not in html


def test_rf04_pe_bus_02_search_by_existing_location(client):
    """
    PE-BUS-02:
    Búsqueda por ubicación existente.
    Resultado esperado: Retorna eventos coincidentes.
    """
    response = client.get("/?q=Cusco")
    html = response.get_data(as_text=True)

    assert "Tech Conference" in html
    assert "Rock Test 2026" not in html


def test_rf04_search_by_existing_description(client):
    """
    Regla de negocio:
    La búsqueda también debe funcionar por descripción.
    """
    response = client.get("/?q=tecnológico")
    html = response.get_data(as_text=True)

    assert "Tech Conference" in html
    assert "Rock Test 2026" not in html


def test_rf04_pe_bus_03_search_without_matches(client):
    """
    PE-BUS-03:
    Búsqueda sin coincidencias.
    Resultado esperado: Mensaje sin resultados.
    """
    response = client.get("/?q=EventoXYZ")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "No se encontraron eventos" in html
    assert "EventoXYZ" in html


def test_rf04_pe_bus_04_empty_search_shows_all_events(client):
    """
    PE-BUS-04:
    Campo vacío.
    Resultado esperado: Muestra todos los eventos.
    """
    response = client.get("/?q=")
    html = response.get_data(as_text=True)

    assert "Rock Test 2026" in html
    assert "Jazz Agotado" in html
    assert "Tech Conference" in html


def test_rf04_avl_bus_01_length_zero(client):
    """
    AVL-BUS-01:
    Longitud mínima, 0 caracteres.
    Resultado esperado: Mostrar todos los eventos.
    """
    response = client.get("/?q=")
    html = response.get_data(as_text=True)

    assert "Rock Test 2026" in html
    assert "Tech Conference" in html


def test_rf04_avl_bus_02_length_one(client):
    """
    AVL-BUS-02:
    Longitud mínima válida, 1 carácter.
    Resultado esperado: Buscar coincidencias.
    """
    response = client.get("/?q=R")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Rock Test 2026" in html


def test_rf04_avl_bus_03_normal_length(client):
    """
    AVL-BUS-03:
    Longitud normal.
    Resultado esperado: Buscar coincidencias.
    """
    response = client.get("/?q=Rock")
    html = response.get_data(as_text=True)

    assert "Rock Test 2026" in html
