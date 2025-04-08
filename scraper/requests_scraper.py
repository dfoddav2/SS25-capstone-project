from utils.car_details_scraper import scrape_car_details_from_soup
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
import pandas as pd
import requests
import json
import os


def read_car_links_from_file(file_path="../all_car_links.json"):
    """Reads car links from the `all_car_links.json` file"""
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {file_path}")
        return {}
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return {}


def scrape_car_details_from_url(url, make):
    """Scrapes car details from a URL, returning a tuple of car details."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            return {"url": url, "make": make} | scrape_car_details_from_soup(soup)
        else:
            print(f"Failed to retrieve page: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred while fetching the URL: {e}")
        return None


def scrape_car_details_by_make(make):
    """Scrape car details of a single car make."""
    links = read_car_links_from_file()
    if make in links:
        try:
            car_links = links[make]
            print(f"\n--- Found {len(car_links)} links for make: {make} ---\n")
            car_details_list = []

            i = 1
            for link in car_links:
                details = scrape_car_details_from_url(link, make)
                if details:
                    car_details_list.append(details)
                print(f"-> {i}/{len(car_links)}", end="\r")
                i += 1
            print("\nCar details scraped successfully for make:", make)
            print(f"- Total car details scraped: {len(car_details_list)}")
            print(
                f"- Missed car details: {len(car_links) - len(car_details_list)}")
            return car_details_list

        except Exception as e:
            print(
                f"\n!!! An error occurred while scraping car details: {e} !!!\n")

    else:
        print(f"No links found for make: {make} \nDoes this brand exist?")
        exit(1)


def parallel_scrape_car_details_by_make(make):
    """Scrape car details of a single car make in parallel using threads."""
    links = read_car_links_from_file()
    if make not in links:
        print(f"No links found for make: {make} \nDoes this brand exist?")
        exit(1)

    car_links = links[make]
    print(f"\n--- Found {len(car_links)} links for make: {make} ---\n")
    car_details_list = []

    # For network-bound tasks, you might allow more threads than CPU cores.
    max_workers = os.cpu_count() * 4  # for example, trying twice the CPU count
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all requests concurrently.
        futures = {executor.submit(
            scrape_car_details_from_url, link, make): link for link in car_links}
        for i, future in enumerate(as_completed(futures), start=1):
            details = future.result()
            if details:
                car_details_list.append(details)
            print(f"-> {i}/{len(car_links)} processed", end="\r")
    print("\nCar details scraped successfully for make:", make)
    print(f"- Total car details scraped: {len(car_details_list)}")
    print(f"- Missed car details: {len(car_links) - len(car_details_list)}")
    return car_details_list


def scrape_make_car_details(make):
    """Scrape car details of a single car make."""
    links = read_car_links_from_file()
    if make in links:
        car_details_list = scrape_car_details_by_make(make)
        df = pd.DataFrame(car_details_list)
        print(df.head())
        df.to_parquet(f"car_details_{make}.parquet", index=False)
        print(
            f"\nCar details saved to car_details_{make}.parquet\n")

    else:
        print(f"No links found for make: {make} \nDoes this brand exist?")
        exit(1)


def scrape_all_car_details(start_from=None):
    """Scrape car details from urls for all cars, by make, optionally starting from a specific make."""
    links = read_car_links_from_file()
    i = 0
    total = 0
    if start_from:
        try:
            start_index = list(links.keys()).index(start_from)
            links = dict(list(links.items())[start_index:])
        except ValueError:
            print(f"Make {start_from} not found in the list.")
            exit(1)
    else:
        start_index = 0
    parralel = None
    while parralel not in ["y", "Y", "n", "N"]:
        parralel = input(
            "Do you want to scrape car details in parallel? (y/n): ")
    if parralel in ["y", "Y"]:
        parallel = True
    else:
        parallel = False
    for make in list(links.keys()):
        print(f"\n--- Scraping car details for make: {make} ---")
        print(f"{i}/{len(list(links.keys()))} makes done\n")
        if parallel:
            print("Scraping in parallel...")
            car_details_list = parallel_scrape_car_details_by_make(make)
        else:
            print("Scraping sequentially...")
            car_details_list = scrape_car_details_by_make(make)
        df = pd.DataFrame(car_details_list)
        append_to_consolidated_parquet(df)
        i += 1
        total += len(car_details_list)
    print(f"--- \nAll car details scraped successfully.\n ---")
    print(f"- Total car details scraped: {total}")


def append_to_consolidated_parquet(new_df, consolidated_file="all_car_details.parquet"):
    """
    Appends new_df to an existing consolidated Parquet file by reading
    the current file, concatenating, and re-saving.
    """
    if os.path.exists(consolidated_file):
        # Read existing data
        existing_df = pd.read_parquet(consolidated_file)
        # Concatenate new data
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        combined_df = new_df
    # Save back to Parquet
    combined_df.to_parquet(consolidated_file, index=False)
    print(
        f"Appended {len(new_df)} rows; new total: {len(combined_df)} rows.\n")
