# app/utils/browser_helper.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import logging
import psutil


class BrowserHelper:
    def __init__(self):
        self.driver = None
        self.process = None

    def start_browser(self):
        """
        Запуск браузера и сохранение процесса.
        """
        logging.info("Запуск браузера...")
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # Если нужно запустить браузер в фоновом режиме, установите True
        options.headless = False

        # Убедитесь, что путь корректен
        service = Service(executable_path="path_to_your_chromedriver")

        self.driver = webdriver.Chrome(service=service, options=options)

        # Сохраняем процесс браузера
        self.process = psutil.Process(self.driver.service.process.pid)
        logging.info("Браузер запущен успешно.")
        return self.driver

    def open_url(self, driver, url):
        """
        Открытие страницы в браузере.
        :param driver: WebDriver экземпляр.
        :param url: URL страницы для открытия.
        """
        if not driver:
            logging.error("Браузер не запущен!")
            return

        logging.info(f"Открытие страницы: {url}")
        driver.get(url)
        logging.info(f"Страница {url} загружена.")

    def quit_browser(self, driver):
        """
        Завершение работы с браузером, закрытие процесса.
        :param driver: WebDriver экземпляр.
        """
        if driver:
            logging.info("Закрытие браузера...")
            driver.quit()

            # Убиваем процесс браузера
            if self.process:
                try:
                    logging.info("Завершение процесса браузера...")
                    self.process.terminate()
                    self.process.wait(timeout=5)  # Ждем завершения процесса
                    logging.info("Процесс браузера завершён.")
                except psutil.NoSuchProcess:
                    logging.error("Процесс браузера не найден.")
                except psutil.TimeoutExpired:
                    logging.error(
                        "Не удалось завершить процесс браузера вовремя.")
            else:
                logging.error("Процесс браузера не найден.")
        else:
            logging.error("Браузер не был запущен!")
