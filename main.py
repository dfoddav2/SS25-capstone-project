from general_scraper import setup_selenium_driver, get_page_source, parse_html
from category_page_scraper import extract_car_links
from car_details_scraper import scrape_car_title, scrape_price, scrape_car_mileage, scrape_fuel_type, scrape_gearbox, scrape_power, scrape_first_registration
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import sqlite3

class CarScraper:
    def __init__(self, database_file='car_listings.db', base_url="https://www.autoscout24.com"):
        """Initializes the CarScraper with a database connection and base URL."""
        self.database_file = database_file
        self.base_url = base_url
        self.conn = sqlite3.connect(self.database_file)
        self.cursor = self.conn.cursor()
        self.create_table()  # Ensure the table exists
        self.driver = setup_selenium_driver() # Initialize the Selenium Driver
        self.car_links = []  # List to store car links

    def get_car_links(self, category_url):
        """Gets all car links from a category page, including pagination."""
        try:
            self.driver.get(category_url)
            time.sleep(2)  # Wait for the page to load
            i = 1  # Initialize page counter

            # Handle the consent popup
            try:
                decline_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="as24-cmp-decline-all-button"]'))
                )
                decline_button.click()
                print("Consent popup declined.")
            except:
                print("No consent popup found.")

            while True:  # Loop through pagination
                html = self.driver.page_source
                soup = parse_html(html)

                print(f"\nScraping page {i}...")
                self.car_links.extend(extract_car_links(soup, self.base_url))

                # Find the "Next" button
                try:
                    next_button_li = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//li[contains(@class, "prev-next")]/button[@aria-label="Go to next page"]'))
                    )

                    # Check if the button is disabled
                    if next_button_li.get_attribute("aria-disabled") == "true":
                        print("Next button is disabled. End of pagination.")
                        break  # Exit the loop if the button is disabled

                    # Click the "Next" button
                    next_button_li.click()
                    print("Clicked 'Next' button.  Waiting for page to load...")
                    i += 1  # Increment page counter
                    time.sleep(2)  # Wait for the next page to load

                except:
                    print("No more 'Next' button found.  End of pagination.")
                    break  # No more "Next" button, exit the loop
                
        except Exception as e:
            print(f"An error occurred: {e}")

    def create_table(self):
        """Creates the car_listing table if it doesn't exist."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS car_listing (
                url TEXT PRIMARY KEY,
                title TEXT,
                price INTEGER,
                mileage INTEGER,
                fuel_type TEXT,
                gearbox TEXT,
                power INTEGER,
                first_registration TEXT
            )
        """)
        self.conn.commit()
        
    def save_to_database(self, car_data):
        """Saves scraped car data to the database."""
        try:
            self.cursor.execute("""
                INSERT OR REPLACE INTO car_listing (url, title, price, mileage, fuel_type, gearbox, power, first_registration)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, car_data)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"\n!!! Database error: {e} !!!\n")
        except Exception as e:
            print(f"\n!!! An error occurred while saving to database: {e} !!!\n")
        print("\nData saved to database.\n")
        return True
    
    def scrape_car_details(self, url):
        """Scrapes car details from a single car details page."""
        print(f"\nScraping car details from: {url}")
        try:
            html = get_page_source(self.driver, url)
            soup = parse_html(html)

            car_title = scrape_car_title(soup)
            price = scrape_price(soup)
            car_mileage = scrape_car_mileage(soup)
            fuel_type = scrape_fuel_type(soup)
            gearbox = scrape_gearbox(soup)
            power = scrape_power(soup)
            first_registration = scrape_first_registration(soup)
            
            print(f"- Car title: {car_title}")
            print(f"- Car price: {price}")
            print(f"- Car mileage: {car_mileage}")
            print(f"- Fuel type: {fuel_type}")
            print(f"- Gearbox: {gearbox}")
            print(f"- Power: {power}")
            print(f"- First registration: {first_registration}")

            # Prepare data for database insertion
            car_data = (url, car_title, price, car_mileage, fuel_type, gearbox, power, first_registration)
            self.save_to_database(car_data)

            time.sleep(random.uniform(1, 3))  # Add delay

        except Exception as e:
            print(f"\n!!! An error occurred: {e} !!!\n")

    def scrape_category_page(self, category_url):
        """Scrapes car details from a category page and follows links to car details pages."""
        try:
            html = get_page_source(self.driver, category_url)
            soup = parse_html(html)
            car_links = extract_car_links(soup, self.base_url)

            for i, link in enumerate(car_links):
                self.scrape_car_details(link)

                # Periodic modifications
                if (i + 1) % 10 == 0:  # Clear cookies every 10 pages
                    self.driver.delete_all_cookies()
                    print("Cookies cleared.")

                if (i + 1) % 5 == 0:  # Rotate User-Agent every 5 pages
                    user_agents = [
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.4; rv:124.0) Gecko/20100101 Firefox/124.0",
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/124.0.2478.51",
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/124.0.2478.51",
                        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                        "Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                        "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
                    ]
                    new_user_agent = random.choice(user_agents)
                    self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": new_user_agent})
                    print(f"User-Agent rotated to: {new_user_agent}")

        except Exception as e:
            print(f"An error occurred: {e}")
            
    def close(self):
         """Closes the database connection and the Selenium WebDriver."""
         self.conn.close()
         self.driver.quit()

if __name__ == '__main__':
    category_url = input("Enter the category page URL to scrape: ")
    scraper = CarScraper()  # Instantiate the CarScraper
    try:
        scraper.get_car_links(category_url)
        print(f"\nFound {len(scraper.car_links)} car links.")
    finally:
        scraper.close()  # Close the connection and driver in a finally block