# from selenium import webdriver # type: ignore
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import NoSuchElementException, TimeoutException # type: ignore
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.options import Options
# import time

# def get_event_links():
#     """Scrapes event links from Eventbrite and returns them as a list."""
    
#     service = Service()
#     chrome_options = Options()
#     #chrome_options.add_argument("--headless")  # Run in headless mode
#     driver = webdriver.Chrome(service=service, options=chrome_options)    
    

#     Events_Link = []

#     try:
#         # Open the Eventbrite URL
#         driver.get('https://www.eventbrite.com/d/india/events/')
#         driver.maximize_window()

#         # Click "Explore more events"
#         try:
#             explore_more = WebDriverWait(driver, 2).until(
#                 EC.element_to_be_clickable((By.XPATH, "(//span[contains(text(),'Explore more events')])[1]"))
#             )
#             explore_more.click()
#         except TimeoutException:
#             print("Explore More Events button not found or already clicked.")

#         # Click "Business" filter
#         try:
#             business_filter = WebDriverWait(driver, 2).until(
#                 EC.element_to_be_clickable((By.XPATH, "(//span[normalize-space()='Business'])[1]"))
#             )
#             business_filter.click()
#         except TimeoutException:
#             print("Business filter not found or already applied.")

#         # Scrape event links from all available pages
#         while True:
#             try:
#                 # Wait for event cards to load
#                 event_rows = WebDriverWait(driver, 10).until(
#                     EC.presence_of_all_elements_located(
#                         (By.XPATH, "//div[@class='SearchResultPanelContentEventCard-module__card___Xno0V']")
#                     )
#                 )

#                 # Extract links
#                 for row in event_rows:
#                     anchor_tags = row.find_elements(By.TAG_NAME, 'a')
#                     for anchor in anchor_tags:
#                         href = anchor.get_attribute("href")
#                         if href and href not in Events_Link:
#                             Events_Link.append(href)

#                 # Click the "Next" button if available
#                 next_button = driver.find_element(By.XPATH, "//button[@aria-label='Next Page']//i[@class='Icon_root__1kdkz Icon_icon-small__1kdkz']//*[name()='svg']")
#                 if "disabled" in next_button.get_attribute("class"):
#                     break  # Stop if next button is disabled
#                 else:
#                     next_button.click()
#                     time.sleep(5)  # Allow time for the next page to load

#             except (NoSuchElementException, TimeoutException):
#                 break  # Exit loop if no "Next" button is found

#     except Exception as e:
#         print("An error occurred:", e)

#     finally:
#         driver.quit()  # Ensure browser closes properly

#     return Events_Link  # Return collected event links

# # Uncomment for testing
# if __name__ == "__main__":
#     links = get_event_links()
#     print("Collected Event Links:", links)
#     print("Total Events:", len(links))

from selenium import webdriver # type: ignore
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException # type: ignore
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time

def get_event_links():
    """Scrapes event links from Eventbrite and returns them as a list."""
    
    service = Service()
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    driver = webdriver.Chrome(service=service, options=chrome_options)    
    

    Events_Link = []

    try:
        # Open the Eventbrite URL
        driver.get('https://www.eventbrite.com/d/india/events/')
        driver.maximize_window()

        # Click "Explore more events"
        try:
            explore_more = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, "(//span[contains(text(),'Explore more events')])[1]"))
            )
            explore_more.click()
        except TimeoutException:
            print("Explore More Events button not found or already clicked.")

        # Click "Business" filter
        try:
            business_filter = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, "(//span[normalize-space()='Business'])[1]"))
            )
            business_filter.click()
        except TimeoutException:
            print("Business filter not found or already applied.")

        # Scrape event links from all available pages
        while True:
            try:
                # Wait for event cards to load
                event_rows = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, "//div[@class='SearchResultPanelContentEventCard-module__card___Xno0V']")
                    )
                )

                # Extract links
                for row in event_rows:
                    anchor_tags = row.find_elements(By.TAG_NAME, 'a')
                    for anchor in anchor_tags:
                        href = anchor.get_attribute("href")
                        if href and href not in Events_Link:
                            Events_Link.append(href)

                # Scroll into view for next button and click
                try:
                    next_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "(//button[@aria-label='Next Page'])[1]"))
                    )
                    driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                    driver.execute_script("arguments[0].click();", next_button)
                    time.sleep(5)
                except TimeoutException:
                    print("Next button not found or not clickable.")
                    break  # Exit loop if no "Next" button is found

            except (NoSuchElementException, TimeoutException):
                break  # Exit loop if no "Next" button is found

    except Exception as e:
        print("An error occurred:", e)

    finally:
        driver.quit()  # Ensure browser closes properly

    return Events_Link  # Return collected event links

# # Uncomment for testing
# if __name__ == "__main__":
#     links = get_event_links()
#     print("Collected Event Links:", links)
#     print("Total Events:", len(links))
