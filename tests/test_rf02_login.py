# ==============================================================================
# RF-02: Inicio de Sesión / Autenticación
# ==============================================================================

def test_rf02_pe_log_01_login_valid_credentials(client, registered_user):
    """
    PE-LOG-01:
    Credenciales correctas.
    Resultado esperado: Inicio de sesión exitoso.
    """
    response = client.post("/login", data={
        "email": registered_user["email"],
        "password": registered_user["password"],
    }, follow_redirects=True)

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "¡Bienvenido de nuevo, Usuario de Prueba!" in html
    assert "Mis Entradas" in html


def test_rf02_pe_log_02_login_unregistered_email(client):
    """
    PE-LOG-02:
    Correo no registrado.
    Resultado esperado: Error de credenciales.
    """
    response = client.post("/login", data={
        "email": "noexiste@test.com",
        "password": "password123",
    }, follow_redirects=True)

    html = response.get_data(as_text=True)
    assert "Correo electrónico o contraseña incorrectos." in html


def test_rf02_pe_log_03_login_wrong_password(client, registered_user):
    """
    PE-LOG-03:
    Contraseña incorrecta.
    Resultado esperado: Error de credenciales.
    """
    response = client.post("/login", data={
        "email": registered_user["email"],
        "password": "incorrecta",
    }, follow_redirects=True)

    html = response.get_data(as_text=True)
    assert "Correo electrónico o contraseña incorrectos." in html


def test_rf02_pe_log_04_login_empty_fields(client):
    """
    PE-LOG-04:
    Campos vacíos.
    Resultado esperado: Error de campos obligatorios.
    """
    response = client.post("/login", data={
        "email": "",
        "password": "",
    }, follow_redirects=True)

    html = response.get_data(as_text=True)
    assert "Todos los campos son obligatorios." in html


def test_rf02_avl_log_01_empty_email_invalid(client):
    """
    AVL-LOG-01:
    Email vacío.
    Resultado esperado: Error de validación.
    """
    response = client.post("/login", data={
        "email": "",
        "password": "password123",
    }, follow_redirects=True)

    html = response.get_data(as_text=True)
    assert "Todos los campos son obligatorios." in html


def test_rf02_avl_log_02_empty_password_invalid(client, registered_user):
    """
    AVL-LOG-02:
    Contraseña vacía.
    Resultado esperado: Error de validación.
    """
    response = client.post("/login", data={
        "email": registered_user["email"],
        "password": "",
    }, follow_redirects=True)

    html = response.get_data(as_text=True)
    assert "Todos los campos son obligatorios." in html


def test_rf02_avl_log_03_complete_fields_valid(client, registered_user):
    """
    AVL-LOG-03:
    Ambos campos completos y válidos.
    Resultado esperado: Inicio de sesión exitoso.
    """
    response = client.post("/login", data={
        "email": registered_user["email"],
        "password": registered_user["password"],
    }, follow_redirects=True)

    html = response.get_data(as_text=True)
    assert "¡Bienvenido de nuevo, Usuario de Prueba!" in html


def test_rf02_session_is_created_after_login(client, registered_user):
    """
    Verifica que el sistema mantiene una sesión segura basada en cookies.
    """
    client.post("/login", data={
        "email": registered_user["email"],
        "password": registered_user["password"],
    }, follow_redirects=True)

    with client.session_transaction() as sess:
        assert sess["user_id"] == registered_user["id"]
        assert sess["user_name"] == registered_user["name"]
