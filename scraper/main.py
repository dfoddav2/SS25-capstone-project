from selenium_scraper import CarScraperSelenium
from requests_scraper import scrape_make_car_details, scrape_all_car_details
from concurrent.futures import ProcessPoolExecutor
import os


def parallel_scrape_car_links():
    """Function to scrape car links in parallel."""
    try:
        print("\nProceeding with parallel scraping...\n")
        print("- Setting up parallel scrapers...")
        max_workers = int(os.cpu_count() * 0.8)
        print(f"- Using {max_workers} workers for parallel scraping.")
        # Read car makes from file
        with open('./car_make_metadata/car_makes.txt', 'r') as f:
            car_makes = f.read().splitlines()
        print(f"- Car makes loaded from file.")
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            for _ in executor.map(handle_parallel_scrape_car_make, car_makes):
                pass  # Wait for all processes to complete
    except Exception as e:
        print(f"An error occurred during parallel scraping: {e}")
        exit(1)
    finally:
        print("\n--- Parallel scraping completed. ---\n")


def handle_parallel_scrape_car_make(car_make):
    """Function to scrape car make in parallel."""
    scraper = CarScraperSelenium()
    try:
        print(f"\n--- Starting scraping for {car_make} ---\n")
        scraper.get_car_make_links_parallel(car_make)
        print(f"\n--- Finished scraping for {car_make} ---\n")
    finally:
        scraper.close()


def singular_scrape_car_links():
    print("\nProceeding with single-threaded scraping...\n")
    singular = input("Do you want to scrape a single car make? (y/n): ")
    if singular.lower() == 'y':
        car_make = input("Enter the car make to scrape: ")
        from_kw = int(input("Enter the minimum power in kw: "))
    elif singular.lower() == 'n':
        car_make = None
    else:
        print("\n!!! Invalid input. Exiting... !!!\n")
        exit(1)
    # category_url = input("Enter the category page URL to scrape: ")
    print("\nSetting up scraper...")
    scraper = CarScraperSelenium()  # Instantiate the CarScraper
    print("Scraper setup complete. Commencing crawling...\n")
    try:
        if car_make:
            scraper.get_car_links_single_make_from_kw(car_make, from_kw)
        else:
            scraper.get_car_links()
        print(f"\nFound {len(scraper.car_links)} car links.")
        print("Last 5 car links: ", scraper.car_links[-5:])
    except KeyboardInterrupt:
        print(
            "\n!!! KeyboardInterrupt detected. Saving car links before exiting... !!!\n")
    finally:
        try:
            # Write the car links to a file
            if (car_make):
                with open(f"car_links_{car_make}.txt", 'w') as f:
                    for link in scraper.car_links:
                        f.write(link + '\n')
                print(
                    f"\nCar links saved to {car_make}_links.txt\n")
            else:
                with open('car_links.txt', 'w') as f:
                    for link in scraper.car_links:
                        f.write(link + '\n')
                print("\nCar links saved to car_links.txt\n")
        except Exception as e:
            print(
                f"\n!!! An error occurred while saving car links: {e} !!!\n")
        finally:
            scraper.close()


if __name__ == '__main__':
    print("""
    ___         __                              __     _____                                
   /   | __  __/ /_____  ______________  __  __/ /_   / ___/______________ _____  ___  _____
  / /| |/ / / / __/ __ \/ ___/ ___/ __ \/ / / / __/   \__ \/ ___/ ___/ __ `/ __ \/ _ \/ ___/
 / ___ / /_/ / /_/ /_/ (__  ) /__/ /_/ / /_/ / /_    ___/ / /__/ /  / /_/ / /_/ /  __/ /    
/_/  |_\__,_/\__/\____/____/\___/\____/\__,_/\__/   /____/\___/_/   \__,_/ .___/\___/_/     
                                                                        /_/                 """)
    print("Welcome!\n")
    option = input(
        "What do you want to do?\n\n1. Scrape car links (requires selenium with driver)\n2. Scrape car details\n3. Consolidate car links\n4. Exit\n\nEnter your choice: ")
    if option == '1':
        print("\n--- Scraping car links ---\n")
        parallel = input("Do you want to scrape in parallel? (y/n): ")
        if parallel.lower() == 'y':
            parallel_scrape_car_links()

        elif parallel.lower() == 'n':
            singular_scrape_car_links()
    elif option == '2':
        singular_make = input(
            "Do you want to scrape a single car make? (y/n): ")
        if singular_make.lower() == 'y':
            print(
                f"\n--- This will consolidate details in the file 'car_links_[make-name].parquet' ---")
            make = input("Enter the car make to scrape details for: ")
            scrape_make_car_details(make)
        elif singular_make.lower() == 'n':
            print(
                "\n--- This will consolidate details in the file 'all_car_links.parquet' ---")
            make = input(
                "Enter the car make to scrape details starting from (or leave blank to scrape all): ")
            if make:
                scrape_all_car_details(make)
            else:
                scrape_all_car_details()
        else:
            print("\n!!! Invalid input. Exiting... !!!\n")
            exit(1)
    elif option == '3':
        print("\n--- Consolidating car links ---\n")
        print("\n!!! Consolidating car links is not yet implemented. Exiting... !!!\n")
        exit(1)
    elif option == '4':
        print("\nExiting...\n")
        exit(0)

    else:
        print("\n!!! Invalid input. Exiting... !!!\n")
        exit(1)
