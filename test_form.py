"""
Автоматизированные тесты формы авторизации с использованием Selenium.

Тестирует успешную и неуспешную авторизацию на сайте 
the-internet.herokuapp.com/login

Автор: Березина Анастасия Дмитриевна
"""

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class LoginPage:
    """Page Object для страницы авторизации."""
    
    def __init__(self, driver):
        """
        Инициализация Page Object.
        
        Args:
            driver: Экземпляр WebDriver
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        
        # URL страницы авторизации
        self.login_url = "https://the-internet.herokuapp.com/login"
        
        # Локаторы элементов формы
        self.username_field = (By.ID, "username")
        self.password_field = (By.ID, "password")
        self.login_button = (By.CSS_SELECTOR, "button[type='submit']")
        
        # Локаторы для проверки результатов
        self.success_message = (By.CSS_SELECTOR, ".flash.success")
        self.error_message = (By.CSS_SELECTOR, ".flash.error")
        self.secure_area_header = (By.CSS_SELECTOR, ".subheader")
        self.logout_button = (By.CSS_SELECTOR, "a[href='/logout']")
    
    def open_login_page(self):
        """Открытие страницы авторизации."""
        self.driver.get(self.login_url)
        
        # Ждём загрузки формы
        self.wait.until(EC.presence_of_element_located(self.username_field))
        
        # Проверяем что попали на правильную страницу
        assert "login" in self.driver.current_url.lower(), \
            f"Ожидалась страница логина, текущий URL: {self.driver.current_url}"
    
    def enter_username(self, username: str):
        """Ввод имени пользователя."""
        username_element = self.wait.until(
            EC.element_to_be_clickable(self.username_field)
        )
        username_element.clear()
        username_element.send_keys(username)
    
    def enter_password(self, password: str):
        """Ввод пароля."""
        password_element = self.wait.until(
            EC.element_to_be_clickable(self.password_field)
        )
        password_element.clear()
        password_element.send_keys(password)
    
    def click_login_button(self):
        """Нажатие кнопки входа."""
        login_button_element = self.wait.until(
            EC.element_to_be_clickable(self.login_button)
        )
        login_button_element.click()
    
    def perform_login(self, username: str, password: str):
        """
        Выполнение полного процесса авторизации.
        
        Args:
            username: Имя пользователя
            password: Пароль
        """
        self.enter_username(username)
        self.enter_password(password)
        self.click_login_button()
    
    def is_login_successful(self) -> bool:
        """
        Проверка успешной авторизации.
        
        Returns:
            True если авторизация успешна
        """
        try:
            # Ждём появления сообщения об успехе или кнопки выхода
            self.wait.until(
                lambda driver: (
                    len(driver.find_elements(*self.success_message)) > 0 or
                    len(driver.find_elements(*self.logout_button)) > 0
                )
            )
            
            # Проверяем наличие элементов успешной авторизации
            success_elements = [
                self.driver.find_elements(*self.success_message),
                self.driver.find_elements(*self.logout_button),
                self.driver.find_elements(*self.secure_area_header)
            ]
            
            return any(len(elements) > 0 for elements in success_elements)
            
        except TimeoutException:
            return False
    
    def is_login_failed(self) -> bool:
        """
        Проверка неуспешной авторизации.
        
        Returns:
            True если авторизация неуспешна
        """
        try:
            # Ждём появления сообщения об ошибке
            self.wait.until(EC.presence_of_element_located(self.error_message))
            
            error_elements = self.driver.find_elements(*self.error_message)
            return len(error_elements) > 0
            
        except TimeoutException:
            return False
    
    def get_success_message_text(self) -> str:
        """Получение текста сообщения об успехе."""
        try:
            success_element = self.wait.until(
                EC.presence_of_element_located(self.success_message)
            )
            return success_element.text.strip()
        except TimeoutException:
            return ""
    
    def get_error_message_text(self) -> str:
        """Получение текста сообщения об ошибке."""
        try:
            error_element = self.wait.until(
                EC.presence_of_element_located(self.error_message)
            )
            return error_element.text.strip()
        except TimeoutException:
            return ""


class TestLoginForm:
    """Класс с тестами формы авторизации."""
    
    VALID_USERNAME = "tomsmith"
    VALID_PASSWORD = "SuperSecretPassword!"
    INVALID_USERNAME = "invaliduser"
    INVALID_PASSWORD = "wrongpassword"
    
    def test_successful_login(self, driver):
        """
        Тест успешной авторизации.
        
        Проверяет:
        - Успешный вход с корректными данными
        - Отображение сообщения об успехе
        - Переход на защищённую страницу
        - Появление кнопки выхода
        
        Args:
            driver: Фикстура WebDriver
        """
        login_page = LoginPage(driver)
        login_page.open_login_page()
        
        # Act (действие)
        login_page.perform_login(self.VALID_USERNAME, self.VALID_PASSWORD)
        
        # Основная проверка - авторизация успешна
        assert login_page.is_login_successful(), \
            "Авторизация должна быть успешной с корректными данными"
        
        # Дополнительные проверки
        success_message = login_page.get_success_message_text()
        assert "You logged into a secure area!" in success_message, \
            f"Ожидалось сообщение об успехе, получено: '{success_message}'"
        
        # Проверяем что перешли на secure area
        assert "secure" in driver.current_url, \
            f"После успешной авторизации должен быть переход на secure area, текущий URL: {driver.current_url}"
        
        # Проверяем наличие кнопки выхода
        logout_buttons = driver.find_elements(By.CSS_SELECTOR, "a[href='/logout']")
        assert len(logout_buttons) > 0, "Кнопка выхода должна присутствовать после успешной авторизации"
    
    def test_unsuccessful_login(self, driver):
        """
        Тест неуспешной авторизации.
        
        Проверяет:
        - Блокировку входа с некорректными данными
        - Отображение сообщения об ошибке
        - Остаемся на странице логина
        - Отсутствие кнопки выхода
        
        Args:
            driver: Фикстура WebDriver
        """
        login_page = LoginPage(driver)
        login_page.open_login_page()
        
        # Act (действие)
        login_page.perform_login(self.INVALID_USERNAME, self.INVALID_PASSWORD)
        
        # Assert (проверка)
        # Основная проверка - авторизация НЕ успешна
        assert login_page.is_login_failed(), \
            "Авторизация должна быть неуспешной с некорректными данными"
        
        # Дополнительные проверки
        error_message = login_page.get_error_message_text()
        assert "Your username is invalid!" in error_message, \
            f"Ожидалось сообщение об ошибке, получено: '{error_message}'"
        
        # Проверяем что остались на странице логина
        assert "login" in driver.current_url, \
            f"После неуспешной авторизации должны остаться на странице логина, текущий URL: {driver.current_url}"
        
        # Проверяем отсутствие кнопки выхода
        logout_buttons = driver.find_elements(By.CSS_SELECTOR, "a[href='/logout']")
        assert len(logout_buttons) == 0, "Кнопка выхода НЕ должна присутствовать после неуспешной авторизации"
    
    def test_empty_credentials_login(self, driver):
        """
        Тест авторизации с пустыми данными.
        
        Проверяет:
        - Обработку пустых полей
        - Отображение соответствующего сообщения об ошибке
        
        Args:
            driver: Фикстура WebDriver
        """
        login_page = LoginPage(driver)
        login_page.open_login_page()
        
        # Act (действие) - отправляем форму с пустыми полями
        login_page.perform_login("", "")
        
        # Assert (проверка)
        assert login_page.is_login_failed(), \
            "Авторизация должна быть неуспешной с пустыми данными"
        
        # Проверяем что остались на странице логина
        assert "login" in driver.current_url, \
            "После авторизации с пустыми данными должны остаться на странице логина"
    
    def test_invalid_password_valid_username(self, driver):
        """
        Тест с корректным логином но неверным паролем.
        
        Проверяет:
        - Обработку случая с правильным логином и неверным паролем
        - Специфичное сообщение об ошибке пароля
        
        Args:
            driver: Фикстура WebDriver
        """
        login_page = LoginPage(driver)
        login_page.open_login_page()
        
        # Act (действие) - правильный логин, неверный пароль
        login_page.perform_login(self.VALID_USERNAME, self.INVALID_PASSWORD)
        
        # Assert (проверка)
        assert login_page.is_login_failed(), \
            "Авторизация должна быть неуспешной с неверным паролем"
        
        error_message = login_page.get_error_message_text()
        assert "Your password is invalid!" in error_message, \
            f"Ожидалось сообщение об ошибке пароля, получено: '{error_message}'"
    
    def test_ui_elements_presence(self, driver):
        """
        Тест наличия всех элементов на странице авторизации.
        
        Проверяет:
        - Наличие поля логина
        - Наличие поля пароля  
        - Наличие кнопки входа
        - Корректность заголовка страницы
        
        Args:
            driver: Фикстура WebDriver
        """
        login_page = LoginPage(driver)
        login_page.open_login_page()
        
        # Assert (проверки наличия элементов)
        
        # Проверяем заголовок страницы
        assert "The Internet" in driver.title, \
            f"Ожидался заголовок 'The Internet', получен: '{driver.title}'"
        
        # Проверяем наличие поля логина
        username_fields = driver.find_elements(*login_page.username_field)
        assert len(username_fields) == 1, "Поле логина должно присутствовать на странице"
        
        # Проверяем наличие поля пароля
        password_fields = driver.find_elements(*login_page.password_field)
        assert len(password_fields) == 1, "Поле пароля должно присутствовать на странице"
        
        # Проверяем наличие кнопки входа
        login_buttons = driver.find_elements(*login_page.login_button)
        assert len(login_buttons) == 1, "Кнопка входа должна присутствовать на странице"
        
        # Проверяем что кнопка имеет правильный текст
        login_button = login_buttons[0]
        button_text = login_button.text.strip()
        assert button_text.lower() in ["login", "log in", "войти"], \
            f"Кнопка должна иметь текст для входа, получен: '{button_text}'"
        
        # Проверяем что поля доступны для ввода
        username_element = driver.find_element(*login_page.username_field)
        password_element = driver.find_element(*login_page.password_field)
        
        assert username_element.is_enabled(), "Поле логина должно быть активным"
        assert password_element.is_enabled(), "Поле пароля должно быть активным"
        assert login_button.is_enabled(), "Кнопка входа должна быть активной"


# Фикстура для WebDriver
@pytest.fixture
def driver():
    """
    Фикстура для создания и настройки WebDriver.
    
    Yields:
        WebDriver: Настроенный экземпляр Chrome WebDriver
    """
    # Selenium Manager автоматически скачает подходящий драйвер
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    
    # Возвращаем драйвер для использования в тестах
    yield driver
    
    driver.quit()


# Дополнительные фикстуры для тестовых данных
@pytest.fixture
def valid_credentials():
    """Фикстура с корректными данными авторизации."""
    return {
        "username": "tomsmith",
        "password": "SuperSecretPassword!"
    }


@pytest.fixture
def invalid_credentials():
    """Фикстура с некорректными данными авторизации."""
    return [
        {"username": "invaliduser", "password": "wrongpassword"},
        {"username": "tomsmith", "password": "wrongpassword"},
        {"username": "invaliduser", "password": "SuperSecretPassword!"},
        {"username": "", "password": ""},
        {"username": "tomsmith", "password": ""}
    ]


@pytest.fixture
def login_page(driver):
    """Фикстура для создания Page Object."""
    return LoginPage(driver)


# Маркеры для категоризации тестов
pytestmark = [
    pytest.mark.ui,
    pytest.mark.selenium,
    pytest.mark.login
]