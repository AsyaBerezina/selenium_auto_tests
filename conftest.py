"""
Конфигурация pytest и настройки для Allure отчётов.

Содержит глобальные фикстуры и хуки для улучшения отчётности.
"""

import pytest
import allure
import os
import platform
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def pytest_configure(config):
    """Конфигурация pytest при запуске."""
    # Создаём директорию для результатов Allure, если её нет
    allure_dir = config.getoption("--alluredir")
    if allure_dir and not os.path.exists(allure_dir):
        os.makedirs(allure_dir)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Хук для создания отчёта о результате теста.
    Добавляет скриншоты и логи в случае падения теста.
    """
    outcome = yield
    rep = outcome.get_result()
    
    # Добавляем информацию о тесте в Allure при падении
    if rep.when == "call" and rep.failed:
        # Получаем driver из фикстуры, если он доступен
        if hasattr(item, "funcargs") and "driver" in item.funcargs:
            driver = item.funcargs["driver"]
            
            # Прикрепляем скриншот
            try:
                screenshot = driver.get_screenshot_as_png()
                allure.attach(
                    screenshot,
                    name="Скриншот при падении теста",
                    attachment_type=allure.attachment_type.PNG
                )
            except Exception as e:
                allure.attach(
                    str(e),
                    name="Ошибка получения скриншота",
                    attachment_type=allure.attachment_type.TEXT
                )
            
            # Прикрепляем URL текущей страницы
            try:
                current_url = driver.current_url
                allure.attach(
                    current_url,
                    name="URL при падении теста",
                    attachment_type=allure.attachment_type.TEXT
                )
            except Exception as e:
                allure.attach(
                    str(e),
                    name="Ошибка получения URL",
                    attachment_type=allure.attachment_type.TEXT
                )
            
            # Прикрепляем HTML код страницы
            try:
                page_source = driver.page_source
                allure.attach(
                    page_source,
                    name="HTML код страницы",
                    attachment_type=allure.attachment_type.HTML
                )
            except Exception as e:
                allure.attach(
                    str(e),
                    name="Ошибка получения HTML",
                    attachment_type=allure.attachment_type.TEXT
                )


@pytest.fixture(scope="session", autouse=True)
def test_environment():
    """
    Автоматическая фикстура для добавления информации о тестовом окружении.
    Выполняется один раз за сессию тестирования.
    """
    # Добавляем информацию об окружении
    allure.attach(
        f"Операционная система: {platform.system()} {platform.release()}",
        name="Информация об ОС",
        attachment_type=allure.attachment_type.TEXT
    )
    
    allure.attach(
        f"Python версия: {platform.python_version()}",
        name="Версия Python",
        attachment_type=allure.attachment_type.TEXT
    )
    
    allure.attach(
        f"Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        name="Время запуска тестов",
        attachment_type=allure.attachment_type.TEXT
    )


@pytest.fixture(scope="function")
def browser_logs(driver):
    """
    Фикстура для сбора логов браузера.
    Собирает логи браузера после каждого теста.
    """
    yield
    
    try:
        # Получаем логи браузера
        logs = driver.get_log('browser')
        if logs:
            log_text = "\n".join([f"[{log['level']}] {log['message']}" for log in logs])
            allure.attach(
                log_text,
                name="Логи браузера",
                attachment_type=allure.attachment_type.TEXT
            )
    except Exception as e:
        allure.attach(
            f"Не удалось получить логи браузера: {str(e)}",
            name="Ошибка логов",
            attachment_type=allure.attachment_type.TEXT
        )


@pytest.fixture(scope="function")
def test_data():
    """
    Фикстура с тестовыми данными.
    Предоставляет централизованный доступ к тестовым данным.
    """
    return {
        "valid_user": {
            "username": "tomsmith",
            "password": "SuperSecretPassword!"
        },
        "invalid_users": [
            {"username": "invaliduser", "password": "wrongpassword"},
            {"username": "tomsmith", "password": "wrongpassword"},
            {"username": "invaliduser", "password": "SuperSecretPassword!"},
            {"username": "", "password": ""},
            {"username": "tomsmith", "password": ""}
        ],
        "test_urls": {
            "login_page": "https://the-internet.herokuapp.com/login",
            "secure_area": "https://the-internet.herokuapp.com/secure"
        }
    }


def pytest_collection_modifyitems(config, items):
    """
    Модификация собранных тестов.
    Добавляет автоматические маркеры на основе имён тестов.
    """
    for item in items:
        # Добавляем маркер на основе имени теста
        if "login" in item.name.lower():
            item.add_marker(pytest.mark.login)
        
        if "successful" in item.name.lower() or "positive" in item.name.lower():
            item.add_marker(pytest.mark.positive)
        
        if "unsuccessful" in item.name.lower() or "invalid" in item.name.lower() or "negative" in item.name.lower():
            item.add_marker(pytest.mark.negative)
        
        if "empty" in item.name.lower() or "edge" in item.name.lower():
            item.add_marker(pytest.mark.edge_case)


# Дополнительная конфигурация для запуска в разных режимах
def pytest_addoption(parser):
    """Добавление дополнительных опций командной строки."""
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        help="Браузер для тестирования: chrome, firefox"
    )
    
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Запуск в headless режиме"
    )
    
    parser.addoption(
        "--base-url",
        action="store",
        default="https://the-internet.herokuapp.com",
        help="Базовый URL для тестирования"
    )