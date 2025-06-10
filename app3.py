import logging
import traceback
import concurrent.futures
# import Eventbrite #
import Eventbrite
import Nasscom #
import ConferenceAlerts
import Assocham
import pandas as pd
import re
import os
import time
import pyperclip




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

import asyncio
import re
from crawl4ai import *


# Configure logging
logging.basicConfig(
    filename="event_scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# # Load environment variables
# load_dotenv()

# # Initialize Gemini AI
# Gemini_api_key = os.getenv("GEMINI_API_KEY")
# if not Gemini_api_key:
#     raise ValueError("Gemini API key not found. Please set GEMINI_API_KEY in the .env file.")

# genai.configure(api_key=Gemini_api_key)
genai.configure(api_key="AIzaSyBtO-JpfCUZ8Zz_uLrjY1SavDvSUICvbqY")

# model = genai.GenerativeModel("gemini-1.5-flash")  


# Initialize Selenium WebDriver
# options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # Run in headless mode
# service = Service()
# driver = webdriver.Chrome(service=service)

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


# Function to extract event details using AI
def extract_event_details(page_content):
    input_prompt = (
        "You are an AI assistant tasked with extracting specific event details from event descriptions. "
        "From the provided text, identify and extract the following information: "
        "Event Name,Industry, Subindustry, Function, Date, Time, Location, Organizer, Event Themes, Awards, Nomination Deadline, Objectives, Contact Information "
        "(including Name, Phone, and Email for each contact). "
        "If the Industry is not explicitly mentioned, infer it from the event description or Event Name."
        "Ensure that the assigned industry matches or is the closest match to one of the following industries: "
        "[Professional Services, Not for profit / NGO, Media / Entertainment / Communication, Logistics / Transportation, "
        "IT & ITES, Industrial / Manufacturing, Healthcare / Pharma, FMCG / Retail, Energy / Oil & Gas, Education / Training, "
        "E-commerce, BFSI, Agriculture and allied services, Tourism & Hospitality, Confidential, Startup / VCs/ PEs, Real Estate / Construction, HR, FInance, marketing]."
        "If the Function is not explicitly mentioned, infer it from the event description or Event Name."
        "Ensure that the assigned Function matches or is the closest match to one of the following Functions: "
        "[Marketing, HR, IT, Operations, Finance, ESG, Legal, Business Development and Sales, Legal, Supply Chain Management,"
        "Quality Management, Leadership and Executive Management, Business Development and Sales, Strategy and Planning, Legal, Research and Development, Production]."
        "Each section should be clearly labeled. "
        "If any section is not present in the provided text, please leave the section blank or empty. "
        "Format your response as follows:\n\n"
        "Event Name: [Event Name]\n"
        "Industry: [Industry]\n"
        "Subindustry: [Subindustry]\n"
        "Function: [Function]\n"
        "Date: [Date]\n"
        "Time: [Time]"
        "Location: [Location]\n"
        "Organizer: [Organizer]\n"
        "Event Themes: [Event Themes] (List of themes or topics)\n"
        "Awards: [Awards]\n"
        "Nomination Deadline: [Nomination Deadline]\n"
        "Objectives: [Objectives] (List of objectives)\n"
        "Contact Information:\n"
        "{Contact 1 Name: [Name]\n"
        "Phone: [Phone]\n"
        "Email: [Email]\n"
        "Contact 2 Name: [Name]\n"
        "Phone: [Phone]\n"
        "Email: [Email]}\n"
    )

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        full_prompt = f"{input_prompt}\n\n{page_content}"
        response = model.generate_content(full_prompt, generation_config=genai.GenerationConfig(
            temperature=0.3))

        if response and hasattr(response, 'text'):
            return response.text.strip()
        else:
            return "No valid response"
    except Exception as e:
        print(f"An error occurred during AI content generation: {e}")
        return "Error generating content"


    

def parse_event_details(response_text):
    # Define the regex patterns to match each section more carefully
    patterns = {
        'Event Name': r"Event Name:\s*(.*?)(?=\n|Industry:|Subindustry:|Function:|Date:|Time:|Location:|Organizer:|Event Themes:|Awards:|Nomination Deadline:|Objectives:|Contact Information:)",
        'Industry': r"Industry:\s*(.*?)(?=\n|Subindustry:|Function:|Date:|Time:|Location:|Organizer:|Event Themes:|Awards:|Nomination Deadline:|Objectives:|Contact Information:)",
        'Subindustry': r"Subindustry:\s*(.*?)(?=\n|Function:|Date:|Time:|Location:|Organizer:|Event Themes:|Awards:|Nomination Deadline:|Objectives:|Contact Information:)",
        'Function': r"Function:\s*(.*?)(?=\n|Date:|Time:|Location:|Organizer:|Event Themes:|Awards:|Nomination Deadline:|Objectives:|Contact Information:)",
        'Date': r"Date:\s*(.*?)(?=\n|Time:|Location:|Organizer:|Event Themes:|Awards:|Nomination Deadline:|Objectives:|Contact Information:)",
        'Time': r"Time:\s*(.*?)(?=\n|Location:|Organizer:|Event Themes:|Awards:|Nomination Deadline:|Objectives:|Contact Information:)",
        'Location': r"Location:\s*(.*?)(?=\n|Organizer:|Event Themes:|Awards:|Nomination Deadline:|Objectives:|Contact Information:)",
        'Organizer': r"Organizer:\s*(.*?)(?=\n|Event Themes:|Awards:|Nomination Deadline:|Objectives:|Contact Information:)",
        'Event Themes': r"Event Themes:\s*(.*?)(?=\n|Awards:|Nomination Deadline:|Objectives:|Contact Information:)",
        'Awards': r"Awards:\s*(.*?)(?=\n|Nomination Deadline:|Objectives:|Contact Information:)",
        'Nomination Deadline': r"Nomination Deadline:\s*(.*?)(?=\n|Objectives:|Contact Information:)",
        'Objectives': r"Objectives:\s*(.*?)(?=\n|Contact Information:)",
        'Contact Information': r"Contact Information:\s*(.*)",
    }

    event_info = {}

    # Search for each pattern in the response_text and store the match in the dictionary
    for key, pattern in patterns.items():
        match = re.search(pattern, response_text, re.DOTALL)
        if match:
            event_info[key] = match.group(1).strip()  # Remove leading/trailing spaces

    return event_info

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

        for info in results:
            if info and info not in event_data:
                event_data.append(info)

    # Also save inside here if you want immediate result export
    df = pd.DataFrame(event_data)
    df.to_excel("Event_aggreg_data_Crawl4AI.xlsx", index=False)
    return event_data

# Async function to extract event info from a link
async def extract_event_info(crawler, link):
    try:
        # # PATCH: Add a dummy config if missing to avoid attribute error
        # if not hasattr(crawler.strategy, "config"):
        #     crawler.strategy.config = type("Config", (), {"verbose": False})()

        result = await crawler.arun(url=link)
        text = result.markdown
        text = strip_markdown_links(text)
        text = remove_image_tags(text)
        text = remove_boilerplate_lines(text)

        event_details = extract_event_details(text)
        event_info = parse_event_details(event_details)
        event_info['Event Link'] = link
        return event_info
    except Exception as e:
        logging.error(f"Error processing {link}: {e}")
        return None

if __name__ == "__main__":
    logging.info("Starting Event Scraper")

    modules = [Nasscom, Assocham, Eventbrite] #
    all_event_links = []

    # Run each module's scraper in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(modules)) as executor:
        for result in executor.map(run_scraper, modules):
            all_event_links.extend(result)

    print("Total Events Link : ",len(all_event_links)) ##

    logging.info(f"Total {len(all_event_links)} event links collected.")
    all_event_links = all_event_links[:15]  # Limit for testing or rate-limiting

    # Run async processing and save final event data
    event_data = asyncio.run(process_events(all_event_links))

    df = pd.DataFrame(event_data)
    df.to_excel("Event_aggregation_data_CrawlAI_test1.xlsx", index=False)

    logging.info("Event Scraper Completed Successfully")


