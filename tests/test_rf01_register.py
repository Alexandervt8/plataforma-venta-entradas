import database


# ==============================================================================
# RF-01: Registro de Usuarios
# ==============================================================================

def test_rf01_pe_reg_01_register_valid_user(client):
    """
    PE-REG-01:
    Datos válidos completos.
    Resultado esperado: Registro exitoso.
    """
    response = client.post("/register", data={
        "name": "Juan Perez",
        "email": "juan@test.com",
        "password": "password123",
    }, follow_redirects=True)

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Registro exitoso. Por favor inicia sesión." in html


def test_rf01_pe_reg_02_register_empty_fields(client):
    """
    PE-REG-02:
    Algún campo obligatorio vacío.
    Resultado esperado: Error de campos obligatorios.
    """
    cases = [
        {"name": "", "email": "juan@test.com", "password": "password123"},
        {"name": "Juan Perez", "email": "", "password": "password123"},
        {"name": "Juan Perez", "email": "juan@test.com", "password": ""},
    ]

    for form_data in cases:
        response = client.post("/register", data=form_data, follow_redirects=True)
        html = response.get_data(as_text=True)
        assert "Todos los campos son obligatorios." in html


def test_rf01_pe_reg_03_register_invalid_email(client):
    """
    PE-REG-03:
    Correo electrónico con formato inválido.
    Resultado esperado: Error de correo inválido.
    """
    invalid_emails = [
        "juan.sin.arroba",
        "usuario@",
        "@dominio.com",
        "usuario@dominio",
    ]

    for email in invalid_emails:
        response = client.post("/register", data={
            "name": "Juan Perez",
            "email": email,
            "password": "password123",
        }, follow_redirects=True)

        html = response.get_data(as_text=True)
        assert "Por favor ingresa un correo electrónico válido." in html


def test_rf01_pe_reg_04_register_duplicate_email(client):
    """
    PE-REG-04:
    Correo electrónico ya existente.
    Resultado esperado: Error de correo duplicado.
    """
    client.post("/register", data={
        "name": "Usuario Original",
        "email": "duplicado@test.com",
        "password": "password123",
    }, follow_redirects=True)

    response = client.post("/register", data={
        "name": "Usuario Duplicado",
        "email": "duplicado@test.com",
        "password": "password123",
    }, follow_redirects=True)

    html = response.get_data(as_text=True)
    assert "El correo electrónico ya se encuentra registrado." in html


def test_rf01_avl_reg_01_password_five_characters_invalid(client):
    """
    AVL-REG-01:
    Límite inferior inválido, contraseña de 5 caracteres.
    Resultado esperado: Error de longitud mínima.
    """
    response = client.post("/register", data={
        "name": "Usuario AVL",
        "email": "avl5@test.com",
        "password": "abcde",
    }, follow_redirects=True)

    html = response.get_data(as_text=True)
    assert "La contraseña debe tener al menos 6 caracteres." in html


def test_rf01_avl_reg_02_password_six_characters_valid(client):
    """
    AVL-REG-02:
    Límite mínimo válido, contraseña de 6 caracteres.
    Resultado esperado: Registro exitoso.
    """
    response = client.post("/register", data={
        "name": "Usuario AVL",
        "email": "avl6@test.com",
        "password": "abcdef",
    }, follow_redirects=True)

    html = response.get_data(as_text=True)
    assert "Registro exitoso. Por favor inicia sesión." in html


def test_rf01_avl_reg_03_password_nominal_valid(client):
    """
    AVL-REG-03:
    Valor nominal seguro, contraseña mayor al mínimo.
    Resultado esperado: Registro exitoso.
    """
    response = client.post("/register", data={
        "name": "Usuario Seguro",
        "email": "seguro@test.com",
        "password": "seguro12345",
    }, follow_redirects=True)

    html = response.get_data(as_text=True)
    assert "Registro exitoso. Por favor inicia sesión." in html


def test_rf01_rnf_password_is_hashed(client):
    """
    RNF-02:
    La contraseña no debe almacenarse en texto plano.
    """
    client.post("/register", data={
        "name": "Usuario Hash",
        "email": "hash@test.com",
        "password": "password123",
    }, follow_redirects=True)

    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE email = ?", ("hash@test.com",))
    stored_password = cursor.fetchone()["password"]
    conn.close()

    assert stored_password != "password123"
    assert stored_password.startswith("scrypt:") or stored_password.startswith("pbkdf2:")
