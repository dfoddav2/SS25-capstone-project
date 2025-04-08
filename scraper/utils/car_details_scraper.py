from bs4 import BeautifulSoup
from datetime import datetime
import re


class ElementNotFoundError(Exception):
    """Custom exception for element not found errors."""

    def __init__(self, message):
        super().__init__(message)
        self.message = message


def scrape_car_details_from_soup(soup):
    """Scrapes car details from a soup object, retuning a tuple of car details."""
    try:
        # First  check that the soup object is valid
        if not soup or not isinstance(soup, BeautifulSoup):
            raise ValueError("Invalid soup object provided")

        # Check that the car listing still exists
        no_longer_exists = soup.find(string="This listing no longer exists.")
        if no_longer_exists:
            print("\n!!! This listing no longer exists !!!\n")
            return None

        # Scrape car details
        car_title = scrape_car_title(soup)
        price = scrape_price(soup)
        seller = scrape_seller(soup)
        location = scrape_location(soup)
        num_images = scrape_num_images(soup)
        basic_data = scrape_basic_data(soup)
        vehicle_history = scrape_vehicle_history(soup)
        technical_data = scrape_technical_data(soup)
        energy_consumption = scrape_energy_consumption(soup)
        equipment = scrape_equipment(soup)
        colour_and_upholstery = scrape_colour_and_upholstery(soup)

        # Prepare data for database insertion
        car_data = {
            "car_title": car_title,
            "price": price,
            "seller": seller,
            "location": location,
            "num_images": num_images,
        } | basic_data | vehicle_history | technical_data | energy_consumption | equipment | colour_and_upholstery
        return car_data

    except Exception as e:
        print(f"\n!!! An error occurred: {e} !!!\n")


def scrape_relative_div(soup, target_text):
    """Scrape the div relative to the target text."""
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


def scrape_dt_dd(soup, target_text):
    """Scrape the dt and dd elements relative to the target text."""
    try:
        # Find the <dt> element with the target text
        dt_element = soup.find('dt', string=target_text)

        if dt_element:
            # Navigate to the corresponding <dd> element
            dd_element = dt_element.find_next('dd')

            if dd_element:
                return dd_element.text.strip()
            else:
                raise ElementNotFoundError(
                    f"<dd> not found in the soup object for <dt> with text '{target_text}'")
        else:
            raise ElementNotFoundError(
                f"<dt> with text '{target_text}' not found in the soup object")
    except ElementNotFoundError as e:
        # print(f"\n!!! Element not found: {e.message} !!!\n")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def scrape_dt_dd_li(soup, target_text):
    """Scrape the dt and dd elements relative to the target text."""
    try:
        dt_elements = soup.find_all('dt')
        for dt in dt_elements:
            # print(f"dt: {dt.text.strip()}")
            if dt.get_text(strip=True) == target_text:
                # Navigate to the corresponding <dd> element
                dd_element = dt.find_next('dd')

                if dd_element:
                    li_elements = dd_element.find_all('li')
                    string_representation = ";".join(
                        [li.text.strip() for li in li_elements])
                    # print(f"dd: {string_representation}")
                    if string_representation:
                        return string_representation
                    else:
                        return None
                else:
                    raise ElementNotFoundError(
                        f"<dd> not found in the soup object for <dt> with text '{target_text}'")
        raise ElementNotFoundError(
            f"<dt> with text '{target_text}' not found in the soup object")
    except ElementNotFoundError as e:
        # print(f"\n!!! Element not found: {e.message} !!!\n")
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
        # print(f"\n!!! Element not found: {e.message} !!!\n")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def scrape_price(soup):
    """Scrape the car price from the soup object."""
    try:
        price = soup.find(
            'span', {'class': 'PriceInfo_price__XU0aF'}).text.strip()
        if price:
            # Extract the numeric part of the price
            price_numeric = re.sub(r'[^\d]', '', price.split(".")[0])
            return int(price_numeric)
        else:
            raise ElementNotFoundError("Car price not found")
    except ElementNotFoundError as e:
        # print(f"\n!!! Element not found: {e.message} !!!\n")
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
        # print(f"\n!!! Element not found: {e.message} !!!\n")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def scrape_seller(soup):
    """Scrapes the seller type from the soup object."""
    try:
        seller = scrape_relative_div(soup, "Seller")
        if seller:
            return seller
        else:
            raise ElementNotFoundError("Seller not found")
    except ElementNotFoundError as e:
        # print(f"\n!!! Element not found: {e.message} !!!\n")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def scrape_location(soup):
    """Scrapes the location from the soup object."""
    try:
        location = soup.find(
            "a", {"class": "LocationWithPin_locationItem__tK1m5"})
        if location:
            # print("Location:", location)
            return location.text.strip()
        else:
            raise ElementNotFoundError("Location not found")
    except ElementNotFoundError as e:
        # print(f"\n!!! Element not found: {e.message} !!!\n")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def scrape_num_images(soup):
    """Scrapes the number of images from the soup object."""
    try:
        num_images = soup.find(
            'span', {'class': 'image-gallery-index-total'}).text.strip()
        if num_images and num_images.isdigit():
            return int(num_images)
        else:
            raise ElementNotFoundError("Number of images not found")
    except ElementNotFoundError as e:
        # print(f"\n!!! Element not found: {e.message} !!!\n")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def scrape_basic_data(soup):
    """Scrapes the basic data section of the car from the soup object."""
    try:
        # Check if Basic data section exists
        basic_data_section = soup.find(
            'h2', string="Basic Data")
        if not basic_data_section:
            # print("\n!!! Basic data section not found !!!\n")
            return {
                "body_type": None,
                "used_type": None,
                "drivetrain": None,
                "seats": None,
                "doors": None,
                "country_version": None,
                "model_code": None
            }

        body_type = scrape_dt_dd(soup, "Body type")
        used_type = scrape_dt_dd(soup, "Type")
        drivetrain = scrape_dt_dd(soup, "Drivetrain")
        seats = scrape_dt_dd(soup, "Seats")
        doors = scrape_dt_dd(soup, "Doors")
        country_version = scrape_dt_dd(soup, "Country version")
        model_code = scrape_dt_dd(soup, "Model code")

        return {
            "body_type": body_type,
            "used_type": used_type,
            "drivetrain": drivetrain,
            "seats": seats,
            "doors": doors,
            "country_version": country_version,
            "model_code": model_code
        }
    except Exception as e:
        print(f"An error occurred: {e}")
        return {
            "body_type": None,
            "used_type": None,
            "drivetrain": None,
            "seats": None,
            "doors": None,
            "country_version": None,
            "model_code": None
        }


def scrape_vehicle_history(soup):
    """Scrapes the vehicle history section of the car from the soup object."""
    try:
        # Check if Vehicle History section exists
        basic_data_section = soup.find(
            'h2', string="Vehicle History")
        if not basic_data_section:
            # print("\n!!! Vehicle History section not found !!!\n")
            return {
                "mileage": None,
                "first_registration": None,
                "general_inspection": None,
                "previous_owner": None,
                "full_service_history": None,
                "non_smoker_service": None
            }

        # Mileage - Turned to numeric value
        mileage = scrape_dt_dd(soup, "Mileage")
        if mileage:
            mileage = int(mileage.split(" ")[0].replace(",", ""))
        # First registration - Turned to ISO format
        first_registration = scrape_dt_dd(soup, "First registration")
        if first_registration:
            month, year = map(int, first_registration.split('/'))
            iso_date = f"{year:04d}-{month:02d}"
            first_registration = iso_date
        general_inspection = scrape_dt_dd(soup, "General inspection")
        # Previous owner - Turned to numeric value
        previous_owner = scrape_dt_dd(soup, "Previous owner")
        if previous_owner and previous_owner.isdigit():
            previous_owner = int(previous_owner)
        else:
            previous_owner = None
        full_service_history = scrape_dt_dd(soup, "Full service history")
        non_smoker_service = scrape_dt_dd(soup, "Non-smoker service")

        return {
            "mileage": mileage,
            "first_registration": first_registration,
            "general_inspection": general_inspection,
            "previous_owner": previous_owner,
            "full_service_history": full_service_history,
            "non_smoker_service": non_smoker_service
        }
    except Exception as e:
        print(f"An error occurred: {e}")
        return {
            "mileage": None,
            "first_registration": None,
            "general_inspection": None,
            "previous_owner": None,
            "full_service_history": None,
            "non_smoker_service": None
        }


def scrape_technical_data(soup):
    """Scrapes the technical data section of the car from the soup object."""
    try:
        # Check if Technical Data section exists
        technical_data_section = soup.find(
            'h2', string="Technical Data")
        if not technical_data_section:
            # print("\n!!! Technical Data section not found !!!\n")
            return {
                "power": None,
                "gearbox": None,
                "engine_size": None,
                "gears": None,
                "cylinders": None,
                "empty_weight": None
            }

        # Power - Turned to numeric value
        power = scrape_dt_dd(soup, "Power")
        if power:
            power = int(re.search(r'\((\d+)\s*hp\)', power).group(1))
        gearbox = scrape_dt_dd(soup, "Gearbox")
        # Engine size - Turned to numeric value
        engine_size = scrape_dt_dd(soup, "Engine size")
        if engine_size:  # In cc
            engine_size = int(engine_size.split(" ")[0].replace(",", ""))
        gears = scrape_dt_dd(soup, "Gears")
        cylinders = scrape_dt_dd(soup, "Cylinders")
        # Empty weight - Turned to numeric value
        empty_weight = scrape_dt_dd(soup, "Empty weight")
        if empty_weight:  # In kg
            empty_weight = int(empty_weight.split(" ")[0].replace(",", ""))

        return {
            "power": power,
            "gearbox": gearbox,
            "engine_size": engine_size,
            "gears": gears,
            "cylinders": cylinders,
            "empty_weight": empty_weight
        }

    except Exception as e:
        print(f"An error occurred: {e}")
        return {
            "power": None,
            "gearbox": None,
            "engine_size": None,
            "gears": None,
            "cylinders": None,
            "empty_weight": None
        }


def scrape_energy_consumption(soup):
    """Scrapes the energy consumption section of the car from the soup object."""
    try:
        # Check if Energy Consumption section exists
        energy_consumption_section = soup.find(
            'h2', string="Energy Consumption")
        if not energy_consumption_section:
            # print("\n!!! Energy Consumption section not found !!!\n")
            return {
                "fuel_type": None,
                "fuel_consumption": None,
                "emission_class": None,
                "emissions_sticker": None,
                "co2_emissions": None,
                "electric_range": None
            }

        # Fuel Type
        fuel_type = scrape_fuel_type(soup)
        fuel_consumption = scrape_dt_dd(soup, "Fuel consumption")
        emission_class = scrape_dt_dd(soup, "Emission class")
        emissions_sticker = scrape_dt_dd(soup, "Emissions sticker")
        co2_emissions = scrape_dt_dd(soup, "CO₂-emissions")
        if co2_emissions:
            co2_emissions = int(co2_emissions.split(
                " ")[0].replace(",", "").replace(".", ""))
        electric_range = scrape_dt_dd(soup, "Electric range")
        if electric_range:
            electric_range = int(electric_range.split(
                " ")[0].replace(",", "").replace(".", ""))

        return {
            "fuel_type": fuel_type,
            "fuel_consumption": fuel_consumption,
            "emission_class": emission_class,
            "emissions_sticker": emissions_sticker,
            "co2_emissions": co2_emissions,
            "electric_range": electric_range
        }

    except Exception as e:
        print(f"An error occurred: {e}")
        return {
            "fuel_type": None,
            "fuel_consumption": None,
            "emission_class": None,
            "emissions_sticker": None,
            "co2_emissions": None,
            "electric_range": None
        }


def scrape_equipment(soup):
    """Scrapes the equipment section of the car from the soup object."""
    try:
        # print("\nScraping Equipment section...\n")
        # Check if Equipment section exists
        equipment_section = soup.find(
            'h2', string="Equipment")
        if not equipment_section:
            # print("\n!!! Equipment section not found !!!\n")
            return {
                "comfort_and_convenience": None,
                "entertainment_and_media": None,
                "safety_and_security": None,
                "extras": None
            }

        comfort_and_convenience = scrape_dt_dd_li(
            soup, "Comfort & Convenience")
        entertainment_and_media = scrape_dt_dd_li(
            soup, "Entertainment & Media")
        safety_and_security = scrape_dt_dd_li(soup, "Safety & Security")
        extras = scrape_dt_dd_li(soup, "Extras")

        return {
            "comfort_and_convenience": comfort_and_convenience,
            "entertainment_and_media": entertainment_and_media,
            "safety_and_security": safety_and_security,
            "extras": extras
        }

    except Exception as e:
        print(f"An error occurred: {e}")
        return {
            "comfort_and_convenience": None,
            "entertainment_and_media": None,
            "safety_and_security": None,
            "extras": None
        }


def scrape_colour_and_upholstery(soup):
    """Scrapes the colour and upholstery section of the car from the soup object."""
    try:
        # Check if Colour & Upholstery section exists
        colour_and_upholstery_section = soup.find(
            'h2', string="Colour and Upholstery")
        if not colour_and_upholstery_section:
            # print("\n!!! Colour and Upholstery section not found !!!\n")
            return {
                "exterior_colour": None,
                "manufacturer_colour": None,
                "paint": None,
                "upholstery_colour": None,
                "upholstery": None
            }

        exterior_colour = scrape_dt_dd(soup, "Colour")
        manufacturer_colour = scrape_dt_dd(soup, "Manufacturer colour")
        paint = scrape_dt_dd(soup, "Paint")
        upholstery_colour = scrape_dt_dd(soup, "Upholstery colour")
        upholstery = scrape_dt_dd(soup, "Upholstery")

        return {
            "exterior_colour": exterior_colour,
            "manufacturer_colour": manufacturer_colour,
            "paint": paint,
            "upholstery_colour": upholstery_colour,
            "upholstery": upholstery
        }

    except Exception as e:
        print(f"An error occurred: {e}")
        return {
            "exterior_colour": None,
            "manufacturer_colour": None,
            "paint": None,
            "upholstery_colour": None,
            "upholstery": None
        }
