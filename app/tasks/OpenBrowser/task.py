# tasks/OpenBrowser/task.py

import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import os
import psutil


class Task:
    def __init__(self, shared_resources, process_number, log_queue, log_helper=None, settings=None):
        self.shared_resources = shared_resources
        self.process_number = process_number
        self.log_queue = log_queue
        self.log_helper = log_helper
        self.settings = settings or {}
        self.driver = None
        self.process = None

    def get_task_name(self):
        return "Открыть браузер"

    def run(self):

        try:
            # Настройка опций для Chrome
            options = Options()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            # Настройка режима запуска браузера на основе настроек
            if self.settings.get('browser_options', {}).get('headless', False):
                options.headless = True
            else:
                options.headless = False

            window_size = self.settings.get(
                'browser_options', {}).get('window_size', "1920,1080")
            options.add_argument(f"--window-size={window_size}")

            # Указание путей к Chrome и ChromeDriver
            chrome_path = os.path.abspath("ChromeApp/Chrome/chrome.exe")
            chrome_driver_path = os.path.abspath(
                "ChromeApp/ChromeDriver/chromedriver.exe")

            # Проверка наличия Chrome
            if not os.path.exists(chrome_path):
                raise FileNotFoundError(
                    f"Не найден Chrome по пути: {chrome_path}")

            # Проверка наличия ChromeDriver
            if not os.path.exists(chrome_driver_path):
                raise FileNotFoundError(f"Не найден ChromeDriver по пути: {
                                        chrome_driver_path}")

            # Настройка сервиса для ChromeDriver
            service = Service(executable_path=chrome_driver_path,
                              chrome_binary=chrome_path)

            # Инициализация WebDriver
            self.driver = webdriver.Chrome(service=service, options=options)

            # Сохранение процесса браузера для последующего завершения
            self.process = psutil.Process(self.driver.service.process.pid)

            logging.info(f"Открыть браузер: Процесс {
                         self.process_number} запустил браузер.")

            # Открытие пустой вкладки
            self.driver.get("about:blank")
            logging.info(f"Открыть браузер: Процесс {
                         self.process_number} открыл пустую вкладку.")

            # Симуляция работы браузера (можно заменить на реальные действия)
            time.sleep(5)

        except Exception as e:
            logging.error(f"Открыть браузер: Процесс {
                          self.process_number} столкнулся с ошибкой: {e}")

        finally:
            # Закрытие браузера и завершение процесса
            if self.driver:
                try:
                    self.driver.quit()
                    logging.info(f"Открыть браузер: Процесс {
                                 self.process_number} закрыл браузер.")

                except Exception as e:
                    logging.error(f"Открыть браузер: Процесс {
                                  self.process_number} не смог закрыть браузер: {e}")

            if self.process and self.process.is_running():
                try:
                    self.process.terminate()
                    self.process.wait(timeout=5)
                    logging.info(f"Открыть браузер: Процесс {
                                 self.process_number} завершён.")

                except psutil.NoSuchProcess:
                    logging.error(f"Открыть браузер: Процесс {
                                  self.process_number} уже завершён.")

                except psutil.TimeoutExpired:
                    logging.error(f"Открыть браузер: Процесс {
                                  self.process_number} не завершился вовремя.")
