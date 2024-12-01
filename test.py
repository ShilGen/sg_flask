import pytest
from flask import url_for
import re
from app import app, LoginForm
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
def test_login_form_csrf(client):
    # Получаем страницу для формы и извлекаем CSRF-токен
    response = client.get('/login')
    assert b'name="csrf_token"' in response.data  # Проверяем наличие CSRF-токена

    # Пробуем отправить форму без CSRF-токена
    response = client.post('/login', data={
        'username': 'test'
    }, follow_redirects=True)
    assert b'CSRF Token Missing' in response.data  # Убедитесь, что проверка соответствует вашему шаблону ошибки

    # Извлекаем CSRF-токен
    csrf_token = extract_csrf_token(response.data)

    # Отправляем форму с корректным CSRF-токеном
    response = client.post('/login', data={
        'username': 'test',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    assert response.status_code == 200

def extract_csrf_token(data):
    """Извлечение CSRF токена из HTML."""
    # Используем более гибкое регулярное выражение
    match = re.search(r'name="csrf_token" type="hidden" value="([^"]+)"', data.decode('utf-8'))
    if match is None:
        print("CSRF token not found in data:", data)
    assert match is not None, "CSRF token was not found in the HTML response."
    return match.group(1)

