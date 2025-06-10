from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time

def get_event_links():
    """Scrapes event links from Nasscom and returns them as a list."""
    service = Service()
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    driver = webdriver.Chrome(service=service, options=chrome_options)
    Events_Link = []

    try:  
        # Open the Nasscom Events page
        driver.get('https://nasscom.in/events?type=upcoming')
        driver.maximize_window()

        # Scrape event links from all available pages
        while True:
            try:
                # Wait for event cards to load
                event_rows = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, '//div[@class="perspectives_card"]'))
                )

                # Extract links from event cards
                for row in event_rows:
                    anchor_tags = row.find_elements(By.TAG_NAME, 'a')
                    for anchor in anchor_tags:
                        href = anchor.get_attribute("href")
                        if href and href not in Events_Link:
                            Events_Link.append(href)

                # Click the "Load More" button if available
                load_more = driver.find_element(By.XPATH, "(//a[normalize-space()='Load More'])[1]")
                if "disabled" in load_more.get_attribute("class"):
                    break  # Stop if the button is disabled
                else:
                    load_more.click()
                    time.sleep(2)  # Wait for new events to load

            except (NoSuchElementException, TimeoutException):
                break  # Exit loop if "Load More" is not found

    except Exception as e:
        print("An error occurred:", e)

    finally:
        driver.quit()  # Ensure browser closes properly

    return Events_Link  # Return collected event links





# Uncomment for testing
# if __name__ == "__main__":
#     links = get_event_links()
#     print("Collected Event Links:", links)
#     print("Total Events:", len(links))