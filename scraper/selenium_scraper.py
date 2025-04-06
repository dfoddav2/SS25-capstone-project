from utils.selenium_scraper_setup import setup_selenium_driver, get_page_source, parse_html
from utils.car_details_scraper import scrape_car_title, scrape_price, scrape_car_mileage, scrape_fuel_type, scrape_gearbox, scrape_power, scrape_first_registration
from utils.category_page_scraper import extract_car_links
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from urllib.parse import urlencode, urljoin
import sqlite3
import random
import time


class CarScraperSelenium:
    def __init__(self, database_file='car_listings.db', base_url="https://www.autoscout24.com"):
        """Initializes the CarScraper with a database connection and base URL."""
        self.database_file = database_file
        self.base_url = base_url
        self.conn = sqlite3.connect(self.database_file)
        self.cursor = self.conn.cursor()
        self.create_table()  # Ensure the table exists
        self.driver = setup_selenium_driver()  # Initialize the Selenium Driver
        self.car_links = []  # List to store car links
        self.has_handled_consent = False  # Flag to check if consent has been handled
        self.user_agents = [
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
        self.base_category_url = "https://www.autoscout24.com/lst"

    def change_user_agent(self):
        """Changes the User-Agent of the Selenium WebDriver."""
        new_user_agent = random.choice(self.user_agents)
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                                    "userAgent": new_user_agent})
        print(f"\n-- User-Agent rotated to: {new_user_agent} --\n")

    def handle_consent_popup(self):
        """Handles the consent popup by declining cookies, must be done once per session."""
        # Handle the consent popup
        if self.has_handled_consent:
            print("\n!!! Consent popup already handled. !!!\n")
            return  # Consent popup already handled
        try:
            decline_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, 'button[data-testid="as24-cmp-decline-all-button"]'))
            )
            decline_button.click()
            print("\nConsent popup declined...")
            # Wait for the consent popup to disappear
            WebDriverWait(self.driver, 5).until(
                EC.invisibility_of_element_located(
                    (By.CSS_SELECTOR, 'button[data-testid="as24-cmp-decline-all-button"]'))
            )
            print("Consent popup disappeared.\n")
            self.has_handled_consent = True  # Set the flag to true
        except Exception as e:
            print(f"An error occurred while handling the consent popup: {e}")
            print("No consent popup found.")

    def get_car_links(self):
        """Gets all car links from all car makes one at a time, including power filter and pagination."""
        try:
            with open('car_makes.txt', 'r') as f:
                car_makes = f.read().splitlines()
            print(f"Car makes loaded from file.")
            # Loop through car makes
            i = 1
            for car_make in car_makes:
                print("\nScraping car make:", car_make)
                make_url = self.base_category_url + '/' + car_make
                num_offers = self.get_number_of_offers(make_url)

                if num_offers is not None and num_offers < 500:
                    print(
                        f"Less than 500 offers for {car_make}, doing a simple scrape.")
                    self.get_car_links_paginated(make_url)
                else:
                    print(
                        f"-- More than 500 offers for {car_make} ({num_offers if num_offers is not None else 'unknown'}), looping through power ranges. --\n")
                    # Loop through horsepower ranges with variable increments
                    self.get_car_links_power_filtered(make_url)

        except Exception as e:
            print(f"An error occurred: {e}")

    def get_car_make_links_parallel(self, car_make):
        """Gets all car links in parallel by make, with power filter and pagination."""
        try:
            print(f"\nScraping car make: {car_make}")
            make_url = self.base_category_url + '/' + car_make
            num_offers = self.get_number_of_offers(make_url)

            if num_offers is not None and num_offers < 500:
                print(
                    f"Less than 500 offers for {car_make}, doing a simple scrape.")
                self.get_car_links_paginated(make_url)
            else:
                print(
                    f"More than 500 offers for {car_make} ({num_offers if num_offers is not None else 'unknown'}), looping through power ranges.")
                # Loop through horsepower ranges with variable increments
                self.get_car_links_power_filtered(make_url)

        except Exception as e:
            print(f"An error occurred: {e}")

        finally:
            # Write the car links out to a file
            try:
                with open(f"./car_links/{car_make}_links.txt", 'w') as f:
                    for link in self.car_links:
                        f.write(link + '\n')
                print(f"\nCar links saved to {car_make}_links.txt\n")
            except Exception as e:
                print(
                    f"\n!!! An error occurred while saving car links: {e} !!!\n")

    def get_car_links_single_make_from_kw(self, make, from_kw):
        """Gets just the data for a single car make, with power filter and pagination, starting from a specific kw."""
        try:
            with open('./car_make_metadata/car_makes.txt', 'r') as f:
                car_makes = f.read().splitlines()
            print(f"Car makes loaded from file.")

            if make not in car_makes:
                raise ValueError(
                    f"Car make '{make}' not found in car_makes.txt")

            print("\nScraping car make:", make)
            make_url = self.base_category_url + '/' + make
            num_offers = self.get_number_of_offers(make_url)

            if num_offers is not None and num_offers < 500:
                print(
                    f"Less than 500 offers for {make}, doing a simple scrape.")
                self.get_car_links_paginated(make_url)
            else:
                print(
                    f"More than 500 offers for {make} ({num_offers if num_offers is not None else 'unknown'}), looping through power ranges.")
                # Loop through horsepower ranges with variable increments
                if from_kw < 1:
                    from_kw = 1
                elif from_kw > 1000:
                    from_kw = 9999

                self.get_car_links_power_filtered(make_url, from_kw)

        except Exception as e:
            print(f"An error occurred: {e}")

    def get_car_links_power_filtered(self, make_url, min_kw=1):
        """Gets all car links of a brand with power filter, wrapping paginated scraping."""
        try:
            # Loop through horsepower ranges with variable increments
            kw = min_kw
            while kw <= 1000:
                min_kw = kw
                # Increment kw based on ranges
                if kw < 10:
                    kw += 9
                elif kw < 20:
                    kw += 10
                elif kw < 30:
                    kw += 5
                elif kw < 40:
                    kw += 2
                elif kw <= 250:
                    kw += 1
                elif kw < 350:
                    kw += 2
                elif kw < 400:
                    kw += 5
                elif kw < 500:
                    kw += 10
                elif kw < 600:
                    kw += 20
                elif kw < 750:
                    kw += 25
                elif kw < 1000:
                    kw += 50
                else:
                    kw += 50
                max_kw = kw

                # Construct the URL with power filter parameters
                params = {
                    'atype': 'C',
                    'cy': 'D,A,B,E,F,I,L,NL',
                    'damaged_listing': 'exclude',
                    'desc': '0',
                    'powerfrom': min_kw,
                    'powerto': max_kw - 1,
                    'powertype': 'kw',
                    'sort': 'standard',
                    'source': 'homepage_search-mask',
                    'ustate': 'N,U'
                }

                url_params = urlencode(params)
                filtered_url = urljoin(make_url, '?' + url_params)

                print(
                    f"\n-- {len(self.car_links)} car links found so far. --\n")
                print(
                    f"\nScraping with power filter: {min_kw} kw to {max_kw - 1} kw - URL: {filtered_url}\n")
                self.get_car_links_paginated(filtered_url)

        except Exception as e:
            print(f"An error occurred: {e}")

    def get_car_links_paginated(self, filtered_url):
        """Scrapes car links from a single filtered page, including pagination."""
        try:
            self.driver.get(filtered_url)  # Get the page
            i = 1  # Initialize page counter
            last_scraped_page = 0  # Initialize last scraped page
            time.sleep(5)  # Wait for the page to load

            if not self.has_handled_consent:
                self.handle_consent_popup()

            while True:  # Loop through pagination
                html = self.driver.page_source
                soup = parse_html(html)

                if (i > 20):
                    print(
                        "\n\n\n!!! Went over 20 pages. Error in scraping. !!!\n\n\n")

                if i > last_scraped_page:
                    print(f"Scraping page {i}...")
                    self.car_links.extend(
                        extract_car_links(soup, self.base_url))

                # Find the "Next" button
                try:
                    next_button_li = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//li[contains(@class, "prev-next")]/button[@aria-label="Go to next page"]'))
                    )
                    # print("Nex button is disabled: ",
                    #       next_button_li.get_attribute("aria-disabled"))

                    # Check if the button is disabled
                    if next_button_li.get_attribute("aria-disabled") == "true":
                        print("\nNext button is disabled. End of pagination.\n")
                        break  # Exit the loop if the button is disabled

                    # Click the "Next" button
                    next_button_li.click()
                    # print("Clicked 'Next' button. Waiting for page to load...")
                    # Wait for the page to load and the current page number to update
                    try:
                        is_next_page = WebDriverWait(self.driver, 10).until(
                            lambda driver: self.get_current_page_number() == i + 1
                        )
                        # print("Successfully moved to the next page: ", is_next_page)

                        # print(f"Moved to page {i + 1}")
                        last_scraped_page = i  # Update last scraped page
                        i += 1  # Increment page counter

                    except:
                        print(
                            "\n!!! Timeout waiting for page to load. Retrying... !!!\n")
                        self.driver.refresh()  # Refresh the page
                        time.sleep(5)  # Give the page some time to load
                        continue  # Continue to the next iteration of the loop

                except:
                    print("No more 'Next' button found.  End of pagination.")
                    break  # No more "Next" button, exit the loop

        except Exception as e:
            print(f"An error occurred while scraping a filtered page: {e}")

    # ----- SCRAPING UTILITY FUNCTIONS ----
    def get_number_of_offers(self, url):
        """Gets the number of offers from the category page."""
        try:
            self.driver.get(url)
            time.sleep(5)  # Wait for the page to load

            # Handle the consent popup
            if not self.has_handled_consent:
                self.handle_consent_popup()

            html = self.driver.page_source
            soup = parse_html(html)

            h1_tag = soup.find('h1', {'data-testid': 'list-header-title'})
            if h1_tag:
                text = h1_tag.text
                # Extract the number from the text
                number = int(text.split(' ')[0].replace(',', ''))
                return number
            else:
                print("H1 tag not found.")
                return None
        except Exception as e:
            print(f"An error occurred while getting the number of offers: {e}")
            return None

    def get_current_page_number(self):
        """Gets the current page number from the aria-current attribute."""
        try:
            # print("Getting current page number...")
            current_page_button = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//button[@aria-current="page"]'))
            )
            # print("Current page number found:", current_page_button.text)
            return int(current_page_button.text)
        except:
            print("Could not find current page number, returning -1")
            return -1

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
                    self.change_user_agent()

        except Exception as e:
            print(f"An error occurred: {e}")

    # ----- SCRAPING CAR DETAILS -----
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
            car_data = (url, car_title, price, car_mileage,
                        fuel_type, gearbox, power, first_registration)
            self.save_to_database(car_data)

            time.sleep(random.uniform(1, 3))  # Add delay

        except Exception as e:
            print(f"\n!!! An error occurred: {e} !!!\n")

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
            print(
                f"\n!!! An error occurred while saving to database: {e} !!!\n")
        print("\nData saved to database.\n")
        return True

    def close(self):
        """Closes the database connection and the Selenium WebDriver."""
        self.conn.close()
        self.driver.quit()
