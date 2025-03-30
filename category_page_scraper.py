from bs4 import BeautifulSoup

def extract_car_links(soup, base_url):
    """Extracts links to car details pages from a category page."""
    links = []
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if '/offers/' in href:  # Adjust this condition to match the car details URL pattern
            absolute_url = base_url + href if not href.startswith('http') else href
            links.append(absolute_url)
    return links

def extract_pages(soup, base_url):
    """Extracts pagination links from a category page."""
    pages = []
    prev_next = soup.find_all('li', {'class': 'prev-next'})
    return pages
