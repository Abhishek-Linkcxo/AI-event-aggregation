
import asyncio
from crawl4ai import *
from bs4 import BeautifulSoup
import google.generativeai as genai
import os

# Set your Gemini API key
genai.configure(api_key="AIzaSyBtO-JpfCUZ8Zz_uLrjY1SavDvSUICvbqY")  # Replace with your actual key

genai.configure(api_key=os.getenv("GEMINI_API_KEY", "AIzaSyBtO-JpfCUZ8Zz_uLrjY1SavDvSUICvbqY"))

async def get_banner_logo_images(html: str, page_url: str) -> list:
    soup = BeautifulSoup(html, "html.parser")
    image_srcs = [img['src'] for img in soup.find_all('img', src=True)]

    # Convert relative paths to full URLs
    base_url = page_url.split("/")[0] + "//" + page_url.split("/")[2]
    full_image_urls = [
        src if src.startswith("http") else f"{base_url}/{src.lstrip('/')}"
        for src in image_srcs
    ]

    # Filter only image formats
    # valid_image_urls = [
    #     url for url in full_image_urls
    #     if any(url.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".webp", ".svg"])
    # ]
    valid_image_urls = [
        url for url in full_image_urls
        if (
            any(ext in url.lower() for ext in [".png", ".jpg", ".jpeg", ".webp", ".svg"]) or
            any(keyword in url.lower() for keyword in [
                "images", "banner", "original", "header", "hero", "event", "cdn", "img", "evbuc"
            ])
        )
    ]
    

    prompt = f"""
    You are an AI assistant classifying image URLs from an event webpage.

    Event Page URL: {page_url}

    Your goal:
    Select **one image URL** that best represents the **event banner** — typically a prominent image at the top of the page that visually reflects the event’s title or theme.

    Use the event URL to guide your choice — for example, if the URL includes keywords like "chemical", and an image filename also includes "chemical", that is likely the banner.

    If no banner is clearly available, then return the **event organizer's official logo** instead.

    DO NOT return:
    - Sponsor logos
    - Jury or speaker images
    - Decorative icons or illustrations
    - More than one image

    Here are the available image URLs:
    {chr(10).join(valid_image_urls)}

    Output only the single best image URL. No extra text.
    """

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip().splitlines()

async def fetch_banner(event_info: dict, page_html: str) -> str:
    page_url = event_info.get("EventURL", "")
    banner_logo_images = await get_banner_logo_images(page_html, page_url)
    return banner_logo_images[0] if banner_logo_images else ""

