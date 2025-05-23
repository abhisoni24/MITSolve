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

for page in range(1, MAX_PAGES+1):
    url = CHALLENGE_URL.format(page=page)
    print(f"Scraping page {page}: {url}")
    resp = requests.get(url)
    if resp.status_code != 200:
        print(f"Failed to load page {page} (status: {resp.status_code})")
        break
    soup = BeautifulSoup(resp.text, 'lxml')
    
    # Find the solutions section by its ID
    solutions_section = soup.find('section', id="solutions")
    if not solutions_section:
        print(f"No solutions section found on page {page}")
        continue
    
    # Find all the solution cards
    solution_cards = solutions_section.find_all("div", class_ = "relative flex flex-col p-4 -mt-px transition-colors border group sm:pt-11 sm:pb-9 sm:px-8 border-primary hover:bg-primary")
    print(f"Found {len(solution_cards)} solution cards on page {page}")
    # print(solution_cards[0])
    
    for card in solution_cards:
        # Get the link to the submission page
        link = card.find('a')
        solution_url = link['href']

        #find the solution ID
        id = int(solution_url.replace("https://solve.mit.edu/solutions/",""))
        
        # Skip if we've already seen this link
        if solution_url in seen_links:
            continue
        seen_links.add(solution_url)
        
        # Get submission result (badge) - first span in the card
        badgeSpan = card.find('span') #this is in the first span tag
        badge = badgeSpan.text
        # Get title - first h3 in the card
        title_tag = card.find('h3')
        title = title_tag.text
        
        # Get author - third span in the card
        tempSpans = card.find_all('span', class_ = "block")
        leader = tempSpans[-1].text[3:]
        # Add to solutions list
        solutions.append({
            'ID':id,
            'URL': solution_url,
            'Title': title,
            'Team_Leader': leader,
            'Submission_Result': badge
        })
        print(f"Added: {title} by {leader} ({badge})")    # Polite delay between page requests
    # print(solutions)
    time.sleep(1)

print(f"Collected {len(solutions)} solutions. Now writing to CSV...")

with open(OUTFILE, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['ID','Submission_Result', 'Title', 'Team_Leader', 'URL'])
    writer.writeheader()
    writer.writerows(solutions)

print(f"Done! Data written to {OUTFILE}")
