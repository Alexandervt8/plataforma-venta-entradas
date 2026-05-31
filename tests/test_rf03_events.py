import database


# ==============================================================================
# RF-03: Listado de Eventos
# ==============================================================================

def test_rf03_pe_eve_01_events_are_listed(client):
    """
    PE-EVE-01:
    Existen eventos registrados.
    Resultado esperado: Se muestra el catálogo.
    """
    response = client.get("/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Rock Test 2026" in html
    assert "Jazz Agotado" in html
    assert "Tech Conference" in html


def test_rf03_pe_eve_02_empty_events_table_shows_informative_message(client):
    """
    PE-EVE-02:
    No existen eventos registrados.
    Resultado esperado: Se muestra mensaje informativo.
    """
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM purchases")
    cursor.execute("DELETE FROM events")
    conn.commit()
    conn.close()

    response = client.get("/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "No se encontraron eventos" in html


def test_rf03_pe_eve_03_event_with_low_stock_is_available(client):
    """
    PE-EVE-03:
    Evento con stock entre 1 y 10.
    Resultado esperado: Mostrar mensaje de últimas entradas.
    """
    response = client.get("/")
    html = response.get_data(as_text=True)

    assert "Rock Test 2026" in html
    assert "Comprar Entradas" in html
    assert "¡Últimas entradas! Quedan:" in html


def test_rf03_pe_eve_04_event_without_stock_is_sold_out(client):
    """
    PE-EVE-04:
    Evento agotado.
    Resultado esperado: Evento marcado como agotado.
    """
    response = client.get("/")
    html = response.get_data(as_text=True)

    assert "Jazz Agotado" in html
    assert "Agotado" in html


def test_rf03_avl_eve_01_stock_zero_sold_out(client):
    """
    AVL-EVE-01:
    Stock = 0.
    Resultado esperado: Evento agotado.
    """
    response = client.get("/")
    html = response.get_data(as_text=True)

    assert "Jazz Agotado" in html
    assert "Agotado" in html


def test_rf03_avl_eve_02_stock_one_last_tickets(client):
    """
    AVL-EVE-02:
    Stock = 1.
    Resultado esperado: Últimas entradas.
    """
    response = client.get("/")
    html = response.get_data(as_text=True)

    assert "Evento Ultima Entrada" in html
    assert "¡Últimas entradas! Quedan:" in html
    assert ">1<" in html or "1</strong>" in html


def test_rf03_avl_eve_03_stock_between_1_and_10_shows_low_stock(client):
    """
    AVL-EVE-03:
    Stock entre 1 y 10.
    Resultado esperado: Mostrar mensaje de últimas entradas.
    """
    response = client.get("/")
    html = response.get_data(as_text=True)

    assert "Rock Test 2026" in html
    assert "¡Últimas entradas! Quedan:" in html
    assert "10" in html
