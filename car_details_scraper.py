from bs4 import BeautifulSoup
import re
from datetime import datetime

class ElementNotFoundError(Exception):
    """Custom exception for element not found errors."""
    def __init__(self, message):
        super().__init__(message)
        self.message = message

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
                return None
        else:
            return None
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def scrape_car_title(soup):
    """Scrapes the car title from the soup object."""
    try:
        title = soup.find('h1').find('div').find('span')
        if title:
            return title.text.strip()
        else:
            raise ElementNotFoundError("Car title not found")
    except ElementNotFoundError as e:
        print(f"\n!!! Element not found: {e.message} !!!\n")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def scrape_price(soup):
    """Scrape the car price from the soup object."""
    try:
        price = soup.find('span', {'class': 'PriceInfo_price__XU0aF'}).text.strip()
        if price:
            # Extract the numeric part of the price
            price_numeric = re.sub(r'[^\d]', '', price)
            return int(price_numeric)
        else:
            raise ElementNotFoundError("Car price not found")
    except ElementNotFoundError as e:
        print(f"\n!!! Element not found: {e.message} !!!\n")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def scrape_car_mileage(soup):
    """Scrapes the car mileage from the soup object."""
    try:
        mileage = scrape_relative_div(soup, "Mileage")
        if mileage:
            return int(mileage.split(" ")[0].replace(",", ""))  # Extract the numeric part
        else:
            raise ElementNotFoundError("Car mileage not found")
    except ElementNotFoundError as e:
        print(f"\n!!! Element not found: {e.message} !!!\n")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def scrape_fuel_type(soup):
    """Scrapes the fuel type from the soup object."""
    try:
        fuel_type = scrape_relative_div(soup, "Fuel type")
        if fuel_type:
            return fuel_type
        else:
            raise ElementNotFoundError("Fuel type not found")
    except ElementNotFoundError as e:
        print(f"\n!!! Element not found: {e.message} !!!\n")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def scrape_gearbox(soup):
    """Scrapes the gearbox type from the soup object."""
    try:
        gearbox = scrape_relative_div(soup, "Gearbox")
        if gearbox:
            return gearbox
        else:
            raise ElementNotFoundError("Gearbox not found")
    except ElementNotFoundError as e:
        print(f"\n!!! Element not found: {e.message} !!!\n")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def scrape_power(soup):
    """Scrapes the power from the soup object."""
    try:
        power = scrape_relative_div(soup, "Power")
        if power:
            return int(re.search(r'\((\d+)\s*hp\)', power).group(1))
        else:
            raise ElementNotFoundError("Power not found")
    except ElementNotFoundError as e:
        print(f"\n!!! Element not found: {e.message} !!!\n")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def scrape_first_registration(soup):
    """Scrapes the first registration date from the soup object and converts it to ISO format."""
    try:
        first_registration_text = scrape_relative_div(soup, "First registration")
        if first_registration_text:
            first_registration = first_registration_text.strip()
            # Parse the date string
            month, year = map(int, first_registration.split('/'))
            # Create a datetime object for the first day of the month
            date_object = datetime(year, month, 1)
            # Convert to ISO format (YYYY-MM-DD)
            # TEXT as ISO8601 strings ("YYYY-MM-DD").
            iso_date = date_object.strftime('%Y-%m-%d')
            return iso_date
        else:
            raise ElementNotFoundError("First registration not found")
    except ElementNotFoundError as e:
        print(f"\n!!! Element not found: {e.message} !!!\n")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None