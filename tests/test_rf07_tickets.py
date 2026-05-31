import database


# ==============================================================================
# RF-07: Historial de Entradas / Mis Entradas
# ==============================================================================

def test_rf07_pe_his_01_user_with_purchases_sees_history(authenticated_client):
    """
    PE-HIS-01:
    Usuario con compras registradas.
    Resultado esperado: Mostrar historial completo.
    """
    authenticated_client.post("/purchase/3", data={
        "quantity": "2",
    }, follow_redirects=True)

    response = authenticated_client.get("/tickets")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Mis Entradas Adquiridas" in html
    assert "Tech Conference" in html
    assert "Cantidad" in html
    assert "S/ 60.00" in html
    assert "Código de Operación:" in html


def test_rf07_pe_his_02_user_without_purchases_sees_empty_message(authenticated_client):
    """
    PE-HIS-02:
    Usuario sin compras registradas.
    Resultado esperado: Mostrar mensaje informativo.
    """
    response = authenticated_client.get("/tickets")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Aún no has comprado entradas" in html
    assert "Ver Eventos" in html


def test_rf07_pe_his_03_unauthenticated_user_is_redirected_to_login(client):
    """
    PE-HIS-03:
    Usuario no autenticado.
    Resultado esperado: Redirección al inicio de sesión.
    """
    response = client.get("/tickets", follow_redirects=True)
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Debes iniciar sesión para realizar esta acción." in html
    assert "Iniciar Sesión" in html


def test_rf07_pe_his_04_user_does_not_see_other_users_purchases(
    client,
    registered_user,
    second_user,
):
    """
    PE-HIS-04:
    Intento de acceso a compras ajenas.
    Resultado esperado: El usuario solo visualiza sus propias compras.

    Implementación:
    - Se registra una compra para el usuario 2 directamente en la base de datos.
    - Se inicia sesión como usuario 1.
    - El historial no debe mostrar la compra del usuario 2.
    """
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO purchases (user_id, event_id, quantity, total_price, purchase_date)
        VALUES (?, ?, ?, ?, datetime('now'))
    """, (2, 3, 1, 30.00))
    conn.commit()
    conn.close()

    with client.session_transaction() as sess:
        sess["user_id"] = registered_user["id"]
        sess["user_name"] = registered_user["name"]

    response = client.get("/tickets")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Tech Conference" not in html
    assert "Aún no has comprado entradas" in html


def test_rf07_avl_his_01_zero_purchases(authenticated_client):
    """
    AVL-HIS-01:
    0 compras registradas.
    Resultado esperado: Historial vacío.
    """
    response = authenticated_client.get("/tickets")
    html = response.get_data(as_text=True)

    assert "Aún no has comprado entradas" in html


def test_rf07_avl_his_02_one_purchase(authenticated_client):
    """
    AVL-HIS-02:
    1 compra registrada.
    Resultado esperado: Mostrar una entrada.
    """
    authenticated_client.post("/purchase/3", data={
        "quantity": "1",
    }, follow_redirects=True)

    response = authenticated_client.get("/tickets")
    html = response.get_data(as_text=True)

    assert "Tech Conference" in html
    assert "ticket-item" in html
    assert html.count("ticket-item") == 1


def test_rf07_avl_his_03_multiple_purchases(authenticated_client):
    """
    AVL-HIS-03:
    Varias compras registradas.
    Resultado esperado: Mostrar todas las entradas.
    """
    authenticated_client.post("/purchase/1", data={
        "quantity": "1",
    }, follow_redirects=True)
    authenticated_client.post("/purchase/3", data={
        "quantity": "1",
    }, follow_redirects=True)
    authenticated_client.post("/purchase/4", data={
        "quantity": "1",
    }, follow_redirects=True)

    response = authenticated_client.get("/tickets")
    html = response.get_data(as_text=True)

    assert "Rock Test 2026" in html
    assert "Tech Conference" in html
    assert "Evento Ultima Entrada" in html
    assert html.count("ticket-item") == 3
