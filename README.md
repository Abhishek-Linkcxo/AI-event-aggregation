# AI-event-aggregation
This project automates the end-to-end process of scraping event data from major platforms, enriching it with AI, and pushing it to LinkCXO's production API.

📁 Project Structure
main.py – The orchestrator script that calls all modules and manages the end-to-end flow.

Platform-specific scrapers:

eventbrite.py

assocham.py

nasscom.py
These use Selenium in headless mode to collect event links from respective platforms.

event_image.py – Fetches a suitable banner/logo image using AI (crawl4ai) from each event link.

crawl4ai – Utility used within main.py to scrape the full content of event pages.

requirements.txt – All Python package dependencies.

🔄 Workflow
Scrape event links from platforms like Eventbrite, Assocham, and Nasscom using headless Selenium.

Scrape full event page content using crawl4ai (HTML parser).

Use Gemini 1.5 Flash LLM via custom prompting to:

Extract structured information (e.g. event name, date, location, fee, etc.)

Format it as key-value pairs.

Output is parsed using regular expressions (re) within main.py.

Classify and extract banner/logo image using Gemini (event_image.py).

All data is saved to an Excel sheet.

The Excel file is used to push cleaned and enriched data to the LinkCXO production MongoDB API.

#AI-Powered Structuring
The raw content from event pages is passed into Gemini 1.5 Flash, a fast LLM optimized for long inputs and structured output.

Output from Gemini is parsed using regex (re) to extract fields like title, start date, time, venue, etc.

This allows for accurate field mapping and transformation, even across inconsistently formatted web pages.
