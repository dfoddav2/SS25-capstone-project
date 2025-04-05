from bs4 import BeautifulSoup


def extract_car_links(soup, base_url):
    """Extracts links to car details pages from a category page,
    considering only articles with data-source="listpage_search-results"."""
    links = []
    # Find all article tags with the specified data-source attribute
    articles = soup.find_all(
        'article', {'data-source': 'listpage_search-results'})

    # Iterate through the articles and find the <a> tags within them
    for article in articles:
        a_tag = article.find('a')  # Find the first <a> tag in the article
        if a_tag and 'href' in a_tag.attrs:
            href = a_tag['href']
            if '/offers/' in href:  # Adjust this condition to match the car details URL pattern
                absolute_url = base_url + \
                    href if not href.startswith('http') else href
                links.append(absolute_url)
    return links


def extract_pages(soup, base_url):
    """Extracts pagination links from a category page."""
    pages = []
    prev_next = soup.find_all('li', {'class': 'prev-next'})
    return pages
