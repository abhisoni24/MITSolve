from openai import OpenAI
import requests
import asyncio
import time

def getHTML(url):
    print('marker 1')
    start_time = time.time()
    resp = requests.get(url)
    end_time = time.time()

    print(f'The elapsed time is {end_time-start_time} ms.')
    print('marker 2')
    
getHTML('https://solve.mit.edu/solutions/9147')