from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from typing import List, Optional
import time

class BrowserClient:
    def __init__(self) -> None:
        options = Options()
        options.add_argument("--user-data-dir=chrome-data")
        options.add_argument("--start-maximized")
        self.driver: WebDriver = webdriver.Chrome(options=options)

    def get(self, url: str) -> None:
        self.driver.get(url)

    def find_element(self, by: By, value: str) -> Optional[WebElement]:
        try:
            return self.driver.find_element(by, value)
        except Exception:
            return None

    def find_elements(self, by: By, value: str) -> List[WebElement]:
        try:
            return self.driver.find_elements(by, value)
        except Exception:
            return []

    def quit(self) -> None:
        self.driver.quit()

    def sleep(self, seconds: float) -> None:
        time.sleep(seconds)
