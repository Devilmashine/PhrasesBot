import pytest
from main import main, parse_final_response, remove_duplicates

@pytest.mark.asyncio
async def test_main_positive():
    prompt = [...]  # вставьте положительный тестовый пример
    result = await main(prompt)
    # Проверяем, что результат является списком строк
    assert isinstance(result, list)
    assert all(isinstance(phrase, str) for phrase in result)

@pytest.mark.asyncio
async def test_main_negative():
    prompt = [...]  # вставьте отрицательный тестовый пример
    result = await main(prompt)
    # Проверяем, что результат является пустым списком
    assert result == []

def test_parse_final_response():
    final_response = [...]  # вставьте тестовый пример
    result = parse_final_response(final_response)
    # Проверяем, что результат является списком строк
    assert isinstance(result, list)
    assert all(isinstance(phrase, str) for phrase in result)

def test_remove_duplicates():
    response_list = [...]  # вставьте тестовый пример
    result = remove_duplicates(response_list)
    # Проверяем, что результат является множеством строк
    assert isinstance(result, set)
    assert all(isinstance(phrase, str) for phrase in result)