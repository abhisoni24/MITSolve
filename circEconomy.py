"""
MIT Solve Circular Economy Challenge 2019 Solution Scraper (Static HTML)
- Uses requests + BeautifulSoup
- Loops through all solution listing pages
- Extracts title, short description, badge, and URL for each solution card
- Writes data to a CSV
"""
import requests
from bs4 import BeautifulSoup
import csv
import time

BASE_URL = "https://solve.mit.edu"
CHALLENGE_URL = BASE_URL + "/challenges/circular-economy?solutionsPage={page}"
OUTFILE = "mit_solve_circular_economy_2019_solutions.csv"

solutions = []
seen_links = set()

# Adjust this if you know the exact number of pages (e.g. 20 for 299 submissions @ 15/page)
MAX_PAGES = 20

for page in range(1, 2):
    url = CHALLENGE_URL.format(page=page)
    # print("url: ", url)
    print(f"Scraping page {page}: {url}")
    resp = requests.get(url)
    # with open("demo_response.txt", "w") as file:
    #     file.write(resp.text)
    if resp.status_code != 200:
        print(f"Failed to load page {page} (status: {resp.status_code})")
        break
    soup = BeautifulSoup(resp.text, 'html.parser')
    # Each solution card is an <a> with href starting /solutions/
    for a in soup.select('a[href^="/solutions/"]'):
        print(a.text)
        href = a['href']
        # Avoid duplicates (cards can appear on multiple paginated pages)
        if href in seen_links:
            continue
        seen_links.add(href)
        solution_url = href
        print("Project 1 Url", solution_url)
        # Title
        title_tag = a.select_one('.font-semibold')
        title = title_tag.get_text(strip=True) if title_tag else ''
        # Short Description
        desc_tag = a.find_next(class_='line-clamp-2')
        desc = desc_tag.get_text(strip=True) if desc_tag else ''
        # Badge/Status
        badge_tag = a.find('span', class_=lambda x: x and x.startswith('bg-solve-'))
        badge = badge_tag.get_text(strip=True) if badge_tag else ''
        solutions.append({
            'URL': solution_url,
            'Title': title,
            'Description': desc,
            'Badge': badge
        })
    # Polite delay between page requests
    time.sleep(1)

print(f"Collected {len(solutions)} solutions. Now writing to CSV...")

with open(OUTFILE, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['URL', 'Title', 'Description', 'Badge'])
    writer.writeheader()
    writer.writerows(solutions)

print(f"Done! Data written to {OUTFILE}")
