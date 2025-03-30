from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

def setup_selenium_driver():
    """Sets up the Selenium WebDriver with Chrome options."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")  # Set User-Agent
    chrome_options.binary_location = '/usr/bin/'
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# def handle_cloudflare_challenge(driver, timeout=5):
#     """Handles Cloudflare challenges if present."""
#     try:
#         WebDriverWait(driver, timeout).until(
#             EC.presence_of_element_located((By.ID, "challenge-stage"))
#         )
#         print("Cloudflare challenge detected. Waiting...")
#         time.sleep(timeout)  # Give the challenge time to complete
#     except:
#         print("No Cloudflare challenge detected.")

def get_page_source(driver, url):
    """Retrieves the page source using Selenium, handling Cloudflare challenges."""
    driver.get(url)
    # handle_cloudflare_challenge(driver)
    return driver.page_source

def parse_html(html):
    """Parses HTML content with BeautifulSoup."""
    return BeautifulSoup(html, 'html.parser')