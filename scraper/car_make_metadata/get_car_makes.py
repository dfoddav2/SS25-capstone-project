import re


def extract_car_makes(filename="makes.txt"):
    """
    Extracts car makes from an HTML file containing a list of suggestions.

    Args:
        filename (str, optional): The name of the HTML file. Defaults to "makes.txt".

    Returns:
        list: A list of car makes extracted from the file.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Regex to find car makes within <li> tags
        makes = re.findall(r'>([^<]+)<\/li>', html_content)

        # Clean up the makes by removing extra spaces and "Top Makes"
        makes = [make.strip() for make in makes if make and not make.startswith(
            'Top Makes') and not make.startswith('Other')]

        # Format the car makes to lowercase with hyphens
        formatted_makes = []
        for make in makes:
            formatted_make = make.lower().replace(' ', '-')
            formatted_makes.append(formatted_make)

        return formatted_makes

    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


if __name__ == "__main__":
    car_makes = extract_car_makes()
    if car_makes:
        print("Extracted Car Makes...")
        with open("car_makes.txt", "w", encoding="utf-8") as f:
            for make in car_makes:
                f.write(make + "\n")
    else:
        print("No car makes were extracted.")
