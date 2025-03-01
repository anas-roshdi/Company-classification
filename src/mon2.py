import requests
from bs4 import BeautifulSoup
import time
import csv

# Define the base URL (without the pagination query)
base_url = "https://www.monshaat.gov.sa/ar/business-directory"

# Function to extract business guide links from a single page
def extract_links_from_page(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to retrieve the page {url}, status code: {response.status_code}")
            return [], None

        soup = BeautifulSoup(response.content, 'html.parser')
        business_links = []

        # Find all business guide links
        cards = soup.find_all('a', {'class': 'bussiness-guide-card-link'})
        for card in cards:
            link = card['href']  # Extract the href attribute
            full_link = f"https://www.monshaat.gov.sa{link}"  # Ensure the link is absolute
            business_links.append(full_link)

        # Find the next page URL from the pagination
        next_page_tag = soup.find('a', {'class': 'button btn btn-primary text-white', 'rel': 'next'})
        if next_page_tag:
            next_page_url = next_page_tag['href']  # Get the relative URL (e.g., '?page=2')
            return business_links, next_page_url
        return business_links, None
    except Exception as e:
        print(f"Error extracting links from {url}: {e}")
        return [], None

# Function to scrape the details of each business
def extract_business_details(business_url):
    try:
        response = requests.get(business_url)
        if response.status_code != 200:
            print(f"Failed to retrieve the business page {business_url}, status code: {response.status_code}")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract the business title
        title_tag = soup.find('h2', {'class': 'app-details-title'})
        title = title_tag.get_text(strip=True) if title_tag else 'No title found'

        # Extract the business details/content
        content_tag = soup.find('div', {'class': 'app-details-content mt-3'})
        content = content_tag.get_text(strip=True) if content_tag else 'No content found'
        # Extract the business item
        item_tag = soup.find('div', {'class': 'app-details-area-item area-item'})
        item = item_tag.get_text(strip=True) if item_tag else 'No item found'

        return title, content, item
    except Exception as e:
        print(f"Error extracting details from {business_url}: {e}")
        return None

# Function to scrape all pages
def scrape_all_pages(start_url):
    all_details = []
    current_url = start_url
    page_number = 1

    while current_url:
        print(f"Scraping page {page_number}: {current_url}")
        links, next_page_url = extract_links_from_page(current_url)
        print(f"Found {len(links)} business links on this page.")

        # For each business link, extract the details
        for link in links:
            print(f"Scraping details for {link}")
            details = extract_business_details(link)
            if details:
                all_details.append({'url': link, 'title': details[0], 'content': details[1], 'item': details[2]})

        # Update current_url with the next page
        if next_page_url:
            current_url = base_url + next_page_url  # Append the next page relative URL
            page_number += 1
        else:
            break  # Stop if no more pages

        # Pause between requests to avoid server overload
        time.sleep(1)

    return all_details

# Start scraping
business_details = scrape_all_pages(base_url)

# Save the details to a file
import csv

# Define the field names
field_names = ['Business Number', 'URL', 'Title', 'Content', 'Class']

# Save the details to a CSV file
with open("business_guide_details_all_pages2.csv", "w", newline='', encoding="utf-8-sig") as file:
    writer = csv.DictWriter(file, fieldnames=field_names)
    
    writer.writeheader()
    
    for i, details in enumerate(business_details, 1):
        writer.writerow({
            'Business Number': i,
            'URL': details['url'],
            'Title': details['title'],
            'Content': details['content'],
            'Class': details['item']
        })
        print(f"Business {i} saved.")
