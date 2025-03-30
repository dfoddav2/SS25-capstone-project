from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

def scrape_h1(soup):
    try:
        h1 = soup.find('h1')
        if h1:
            return h1.text.strip()
        else:
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def scrape_relative_div(soup, target_text):
    try:
        # Find the element by its text content
        target_element = soup.find(lambda tag: tag.string == target_text)

        if target_element:
            # Navigate to the sibling div (two divs below)
            sibling_div = target_element.find_next('div').find_next('div')

            if sibling_div:
                return sibling_div.text.strip()
            else:
                return "Sibling div not found"
        else:
            return "Target element not found"

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def selenium_scraper(url):
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")  # Set User-Agent

    # Specify the Chrome binary location
    chrome_options.binary_location = '/usr/bin/'  # Or the correct path if different

    # Initialize the Chrome driver
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Load the URL
        driver.get(url)

        # Wait for the Cloudflare challenge to load (max 10 seconds)
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "challenge-stage"))
            )
            print("Cloudflare challenge detected. Waiting...")
            time.sleep(5)  # Give the challenge time to complete
        except:
            print("No Cloudflare challenge detected.")

        # Get the page source after the challenge
        html = driver.page_source

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        # print(soup.prettify())

        # Autoscout24 specific example
        car_title = scrape_h1(soup)
        if car_title:
            print("Car title:", car_title)
        else:
            print("Car title not found.")
        
        car_mileage = scrape_relative_div(soup, "Mileage")
        if car_mileage:
            print("Car mileage:", car_mileage)
        else:
            print("Car mileage not found")
            
        fuel_type = scrape_relative_div(soup, "Fuel type")
        if fuel_type:
            print("Fuel type:", fuel_type)
        else:
            print("Fuel type not found")
            
        gearbox = scrape_relative_div(soup, "Gearbox")
        if gearbox:
            print("Gearbox:", gearbox)
        else:
            print("Gearbox not found")
        
        power = scrape_relative_div(soup, "Power")
        if power:
            print("Power:", power)
        else:
            print("Power not found")
            
        first_registration = scrape_relative_div(soup, "First registration")
        if first_registration:
            print("First registration:", first_registration)
        else:
            print("First registration not found")
            
        # body_type = scrape_relative_div(soup, "Body type")
        # if body_type:
        #     print("Body type:", body_type)
        # else:
        #     print("Body type not found")
        

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        driver.quit()  # Close the browser

if __name__ == '__main__':
    url = 'https://www.autoscout24.com/offers/bmw-330-ea-phev-hybrid-auto-phares-led-camera-carplay-full-electric-gasoline-white-d00bc9c5-5728-4fb1-8de2-8af3c889c746?ipc=recommendation&ipl=homepage-engine-itemBased&position=1&source_otp=t50&ap_tier=t50&mia_tier=t50&boosting_product=mia&relevance_adjustment=boost&applied_mia_tier=t50&source=homepage_most-searched'  # Replace with the actual URL to scrape
    selenium_scraper(url)
    