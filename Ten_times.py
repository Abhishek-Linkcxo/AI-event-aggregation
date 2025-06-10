from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import time
import pyperclip
import pandas as pd
import re
import google.generativeai as genai


genai.configure(api_key="AIzaSyBtO-JpfCUZ8Zz_uLrjY1SavDvSUICvbqY")  # Update with your API key

# Initialize the Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")  # Use latest available model

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.get('https://10times.com/')
driver.maximize_window()

Events_Link = []
event_data = []  # To store extracted event details

try:
    # Locate the India button
    india_button = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, "//div[normalize-space()='India']"))
    )

    # Scroll to the element
    driver.execute_script("arguments[0].scrollIntoView(true);", india_button)
    time.sleep(1)  # Let scrolling finish

    # Use JavaScript to click the element (bypasses obstruction)
    driver.execute_script("arguments[0].click();", india_button)
    print("Clicked on 'India' button using JavaScript.")

    # Wait for the event elements to load
    time.sleep(2)

    # Scroll down to ensure all events are loaded
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
    time.sleep(2)

    # Find all div elements with class "col-12 text-break show-related"
    event_divs = driver.find_elements(By.XPATH, "//*[@class='col-12 text-break show-related']")

    # Extract href from anchor tags inside each div and store in list
    for div in event_divs:
        anchor_tags = div.find_elements(By.TAG_NAME, 'a')  # Find all <a> tags
        for anchor in anchor_tags:
            href = anchor.get_attribute("href")
            if href and href not in Events_Link:  # Ensure it's not None and not a duplicate
                Events_Link.append(href)

    print("Collected Event Links:", Events_Link)

except TimeoutException:
    print("Timeout occurred while interacting with India Events button.")
except Exception as e:
    print(f"An error occurred: {e}")