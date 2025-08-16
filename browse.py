"""
browse.py

This module provides functions to automate browsing and connecting with LinkedIn profiles using Selenium WebDriver.
It includes logic to filter profiles based on mutual connections and to send connection requests inline when possible.

Functions:
- get_mutual_connection_count_from_card_insights_text(insight_string: str) -> int: Extracts the number of mutual connections from a card's insight text. Raises InsightParseException if the string does not contain exactly one number.
- __send_connect_inline(card: WebElement, browser: BrowserClient) -> int: Attempts to send a connection request using the inline button on a profile card. Raises ConnectButtonError or PopupButtonError on failure.
- send_connect_inline(card: WebElement, browser: BrowserClient) -> int: Checks if a profile card meets the mutual connection threshold and sends a connection request if eligible. Raises InsightsNotFoundException, InsightParseException, LowMutualConnectionsError, ConnectButtonError, PopupButtonError, or InlineConnectException on failure.
- get_search_results(browser: BrowserClient, search_url: str, try_inline: bool) -> List[str]: Visits a LinkedIn search URL, optionally tries to connect inline, and collects profile URLs.
- browse_profiles(browser: BrowserClient, try_inline: bool) -> List[str]: Constructs a sample search and returns relevant profile URLs.

Constants:
- MIN_MUTUAL_CONNECTIONS_TO_SEND_CONNECT (int): Minimum mutual connections required to send a connection request.

Custom Exceptions:
- InsightsNotFoundException: Raised when insights are not found for a card.
- LowMutualConnectionsError: Raised when a profile does not have enough mutual connections.
- ConnectButtonError: Raised when the connect button is missing, disabled, or cannot be clicked.
- PopupButtonError: Raised when the popup button is missing, disabled, or cannot be clicked.
- InsightParseException: Raised when the insight text could not be parsed.
- InlineConnectException: Raised when the inline connect process fails.
"""

from typing import List
from selenium.webdriver.common.by import By
from BrowserClient import BrowserClient
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    InvalidSelectorException,
    ElementNotInteractableException,
    ElementClickInterceptedException,
    InvalidElementStateException,
    WebDriverException
)
import re

MIN_MUTUAL_CONNECTIONS_TO_SEND_CONNECT: int = 10

class InsightsNotFoundException(Exception):
    """Raised when insights are not found for the card."""
    pass

class LowMutualConnectionsError(Exception):
    """Raised when the profile does not have enough mutual connections to send a connect request."""
    pass

class ConnectButtonError(Exception):
    """Raised when the connect button is missing, disabled, or cannot be clicked."""
    pass

class PopupButtonError(Exception):
    """Raised when the popup button is missing, disabled, or cannot be clicked."""
    pass

class InsightParseException(Exception):
    """Raised when the insight text could not be parsed."""
    pass

class InlineConnectException(Exception):
    """Raised when the inline connect process fails."""
    pass

def get_mutual_connection_count_from_card_insights_text(insight_string: str) -> int:
    """
    Extracts the number of mutual connections from the provided insight string.
    Args:
        insight_string (str): The text containing mutual connection information.
    Returns:
        int: The number of mutual connections extracted from the string.
    Raises:
        InsightParseException: If the string does not contain exactly one number.
    """
    ### code tripping up in case of 3k followers or _k followers
    match: List[str] = re.findall(r'\d+', insight_string)
    if len(match) != 1:
        raise InsightParseException(f"Expected exactly one number in insight string, found {len(match)}: {insight_string}")
    return int(match[0])

def __send_connect_inline(card: WebElement, browser: BrowserClient) -> int:
    """
    Attempts to send a connection request using the inline 'Connect' button on the given profile card.
    Args:
        card (WebElement): The profile card element.
        browser (BrowserClient): The browser client instance.
    Returns:
        int: 0 on success.
    Raises:
        ConnectButtonError: If the connect button is missing, disabled, or cannot be clicked.
        PopupButtonError: If the popup button is missing, disabled, or cannot be clicked.
    """
    # look for connect button presense
    connect_button: WebElement
    try:
        connect_button = card.find_element(By.XPATH, ".//button[contains(translate(@aria-label, 'CONNECT', 'connect'), 'connect')]")
    except (NoSuchElementException, StaleElementReferenceException, InvalidSelectorException) as e:
        raise ConnectButtonError("Could not find Connect button")
    if not connect_button.is_enabled():
        raise ConnectButtonError("Connect button not enabled")
    
    # scroll to button first or you might run into click issues
    # commented below code because of two reasons
    # - our browser does not support execute_script
    # - even after using the WebDriver of the browser it seems that the button is still not on the screen
    # browser.execute_script("arguments[0].scrollIntoView(true);", button)
    try:
        connect_button.click()
    except (ElementNotInteractableException,
            ElementClickInterceptedException,
            StaleElementReferenceException,
            InvalidElementStateException) as e:
        raise ConnectButtonError("Could not click Connect button")

    popup_button: WebElement
    try:
        popup_button = browser.find_element(By.XPATH, "//button[contains(., 'Send without a note')]")
        print(popup_button.text)
    except (NoSuchElementException, StaleElementReferenceException, InvalidSelectorException) as e:
        print(f"Popup button not found or could not be clicked: {e}")
        raise PopupButtonError(f"Popup button not found: {e}")
    try:
        popup_button.click()
        return 0
    except (ElementNotInteractableException,
            ElementClickInterceptedException,
            StaleElementReferenceException,
            InvalidElementStateException) as e:
        raise PopupButtonError("Could not click Popup button")


def send_connect_inline(card: WebElement, browser: BrowserClient) -> int:
    """
    Checks if the profile card has enough mutual connections and sends a connection request if eligible.
    Args:
        card (WebElement): The profile card element.
        browser (BrowserClient): The browser client instance.
    Returns:
        int: 0 on success.
    Raises:
        InsightsNotFoundException: If the insights section is not found in the card.
        InsightParseException: If the insight text cannot be parsed.
        LowMutualConnectionsError: If the profile does not have enough mutual connections.
        ConnectButtonError: If the connect button is missing, disabled, or cannot be clicked.
        PopupButtonError: If the popup button is missing, disabled, or cannot be clicked.
        InlineConnectException: If the inline connect process fails.
    """
    try:
        insights_div: WebElement
        try:
            insights_div = card.find_element(By.CSS_SELECTOR, "div.entity-result__insights")
            print(insights_div.text)
        except (NoSuchElementException, StaleElementReferenceException, InvalidSelectorException) as e:
            raise InsightsNotFoundException(f"No Insights Found")
        
        # throws InsightParseException
        conn_count = get_mutual_connection_count_from_card_insights_text(insights_div.text)

        print(conn_count)
        if(conn_count < MIN_MUTUAL_CONNECTIONS_TO_SEND_CONNECT):
            raise LowMutualConnectionsError("")
        
        return __send_connect_inline(card, browser)
    except (InsightsNotFoundException, InsightParseException, 
            LowMutualConnectionsError,
            ConnectButtonError, PopupButtonError) as e:
        raise InlineConnectException("Could not send inline connect")


def get_search_results(browser: BrowserClient, search_url: str, try_inline: bool) -> List[str]:
    """
    Visits the given LinkedIn search URL and returns a list of profile URLs for people with at least the minimum required mutual connections.
    If try_inline is True, attempts to send connection requests inline.
    Args:
        browser (BrowserClient): The browser client instance.
        search_url (str): The LinkedIn search URL to visit.
        try_inline (bool): Whether to attempt inline connection requests.
    Returns:
        List[str]: A list of profile URLs matching the criteria.
    """
    browser.get(search_url)
    browser.sleep(5)
    profile_links: List[str] = []
    cards: List[WebElement] = browser.find_elements(By.CSS_SELECTOR, 'div.linked-area')
    if len(cards) == 0:
        return profile_links
    for card in cards:
        if try_inline:
            try:
                send_connect_inline(card, browser)
                continue
            except InlineConnectException as e:
                print(f"Error in inline connect: {e}")
        try:
            link_elem: WebElement = card.find_element(By.XPATH, ".//a[contains(@href, '/in/')]")
            href: str = link_elem.get_attribute("href")
            if href and href not in profile_links:
                profile_links.append(href)
        except (NoSuchElementException, StaleElementReferenceException, InvalidSelectorException) as e:
            print(f"Error finding profile link: {e}")
    return profile_links

def browse_profiles(browser: BrowserClient, try_inline: bool) -> List[str]:
    """
    Constructs a sample LinkedIn search (e.g., for IIT Kharagpur 2nd/3rd degree connections) and returns a list of relevant profile URLs.
    Args:
        browser (BrowserClient): The browser client instance.
        try_inline (bool): Whether to attempt inline connection requests.
    Returns:
        List[str]: A list of relevant profile URLs.
    """
    # Example: IIT Kharagpur, 2nd, '24' or '25' in headline
    # add parameter to query string page=x to browse more than just 10 people
    search_url: str = "https://www.linkedin.com/search/results/people/?keywords=24&network=%5B%22S%22%5D&origin=FACETED_SEARCH&schoolFilter=%5B%22157265%22%5D&sid=ZDR"
    return get_search_results(browser, search_url, try_inline)