# nocodb.py
import requests
import logging

BASE_URL = "https://api.prod.linkcxo.com/v1/configuration/api/v1/db/data/v1/linkcxo"
HEADERS = {
    "Authorization": "Bearer DHBMRWcAgKvOGQw531KFFF93raNueBkajh4vpQyvdWFd3UeE7HroIlig9sWpzTkZzzWvTxDhB0Wu3lFpy0m9MUbE5pmsn8RKZf2rgUe49GcWKxoyBbWBsSLVZpqflISx",
    "Content-Type": "application/json"
}

def get_id_from_nocodb(table: str, key_field: str, key_value: str) -> str:
    # key_value_clean = key_value.strip().lower()
    key_value_clean = key_value.strip().lower().replace(" ", "")
    url = f"{BASE_URL}/{table}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        items = response.json().get('list', [])

        # mapping = {
        #     str(item.get(key_field, '')).strip().lower(): str(item.get("Id"))
        #     for item in items if item.get("Id") is not None
        # }
    
        mapping = {
            str(item.get(key_field, '')).strip().lower().replace(" ", ""): str(item.get("Id"))
            for item in items if item.get("Id") is not None
        }


        logging.info(f"Available {table} entries: {[item.get(key_field) for item in items]}")

        if key_value_clean in mapping:
            logging.info(f"✅ Exact match found: {key_value} → {mapping[key_value_clean]}")
            return mapping[key_value_clean]

        logging.warning(f"⚠️ No exact match for '{key_value}' in {table}")
        return None

    except requests.RequestException as e:
        logging.error(f"❌ Error fetching {table}: {e}")
        return None

def get_industry_id(name): return get_id_from_nocodb("industries", "Name", name)
def get_category_id(name): return get_id_from_nocodb("categories", "Categories", name)
def get_function_id(name): return get_id_from_nocodb("functions-New", "Title", name)



def get_list_from_nocodb(table: str, key_field: str) -> list:
    url = f"{BASE_URL}/{table}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        items = response.json().get("list", [])
        values = [str(item.get(key_field, "")).strip() for item in items if item.get(key_field)]
        return sorted(set(values))  # remove duplicates + sort
    except requests.RequestException as e:
        logging.error(f"❌ Error fetching list from {table}: {e}")
        return []

def get_industry_list(): return get_list_from_nocodb("industries", "Name")
def get_category_list(): return get_list_from_nocodb("categories", "Categories")
def get_function_list(): return get_list_from_nocodb("functions-New", "Title")











