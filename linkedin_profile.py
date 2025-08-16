from typing import Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from BrowserClient import BrowserClient

def extract_profile_info(browser: BrowserClient) -> str:
    try:
        browser.sleep(3)
        name_elem: Optional[WebElement] = browser.find_element(By.CSS_SELECTOR, "h1")
        headline_elem: Optional[WebElement] = browser.find_element(By.CSS_SELECTOR, "div.text-body-medium")
        name: str = name_elem.text if name_elem else ""
        headline: str = headline_elem.text if headline_elem else ""
        about_section: str = ""
        about_button: Optional[WebElement] = browser.find_element(By.XPATH, "//button[contains(., 'About')]")
        if about_button:
            about_button.click()
            browser.sleep(1)
            about_elem: Optional[WebElement] = browser.find_element(By.XPATH, "//section[contains(@id,'about')]")
            about_section = about_elem.text if about_elem else ""
        return f"{name}\n{headline}\n{about_section}"
    except Exception as e:
        print("Error extracting profile:", e)
        return ""

def send_connect(browser: BrowserClient) -> bool:
    """
    Attempts to send a connection request to the current LinkedIn profile page.
    Returns True if the request was sent, False otherwise.
    """
    try:
        connect_button: Optional[WebElement] = browser.find_element(By.XPATH, "//button[contains(., 'Connect')]")
        if connect_button:
            connect_button.click()
            browser.sleep(1)
            # Confirm send now if dialog appears
            send_button: Optional[WebElement] = browser.find_element(By.XPATH, "//button[contains(., 'Send now') or contains(., 'Send')]")
            if send_button:
                send_button.click()
                browser.sleep(1)
                return True
        return False
    except Exception as e:
        print("Error sending connect request:", e)
        return False
