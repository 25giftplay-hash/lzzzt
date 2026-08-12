import json
import os
import requests

CONFIG_FILE = "config.json"

def test_lzt_connection():
    print("==================================================")
    print("Testing Lolzteam Market API Connection & Filters...")
    print("==================================================")
    
    if not os.path.exists(CONFIG_FILE):
        print(f"Error: {CONFIG_FILE} not found.")
        return
        
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)
        
    lzt_token = config.get("lzt_api_token")
    if not lzt_token or "YOUR_" in lzt_token:
        print("[!] Please enter your LZT API Token in config.json first.")
        return

    filters = config.get("filters", {})
    pmin = filters.get("pmin", 2)
    pmax = filters.get("pmax", 50)
    currency = filters.get("currency", "rub")
    target_countries = filters.get("countries", [])
    daybreak = filters.get("daybreak", 1)
    
    headers = {
        "Authorization": f"Bearer {lzt_token}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    api_params = {
        "pmin": pmin,
        "pmax": pmax,
        "currency": currency,
        "2fa": filters.get("2fa", "no"),
        "nsb": 1 if filters.get("nsb", True) else 0,
        "nsb_by_me": 1 if filters.get("nsb_by_me", True) else 0,
        "allow_geo_spamblock": 1 if filters.get("allow_geo_spamblock", False) else 0,
        "spam": "nomatter",
        "order_by": "pdate_to_down"
    }
    if daybreak:
        api_params["daybreak"] = daybreak
    if target_countries:
        api_params["country[]"] = target_countries
        
    url = "https://api.lzt.market/telegram"
    
    print(f"[*] Sending test request to LZT API...")
    print(f"[*] Testing filters: Price max {pmax} {currency.upper()}, Daybreak: {daybreak}, Countries: {len(target_countries)}")
    
    try:
        r = requests.get(url, headers=headers, params=api_params, timeout=15)
        print(f"[*] HTTP Response Status: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            items = data.get("items") or data.get("accounts") or data.get("listings") or []
            total = data.get("total_items", len(items))
            print(f"[SUCCESS] API Token is VALID!")
            print(f"[RESULT] Total accounts matching your exact filters right now: {len(items)} (Total on market: {total})")
            if items:
                print("\nSample matching item:")
                first = items[0]
                print(f"  - Item ID: {first.get('item_id')}")
                print(f"  - Title: {first.get('title')}")
                print(f"  - Price: {first.get('price')} RUB")
                print(f"  - Country: {first.get('telegram_country')}")
            else:
                print("\n[NOTE] No accounts currently match your exact filters. This is why you haven't received alerts yet.")
                print("      Try temporarily increasing 'pmax' to 500 in config.json to see matching accounts!")
        elif r.status_code == 401:
            print("[FAILED] HTTP 401 Unauthorized - Your LZT API token is invalid or expired.")
        else:
            print(f"[FAILED] HTTP {r.status_code}: {r.text}")
            
    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")

if __name__ == "__main__":
    test_lzt_connection()
