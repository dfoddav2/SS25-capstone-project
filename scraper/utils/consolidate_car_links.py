import os
import json


def consolidate_car_links(directory="car_links", output_file="all_car_links.json"):
    """
    Consolidates car links from individual brand files into a single JSON file,
    preserving brand indexing.
    """
    all_car_links = {}

    for filename in os.listdir(directory):
        if filename.endswith("_links.txt"):
            brand = filename[:-10]  # Extract brand name from filename
            filepath = os.path.join(directory, filename)

            try:
                with open(filepath, 'r') as f:
                    # Read links, removing whitespace
                    links = {line.strip() for line in f if line.strip()}
                all_car_links[brand] = list(links)
                print(f"Successfully read {len(links)} links for {brand}")

            except Exception as e:
                print(f"Error reading {filename}: {e}")

    # Write all car links to a JSON file
    try:
        with open(output_file, 'w') as outfile:
            # Use indent for readability
            json.dump(all_car_links, outfile, indent=4)
        print(f"All car links consolidated into {output_file}")

    except Exception as e:
        print(f"Error writing to {output_file}: {e}")


if __name__ == "__main__":
    consolidate_car_links()
