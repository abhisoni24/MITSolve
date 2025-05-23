import os
import time
import json
import requests
from openai import OpenAI
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
import asyncio

load_dotenv()

# Configs
API_KEY = os.getenv('OPENAI_API_KEY')
MODEL = 'gpt-4o-mini'  # gpt-4o is accurate and cost-effective
CSV_FILE = 'mit_solve_circular_economy_2019_solutions.csv'
OUTPUT_FILE = 'mit_solve_2019_circular_economy_solutions.json'
ERROR_LOG = 'scrape_errors.log'
THROTTLE_SECS = 4  # 15 requests/minute = 4s between requests

client = OpenAI(api_key=API_KEY)

# Prompt for the API
PROMPT_TEMPLATE = """
You are a data extraction agent. Given the raw HTML content of a solution page from the MIT Solve Circular Economy Challenge 2019, extract all unique, relevant information about this solution and return it as a single JSON object. Each unique attribute of the project should be one key-value pair, with descriptive, human-readable keys. Capture team details, solution summary, technology, impact, goals, achievements, statistics, market opportunity, media, website, and any other structured information present on the page.

Only return valid JSON, no extra text or comments.

HTML Content:
---
{html}
---
"""

# Load input data
df = pd.read_csv(CSV_FILE)
if not all(col in df.columns for col in ['ID', 'Submission_Result', 'Title', 'Team_Leader', 'URL']):
    raise ValueError("CSV does not have expected columns.")

# Load existing output (resume mode)
if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        all_results = json.load(f)
else:
    all_results = {}

def log_error(msg):
    with open(ERROR_LOG, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

def get_html(url):
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.text

def extract_json_from_html(html):
    prompt = PROMPT_TEMPLATE.format(html=html)
    response = client.responses.create(
        model=MODEL,
        input = prompt        
    )
    content = response.output_text
    # Extract JSON (allow for whitespace)
    try:
        # Sometimes the API returns extra text, try to extract just the JSON
        start = content.find('{')
        end = content.rfind('}') + 1
        json_str = content[start:end]
        result = json.loads(json_str)
        return result
    except Exception as e:
        raise ValueError(f"Could not parse JSON: {e}\nAPI Response:\n{content}")

# Main loop
try:
    for _, row in tqdm(df.iterrows(), total=len(df)):
        solution_id = str(row['ID'])
        url = row['URL']
        if solution_id in all_results:
            continue  # Already done

        # Retry logic
        for attempt in range(2):
            try:
                html = get_html(url)
                sol_json = extract_json_from_html(html)
                # Optionally, you can add info from the CSV as well
                sol_json['id'] = solution_id
                sol_json['title'] = row['Title']
                sol_json['team_leader'] = row['Team_Leader']
                sol_json['submission_result'] = row['Submission_Result']
                all_results[solution_id] = sol_json

                # Save after every solution (incremental progress)
                with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                    json.dump(all_results, f, indent=2, ensure_ascii=False)
                break  # Success, break retry loop

            except Exception as e:
                err_msg = f"Error on {solution_id} ({url}), attempt {attempt+1}: {e}"
                log_error(err_msg)
                if attempt == 1:
                    print(f"FAILED: {solution_id} - see {ERROR_LOG}")
            time.sleep(THROTTLE_SECS)

except KeyboardInterrupt:
    print("\nInterrupted by user. Progress saved.")

print("Processing complete. All results saved to", OUTPUT_FILE)
