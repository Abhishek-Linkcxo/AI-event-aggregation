import json
import requests
import pandas as pd
import logging
from datetime import datetime, timedelta
from nocodb import get_industry_id, get_category_id, get_function_id

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Replace with your actual Excel file path
input_file_path = r"D:\AI_LinkCxO\Event Aggregation\New_Events_15_05.xlsx"

def safe_split(val, splitter=":", default=("00", "00")):
    try:
        parts = str(val).strip().split(splitter)
        return parts if len(parts) == 2 else default
    except Exception:
        return default

def safe_date(val):
    try:
        dt = pd.to_datetime(val)
        return {
            "year": dt.year,
            "month": dt.month,
            "day": dt.day
        }
    except Exception:
        return {
            "year": 2025,
            "month": 1,
            "day": 1
        }

def parse_time_str(time_val):
    try:
        if pd.isna(time_val):
            return {"hour": 0, "minute": 0}
        if hasattr(time_val, "hour") and hasattr(time_val, "minute"):
            return {"hour": time_val.hour, "minute": time_val.minute}
        dt = datetime.strptime(str(time_val).strip(), "%H:%M")
        return {"hour": dt.hour, "minute": dt.minute}
    except Exception:
        return {"hour": 0, "minute": 0}

# Load the Excel file
logging.info("Loading Excel file...")
df = pd.read_excel(input_file_path)

# Filter rows with Start Date beyond today
# today = datetime.today()
# seven_days_later = today + timedelta(days=0)
# logging.info(f"Filtering events starting after: {seven_days_later.date()}")

# df["Start Date"] = pd.to_datetime(df["Start Date"], errors="coerce")
# df = df[df["Start Date"] > seven_days_later]

logging.info(f"Total events after filtering: {len(df)}")

def push_event_to_linkcxo(row):
    raw_industry = str(row.get("Industry", "")).strip()
    raw_category = str(row.get("Category", "")).strip()
    raw_function = str(row.get("Function", "")).strip()

    logging.info(f"Mapping values → Industry: '{raw_industry}', Category: '{raw_category}', Function: '{raw_function}'")

    industry_id = get_industry_id(raw_industry)
    category_id = get_category_id(raw_category)
    function_id = get_function_id(raw_function)

    logging.info(f"Mapped IDs → Industry: {industry_id}, Category: {category_id}, Function: {function_id}")

    payload = {
        "title": row.get("Event Name", ""),
        "details": row.get("Event Description", ""),
        "industry": [str(industry_id)] if industry_id else [],
        "functions": [str(function_id)] if function_id else [],
        "category": [str(category_id)] if category_id else [],
        "host": "Partner",
        "isPrivate": str(row.get("isPrivate", "")).lower() == "true",
        "isOffline": str(row.get("isOffline", "")).lower() == "true",
        "eventUrl": str(row.get("EventURL")),
        "venue": row.get("Location", ""),
        "fee": row.get("fee",""),
        "startDate": safe_date(row.get("Start Date")),
        "endDate": safe_date(row.get("End Date")),
        "startTime": parse_time_str(row.get("Start Time")),
        "endTime": parse_time_str(row.get("End Time")),
        "emailId": row.get("Email", ""),
        "authorId": "7229672013497622528",
        "authorType": "USER",
        "bannerImageUrl": row.get("bannerImageUrl", "")
    }

    logging.debug("Final payload:")
    logging.debug(json.dumps(payload, indent=2))

    url = "https://api.prod.linkcxo.com/v1/events"
    headers = {
        "accept": "*/*",
        "authorization": "Bearer ixMEFhCLVPtgltPkd5ce2qO0UOifPWgUdZMuiJVVQaodPJDQfK0xwJcj4ijNT0QpDvjA5OrabfcvlWVYNLvFsdKvrH78q9IiPSOkYj5WUtFmfcucTfyBkxgAzLiKRe0D",
        "Content-Type": "application/json",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code in [200, 201]:
            logging.info(f"✅ Successfully pushed: {row['Event Name']}")
            return True
        else:
            logging.warning(f"❌ Failed to push: {row['Event Name']}")
            logging.warning(f"Status: {response.status_code} | Response: {response.text}")
            return False
    except Exception as e:
        logging.error(f"🚨 Error while pushing event: {row['Event Name']} | Error: {e}")
        return False

# Loop through all rows
success_count = 0

logging.info("Starting to push events to LinkCXO API...")

for i, row in df.iterrows():
    logging.info(f"Pushing event {i+1} of {len(df)}: {row.get('Event Name')}")
    if push_event_to_linkcxo(row):
        success_count += 1

logging.info(f"\n✅ Total events successfully pushed: {success_count} / {len(df)}")
