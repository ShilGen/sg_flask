import pytest
from flask import session
from app import app  # предполагается, что приложение названо app.py


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        with app.app_context():
            yield client


def test_homepage_contains_csrf_token(client):
    response = client.get("/login")
    assert response.status_code == 200
    # Проверяем, что форма содержит поле CSRF токена
    assert b'name="csrf_token"' in response.data


def test_form_submission_with_valid_csrf(client):
    # Получаем страницу с формой для извлечения CSRF токена
    response = client.get("/login")
    assert response.status_code == 200
    csrf_token = extract_csrf_token(response.data)

    # Отправляем форму с валидным CSRF токеном
    response = client.post(
        "/login",
        data={"username": "test", "csrf_token": csrf_token},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Logged in as test" in response.data
    # Проверяем, что "username" добавлен в сессию
    with client.session_transaction() as session:
        assert session.get("username") == "test"


def test_form_submission_with_invalid_csrf(client):
    # Отправляем форму с некорректным CSRF токеном
    response = client.post(
        "/login",
        data={"username": "test", "csrf_token": "invalid_token"},
        follow_redirects=True,
    )
    assert response.status_code == 400
    assert b"CSRF Error" in response.data


def test_form_submission_without_csrf(client):
    # Отправляем форму без CSRF токена
    response = client.post(
        "/login",
        data={"username": "test"},
        follow_redirects=True,
    )
    assert response.status_code == 400
    assert b"CSRF Error" in response.data


def extract_csrf_token(response_data):
    """
    Вспомогательная функция для извлечения CSRF токена из ответа.
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(response_data, "html.parser")
    csrf_input = soup.find("input", {"name": "csrf_token"})
    if csrf_input:
        return csrf_input["value"]
    return None
