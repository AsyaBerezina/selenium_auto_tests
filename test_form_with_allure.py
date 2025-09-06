"""
Автоматизированные тесты формы авторизации с использованием Selenium и Allure.

Тестирует успешную и неуспешную авторизацию на сайте 
the-internet.herokuapp.com/login

Автор: Березина Анастасия Дмитриевна
"""

import pytest
import allure
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


@allure.feature("Авторизация")
@allure.story("Page Object для формы авторизации")
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
    
    @allure.step("Открытие страницы авторизации")
    def open_login_page(self):
        """Открытие страницы авторизации."""
        with allure.step(f"Переход по URL: {self.login_url}"):
            self.driver.get(self.login_url)
        
        with allure.step("Ожидание загрузки формы авторизации"):
            self.wait.until(EC.presence_of_element_located(self.username_field))
        
        with allure.step("Проверка корректности загруженной страницы"):
            current_url = self.driver.current_url
            allure.attach(current_url, "Текущий URL", allure.attachment_type.TEXT)
            assert "login" in current_url.lower(), \
                f"Ожидалась страница логина, текущий URL: {current_url}"
    
    @allure.step("Ввод имени пользователя: '{username}'")
    def enter_username(self, username: str):
        """Ввод имени пользователя."""
        username_element = self.wait.until(
            EC.element_to_be_clickable(self.username_field)
        )
        username_element.clear()
        username_element.send_keys(username)
        allure.attach(username, "Введённое имя пользователя", allure.attachment_type.TEXT)
    
    @allure.step("Ввод пароля")
    def enter_password(self, password: str):
        """Ввод пароля."""
        password_element = self.wait.until(
            EC.element_to_be_clickable(self.password_field)
        )
        password_element.clear()
        password_element.send_keys(password)
        # Не логируем пароль в открытом виде в отчёт
        allure.attach("***", "Пароль введён", allure.attachment_type.TEXT)
    
    @allure.step("Нажатие кнопки входа")
    def click_login_button(self):
        """Нажатие кнопки входа."""
        login_button_element = self.wait.until(
            EC.element_to_be_clickable(self.login_button)
        )
        login_button_element.click()
    
    @allure.step("Выполнение авторизации с логином '{username}'")
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
    
    @allure.step("Проверка успешной авторизации")
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
            
            result = any(len(elements) > 0 for elements in success_elements)
            allure.attach(str(result), "Результат проверки успешной авторизации", allure.attachment_type.TEXT)
            return result
            
        except TimeoutException:
            allure.attach("TimeoutException при проверке успешной авторизации", 
                         "Ошибка", allure.attachment_type.TEXT)
            return False
    
    @allure.step("Проверка неуспешной авторизации")
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
            result = len(error_elements) > 0
            allure.attach(str(result), "Результат проверки неуспешной авторизации", allure.attachment_type.TEXT)
            return result
            
        except TimeoutException:
            allure.attach("TimeoutException при проверке неуспешной авторизации", 
                         "Ошибка", allure.attachment_type.TEXT)
            return False
    
    @allure.step("Получение текста сообщения об успехе")
    def get_success_message_text(self) -> str:
        """Получение текста сообщения об успехе."""
        try:
            success_element = self.wait.until(
                EC.presence_of_element_located(self.success_message)
            )
            text = success_element.text.strip()
            allure.attach(text, "Сообщение об успехе", allure.attachment_type.TEXT)
            return text
        except TimeoutException:
            allure.attach("Сообщение об успехе не найдено", "Предупреждение", allure.attachment_type.TEXT)
            return ""
    
    @allure.step("Получение текста сообщения об ошибке")
    def get_error_message_text(self) -> str:
        """Получение текста сообщения об ошибке."""
        try:
            error_element = self.wait.until(
                EC.presence_of_element_located(self.error_message)
            )
            text = error_element.text.strip()
            allure.attach(text, "Сообщение об ошибке", allure.attachment_type.TEXT)
            return text
        except TimeoutException:
            allure.attach("Сообщение об ошибке не найдено", "Предупреждение", allure.attachment_type.TEXT)
            return ""


@allure.feature("Авторизация")
@allure.story("Тестирование формы авторизации")
class TestLoginForm:
    """Класс с тестами формы авторизации."""
    
    VALID_USERNAME = "tomsmith"
    VALID_PASSWORD = "SuperSecretPassword!"
    INVALID_USERNAME = "invaliduser"
    INVALID_PASSWORD = "wrongpassword"
    
    @allure.title("Успешная авторизация с корректными данными")
    @allure.description("""
    Тест проверяет успешную авторизацию пользователя с корректными учётными данными.
    
    Шаги:
    1. Открыть страницу авторизации
    2. Ввести корректное имя пользователя
    3. Ввести корректный пароль
    4. Нажать кнопку входа
    5. Проверить успешную авторизацию
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "positive", "login")
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
        with allure.step("Инициализация Page Object"):
            login_page = LoginPage(driver)
        
        with allure.step("Открытие страницы авторизации"):
            login_page.open_login_page()
        
        with allure.step("Выполнение авторизации с корректными данными"):
            login_page.perform_login(self.VALID_USERNAME, self.VALID_PASSWORD)
        
        with allure.step("Проверка результатов авторизации"):
            # Основная проверка - авторизация успешна
            assert login_page.is_login_successful(), \
                "Авторизация должна быть успешной с корректными данными"
            
            # Дополнительные проверки
            success_message = login_page.get_success_message_text()
            assert "You logged into a secure area!" in success_message, \
                f"Ожидалось сообщение об успехе, получено: '{success_message}'"
            
            # Проверяем что перешли на secure area
            current_url = driver.current_url
            allure.attach(current_url, "URL после авторизации", allure.attachment_type.TEXT)
            assert "secure" in current_url, \
                f"После успешной авторизации должен быть переход на secure area, текущий URL: {current_url}"
            
            # Проверяем наличие кнопки выхода
            logout_buttons = driver.find_elements(By.CSS_SELECTOR, "a[href='/logout']")
            assert len(logout_buttons) > 0, "Кнопка выхода должна присутствовать после успешной авторизации"
    
    @allure.title("Неуспешная авторизация с некорректными данными")
    @allure.description("""
    Тест проверяет блокировку авторизации при использовании некорректных учётных данных.
    
    Шаги:
    1. Открыть страницу авторизации
    2. Ввести некорректное имя пользователя
    3. Ввести некорректный пароль
    4. Нажать кнопку входа
    5. Проверить неуспешную авторизацию и сообщение об ошибке
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("negative", "login", "security")
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
        with allure.step("Инициализация Page Object"):
            login_page = LoginPage(driver)
        
        with allure.step("Открытие страницы авторизации"):
            login_page.open_login_page()
        
        with allure.step("Выполнение авторизации с некорректными данными"):
            login_page.perform_login(self.INVALID_USERNAME, self.INVALID_PASSWORD)
        
        with allure.step("Проверка результатов неуспешной авторизации"):
            # Основная проверка - авторизация НЕ успешна
            assert login_page.is_login_failed(), \
                "Авторизация должна быть неуспешной с некорректными данными"
            
            # Дополнительные проверки
            error_message = login_page.get_error_message_text()
            assert "Your username is invalid!" in error_message, \
                f"Ожидалось сообщение об ошибке, получено: '{error_message}'"
            
            # Проверяем что остались на странице логина
            current_url = driver.current_url
            allure.attach(current_url, "URL после неуспешной авторизации", allure.attachment_type.TEXT)
            assert "login" in current_url, \
                f"После неуспешной авторизации должны остаться на странице логина, текущий URL: {current_url}"
            
            # Проверяем отсутствие кнопки выхода
            logout_buttons = driver.find_elements(By.CSS_SELECTOR, "a[href='/logout']")
            assert len(logout_buttons) == 0, "Кнопка выхода НЕ должна присутствовать после неуспешной авторизации"
    
    @allure.title("Авторизация с пустыми учётными данными")
    @allure.description("""
    Тест проверяет обработку попытки авторизации с пустыми полями.
    
    Шаги:
    1. Открыть страницу авторизации
    2. Оставить поля пустыми
    3. Нажать кнопку входа
    4. Проверить обработку ошибки
    """)
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("negative", "validation", "edge-case")
    def test_empty_credentials_login(self, driver):
        """
        Тест авторизации с пустыми данными.
        
        Проверяет:
        - Обработку пустых полей
        - Отображение соответствующего сообщения об ошибке
        
        Args:
            driver: Фикстура WebDriver
        """
        with allure.step("Инициализация Page Object"):
            login_page = LoginPage(driver)
        
        with allure.step("Открытие страницы авторизации"):
            login_page.open_login_page()
        
        with allure.step("Попытка авторизации с пустыми данными"):
            login_page.perform_login("", "")
        
        with allure.step("Проверка обработки пустых данных"):
            assert login_page.is_login_failed(), \
                "Авторизация должна быть неуспешной с пустыми данными"
            
            # Проверяем что остались на странице логина
            current_url = driver.current_url
            allure.attach(current_url, "URL после авторизации с пустыми данными", allure.attachment_type.TEXT)
            assert "login" in current_url, \
                "После авторизации с пустыми данными должны остаться на странице логина"
    
    @allure.title("Авторизация с корректным логином и неверным паролем")
    @allure.description("""
    Тест проверяет обработку случая, когда логин корректный, но пароль неверный.
    
    Шаги:
    1. Открыть страницу авторизации
    2. Ввести корректный логин
    3. Ввести неверный пароль
    4. Нажать кнопку входа
    5. Проверить специфичное сообщение об ошибке пароля
    """)
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("negative", "security", "password")
    def test_invalid_password_valid_username(self, driver):
        """
        Тест с корректным логином но неверным паролем.
        
        Проверяет:
        - Обработку случая с правильным логином и неверным паролем
        - Специфичное сообщение об ошибке пароля
        
        Args:
            driver: Фикстура WebDriver
        """
        with allure.step("Инициализация Page Object"):
            login_page = LoginPage(driver)
        
        with allure.step("Открытие страницы авторизации"):
            login_page.open_login_page()
        
        with allure.step("Авторизация с корректным логином и неверным паролем"):
            login_page.perform_login(self.VALID_USERNAME, self.INVALID_PASSWORD)
        
        with allure.step("Проверка сообщения об ошибке пароля"):
            assert login_page.is_login_failed(), \
                "Авторизация должна быть неуспешной с неверным паролем"
            
            error_message = login_page.get_error_message_text()
            assert "Your password is invalid!" in error_message, \
                f"Ожидалось сообщение об ошибке пароля, получено: '{error_message}'"
    
    @allure.title("Проверка наличия элементов интерфейса")
    @allure.description("""
    Тест проверяет наличие всех необходимых элементов на странице авторизации.
    
    Проверяемые элементы:
    - Поле для ввода логина
    - Поле для ввода пароля
    - Кнопка входа
    - Корректность заголовка страницы
    """)
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("ui", "smoke", "elements")
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
        with allure.step("Инициализация Page Object"):
            login_page = LoginPage(driver)
        
        with allure.step("Открытие страницы авторизации"):
            login_page.open_login_page()
        
        with allure.step("Проверка заголовка страницы"):
            page_title = driver.title
            allure.attach(page_title, "Заголовок страницы", allure.attachment_type.TEXT)
            assert "The Internet" in page_title, \
                f"Ожидался заголовок 'The Internet', получен: '{page_title}'"
        
        with allure.step("Проверка наличия поля логина"):
            username_fields = driver.find_elements(*login_page.username_field)
            assert len(username_fields) == 1, "Поле логина должно присутствовать на странице"
        
        with allure.step("Проверка наличия поля пароля"):
            password_fields = driver.find_elements(*login_page.password_field)
            assert len(password_fields) == 1, "Поле пароля должно присутствовать на странице"
        
        with allure.step("Проверка наличия кнопки входа"):
            login_buttons = driver.find_elements(*login_page.login_button)
            assert len(login_buttons) == 1, "Кнопка входа должна присутствовать на странице"
        
        with allure.step("Проверка активности элементов формы"):
            login_button = login_buttons[0]
            button_text = login_button.text.strip()
            allure.attach(button_text, "Текст кнопки входа", allure.attachment_type.TEXT)
            assert button_text.lower() in ["login", "log in", "войти"], \
                f"Кнопка должна иметь текст для входа, получен: '{button_text}'"
            
            # Проверяем что поля доступны для ввода
            username_element = driver.find_element(*login_page.username_field)
            password_element = driver.find_element(*login_page.password_field)
            
            assert username_element.is_enabled(), "Поле логина должно быть активным"
            assert password_element.is_enabled(), "Поле пароля должно быть активным"
            assert login_button.is_enabled(), "Кнопка входа должна быть активной"


# Фикстура для WebDriver с поддержкой Allure
@pytest.fixture
def driver():
    """
    Фикстура для создания и настройки WebDriver.
    
    Yields:
        WebDriver: Настроенный экземпляр Chrome WebDriver
    """
    with allure.step("Настройка и запуск WebDriver"):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)
        
        allure.attach(driver.capabilities["browserVersion"], 
                     "Версия браузера", allure.attachment_type.TEXT)
        allure.attach("1920x1080", "Размер окна", allure.attachment_type.TEXT)
    
    try:
        yield driver
    finally:
        with allure.step("Закрытие WebDriver"):
            # Прикрепляем скриншот в случае ошибки
            if hasattr(driver, 'get_screenshot_as_png'):
                try:
                    allure.attach(driver.get_screenshot_as_png(), 
                                "Финальный скриншот", allure.attachment_type.PNG)
                except Exception:
                    pass
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