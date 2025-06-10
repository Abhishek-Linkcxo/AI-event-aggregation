import logging
import traceback
import concurrent.futures
import Eventbrite #
import Nasscom #
import Assocham #
import pandas as pd
import re
import os
import nocodb
import time
import requests
import json
import asyncio
import asyncio
from crawl4ai import *
import asyncio
from crawl4ai import AsyncWebCrawler
import signal
import sys



from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


import google.generativeai as genai
from dotenv import load_dotenv
from nocodb import get_industry_id, get_category_id , get_function_id
from nocodb import get_industry_list, get_category_list, get_function_list
from event_image import get_banner_logo_images


# Configure logging
logging.basicConfig(
    filename="event_scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Load environment variables
load_dotenv()

################################################
genai.configure(api_key="AIzaSyBtO-JpfCUZ8Zz_uLrjY1SavDvSUICvbqY")


def run_scraper(module):
    """Runs the scraper for a given module and logs errors if any."""
    try:
        logging.info(f"Starting scraper: {module.__name__}")
        event_links = module.get_event_links()
        logging.info(f"{len(event_links)} event links collected from {module.__name__}")
        return event_links
    except Exception as e:
        error_message = f"Error in {module.__name__}: {e}\n{traceback.format_exc()}"
        logging.error(error_message)
        return []  # Return empty list if an error occurs


# from nocodb import get_industry_id, get_category_id , get_function_id
# from nocodb import get_industry_list, get_category_list, get_function_list

# Function to extract event details using AI
def extract_event_details(event_detail_text, event_url):
    industries = get_industry_list()
    functions = get_function_list()
    categories = get_category_list()

    industries_str = ", ".join(industries)
    functions_str = ", ".join(functions)
    categories_str = ", ".join(categories)

    input_prompt = f"""
You are an AI assistant tasked with extracting specific event details from event descriptions.
From the provided text, identify and extract the following information:
Event Name, Event Description, Industry, Subindustry, Function, Date, Time, Location, Organizer,
Event Themes, Awards, Nomination Deadline, Objectives, and Contact Information
(including Name, Phone, and Email for each contact).

If the Industry is not explicitly mentioned, infer it from the event description or Event Name.
Ensure that the assigned industry matches or is the closest match to one of the following industries:
[{industries_str}]

If the Function is not explicitly mentioned, infer it from the event description or Event Name.
Pick one Function exactly from the following list (case-insensitive match only):
[{functions_str}]

If the Category is not explicitly mentioned, infer it from the event description or Event Name.
Ensure that the assigned Category matches or is the closest match to one of the following Categories:
[{categories_str}]

Each section should be clearly labeled.
If any section is not present in the provided text, please leave the section blank or empty.

For the isOffline field, determine whether the event is happening online or offline:
- If the event is offline (physical location required), set isOffline to true.
- If the event is online (virtual/remote event), set isOffline to false.

For the isPrivate field, determine whether the event is public or private:
- If the event is open to the public, set isPrivate to false.
- If the event is invitation-only or restricted, set isPrivate to true.

If the event date does not mention a year explicitly, use the current calendar year based on today's date (e.g., 2025).
Ensure that date values (Year, Month, and Day) are extracted as numbers.
Ensure that time values (Hour and Minute) are extracted as numbers.

Format your response as follows:

Event Name: [Event Name]
Event Description: [Event Description]
Industry: [Industry]
Subindustry: [Subindustry]
Function: [Function]
Category: [Category]
Organizer: [Organizer]
isPrivate: [true/false]
isOffline: [true/false]
Location: [Location]
fee:[fee]
Start Date: [YYYY-MM-DD]
End Date: [YYYY-MM-DD]
Start Time: [HH:MM]
End Time: [HH:MM]
Email: [Contact Email]
Event Themes: [Event Themes]
Awards: [Awards]
Nomination Deadline: [Nomination Deadline]
Objectives: [Objectives]
Contact Information:
- Name: [Contact 1 Name], Phone: [Contact 1 Phone], Email: [Contact 1 Email]
- Name: [Contact 2 Name], Phone: [Contact 2 Phone], Email: [Contact 2 Email]
EventURL: [{event_url}]
"""

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        # full_prompt = f"{input_prompt}\n\n{page_content}"
        full_prompt = f"{input_prompt}\n\n{event_detail_text}\n\nEventURL: [{event_url}]"
        response = model.generate_content(full_prompt, generation_config=genai.GenerationConfig(
            temperature=0.3))

        if response and hasattr(response, 'text'):
            return response.text.strip()
        else:
            return "No valid response"

    except Exception as e:
        print(f"An error occurred during AI content generation: {e}")
        return "Error generating content"



def parse_event_details(event_detail_text):
    patterns = {
        'Event Name': r"Event Name:\s*(.*?)(?=\nEvent Description:)",
        'Event Description': r"Event Description:\s*(.*?)(?=\nIndustry:)",
        'Industry': r"Industry:\s*(.*?)(?=\nSubindustry:)",
        'Subindustry': r"Subindustry:\s*(.*?)(?=\nFunction:)",
        # 'Function': r"Function:\s*(.*?)(?=\nCategory:)",
        'Function': r"Function:\s*(.*?)(?:\nCategory:|\nOrganizer:|\nisPrivate:)",
        'Category': r"Category:\s*(.*?)(?=\nOrganizer:)",
        'Organizer': r"Organizer:\s*(.*?)(?=\nisPrivate:)",
        'isPrivate': r"isPrivate:\s*(true|false)",
        'isOffline': r"isOffline:\s*(true|false)",
        'Location': r"Location:\s*(.*?)(?=\nfee:)",
        "fee": r"fee:\s*(.*?)(?=\nStart Date:)",
        'Start Date': r"Start Date:\s*(\d{4}-\d{2}-\d{2})",
        'End Date': r"End Date:\s*(\d{4}-\d{2}-\d{2})",
        'Start Time': r"Start Time:\s*(\d{2}:\d{2})",
        'End Time': r"End Time:\s*(\d{2}:\d{2})",
        'Email': r"Email:\s*(.*?)(?=\nEvent Themes:)",
        'Event Themes': r"Event Themes:\s*(.*?)(?=\nAwards:)",
        'Awards': r"Awards:\s*(.*?)(?=\nNomination Deadline:)",
        'Nomination Deadline': r"Nomination Deadline:\s*(.*?)(?=\nObjectives:)",
        'Objectives': r"Objectives:\s*(.*?)(?=\nContact Information:)",
        'Contact Information': r"Contact Information:\s*(.*?)(?=\nEventURL:)",
        # 'EventURL': r"EventURL:\s*((?:.|\n)*)"
        'EventURL': r"EventURL:\s*((?:.|\n)*?)(?=(\nEvent Name:|$))"
    }

    event_info = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, event_detail_text, re.DOTALL)
        event_info[key] = match.group(1).strip() if match else ""


    # Set default times if missing
    if not event_info['Start Time']:
        event_info['Start Time'] = '09:00'
    if not event_info['End Time']:
        event_info['End Time'] = '17:00'

    return event_info
    
def Event_validation(event_info):
    prompt = f"""
You're an AI event validator. Given an Event Name and Event Description, decide whether the event is professional and business-related.

Accept events that relate to business, industry, technology, leadership, innovation, finance, marketing, operations, HR, or professional development—even if not exclusively aimed at senior executives.

Be open to events that might be useful for professionals or organizations in any sector.

Reject events that are purely entertainment, hobby-based, local community gatherings, or personal interest with no clear professional or business relevance.

Respond only with "Yes" or "No".
Event Name: {event_info.get("Event Name", "")}
Event Description: {event_info.get("Event Description", "")}
"""

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt, generation_config=genai.GenerationConfig(temperature=0.2))

        if response and hasattr(response, 'text'):
            result = response.text.strip().lower()
            return result.startswith("yes")
        else:
            return False

    except Exception as e:
        logging.error(f"Error during event validation: {e}")
        return False


def strip_markdown_links(text):
    # Remove [text](link)
    return re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)

def remove_image_tags(text):
    # Remove markdown images ![alt](src) or !tag
    return re.sub(r'!\[.*?\]\(.*?\)|!\w+', '', text)

def remove_boilerplate_lines(text):
    # Filter out lines that are UI prompts, navigation, timestamps, etc.
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if (
            not line or
            line.startswith("×") or
            line.startswith("!") or
            re.match(r'\d{2}:\d{2} (AM|PM)', line) or
            re.match(r'^#\s?\|', line) or
            re.match(r'^---\|', line) or
            re.match(r'^#$', line) or
            re.match(r'^\|.*\|$', line) or
            'Pause' in line or 'Continue' in line or 'Hi! Welcome' in line
        ):
            continue
        cleaned_lines.append(line)
    return '\n'.join(cleaned_lines)


# Async function to crawl and extract data from event links
async def process_events(event_links):
    event_data = []
    async with AsyncWebCrawler() as crawler:
        tasks = [extract_event_info(crawler, link) for link in event_links]
        results = await asyncio.gather(*tasks)

        # for info in results:
        #     if info and info not in event_data:
        #         event_data.append(info)
        for info, html in results:
            if info and info not in event_data:
                event_data.append((info, html))


    return event_data




# Async function to extract event info from a link
async def extract_event_info(crawler, link):
    try:

        result = await crawler.arun(url=link)
        page_html = result.html  ##  # Get the raw HTML
        text = result.markdown
        text = strip_markdown_links(text)
        text = remove_image_tags(text)
        text = remove_boilerplate_lines(text)

        event_details = extract_event_details(text, link)
        event_info = parse_event_details(event_details)
        event_info['Event Link'] = link
        # return event_info
        return event_info, page_html

    except Exception as e:
        logging.error(f"Error processing {link}: {e}")
        return None



    
#################################################

# Create a wrapper function
async def fetch_banner(event_info, page_html):
    images = await get_banner_logo_images(page_html, event_info["EventURL"])
    return images[0] if images else ""



if __name__ == "__main__":
    logging.info("Starting Event Scraper")

    modules = [Eventbrite, Assocham, Nasscom]  # Define the event modules here
    all_event_links = []

    # Always fetch new event links
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(modules)) as executor:
        for result in executor.map(run_scraper, modules):
            all_event_links.extend(result)

    print(f"Total Event Links: {len(all_event_links)}")
    all_event_links = all_event_links[:12]  # Limit number of links if needed
    # all_event_links = all_event_links[18:50]


    event_data = []

    for link in all_event_links:
        try:
            # Run async processing and save final event data
            # event_detail_text = asyncio.run(process_events([link]))  # Just one event page

            # event_details = extract_event_details(event_detail_text[0], link)
            # event_info = parse_event_details(event_details)
            event_info_list = asyncio.run(process_events([link]))
            event_info, page_html = event_info_list[0]  # <-- You now have HTML

            print(f"Extracted Event Info: {event_info}")


            # Fetch banner/logo
            # banner_image_url = asyncio.run(fetch_banner(event_info))
            # event_info["bannerImageUrl"] = banner_image_url  #
            # print(f"bannerImageUrl:{banner_image_url}")

            banner_image_url = asyncio.run(fetch_banner(event_info, page_html))
            event_info["bannerImageUrl"] = banner_image_url  ##
            print(f"bannerImageUrl:{banner_image_url}")



            # Validate and save
            if event_info not in event_data:
                if Event_validation(event_info):
                    event_data.append(event_info)
                    print(f"1111111{event_data}") ##
                    df = pd.DataFrame(event_data)
                    df.to_excel("testcrawl4_10_06.xlsx", index=False)
                    # push_event_to_linkcxo(event_info)
                else:
                    logging.info(f"Event skipped (not C-Suite/C1 relevant): {event_info.get('Event Name')}")

        except Exception as e:
            logging.error(f"Error processing {link}: {e}")


    print(f"Total events scraped: {len(event_data)} | Saved to Excel: {len(event_data)}")
    print("Event Scraper Completed Successfully")

