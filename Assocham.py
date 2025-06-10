from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time


def get_event_links():
    """Scrapes event links from ASSOCHAM and returns them as a list."""

    service = Service()
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    driver = webdriver.Chrome(service=service, options=chrome_options)
    Events_Link = []

    try:
        driver.get('https://www.assocham.org/')

        # Wait for "Forthcoming Events" button & click it
        Forthcoming_Events = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//label[@for='tab3']"))
        )
        Forthcoming_Events.click()

        # Click "View All" to load all events
        View_All = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "(//div[@class='viewall_tab'])[3]"))
        )
        View_All.click()

        # Find all event div elements
        event_divs = driver.find_elements(By.XPATH, '//div[@class="entire_event"]')

        # Extract href from <a> tags inside each div
        for div in event_divs:
            anchor_tags = div.find_elements(By.TAG_NAME, 'a')
            for anchor in anchor_tags:
                href = anchor.get_attribute("href")
                if href and href not in Events_Link:
                    Events_Link.append(href)

    except TimeoutException:
        print("Forthcoming Events button or View All not found.")

    finally:
        driver.quit()  # Ensure proper cleanup

    return Events_Link  # Return collected event links


def extract_event_data(event_links):
    """Extracts details for each event from the collected links."""
    
    # Setup WebDriver
    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    event_data = []  # Store extracted event details

    for link in event_links:
        try:
            driver.get(link)
            time.sleep(5)  # Allow page to load

            # Select all page content and copy to clipboard
            body = driver.find_element(By.TAG_NAME, 'body')
            body.send_keys(Keys.CONTROL + 'a')
            body.send_keys(Keys.CONTROL + 'c')
            time.sleep(2)  # Ensure clipboard is copied

            # Store event details
            event_info = {"Event Link": link}

            if event_info not in event_data:
                event_data.append(event_info)

        except Exception as e:
            print(f"Error extracting data from {link}: {e}")

    driver.quit()  # Clean up driver
    return event_data


# Uncomment for testing
# if __name__ == "__main__":
#     links = get_event_links()
#     print("Collected Event Links:", links)
#     print("Total Events:", len(links))
#     event_details = extract_event_data(links)
#     print("Extracted Event Data:", event_details)
