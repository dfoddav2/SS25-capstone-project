import requests
from bs4 import BeautifulSoup

def scrape_h1(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        soup = BeautifulSoup(response.content, 'html.parser')
        h1 = soup.find('h1')
        if h1:
            return h1.text.strip()
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def scrape_relative_div(url, target_text):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        soup = BeautifulSoup(response.content, 'html.parser')

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

    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == '__main__':
    url = input("Enter the URL to scrape: ")
    target_text = input("Enter the target text to find: ")
    h1_content = scrape_h1(url)
    if h1_content:
        print("H1 content:", h1_content)
    else:
        print("No H1 content found or an error occurred.")
    div_content = scrape_relative_div(url, target_text)
    if div_content:
        print("Sibling div content:", div_content)
    else:
        print("No sibling div content found or an error occurred.")