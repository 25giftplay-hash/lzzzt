import os
import sys
import json
import time
import requests
from datetime import datetime

CONFIG_FILE = "config.json"
SENT_ALERTS_FILE = "sent_alerts.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"Error: {CONFIG_FILE} not found. Please create it.")
        sys.exit(1)
        
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)
        
    # Override tokens from environment variables if present (useful for cloud platforms like Railway)
    env_lzt = os.environ.get("LZT_API_TOKEN")
    env_tg = os.environ.get("TELEGRAM_BOT_TOKEN")
    env_chat = os.environ.get("TELEGRAM_CHAT_ID")
    
    if env_lzt:
        config["lzt_api_token"] = env_lzt
    if env_tg:
        config["telegram_bot_token"] = env_tg
    if env_chat:
        config["telegram_chat_id"] = env_chat
        
    return config



def load_sent_alerts():
    if os.path.exists(SENT_ALERTS_FILE):
        try:
            with open(SENT_ALERTS_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception as e:
            print(f"Warning: Failed to load sent alerts ({e}). Starting fresh.")
    return set()

def save_sent_alerts(sent_set):
    try:
        with open(SENT_ALERTS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(sent_set), f, indent=2)
    except Exception as e:
        print(f"Error saving sent alerts: {e}")

def parse_spamblock(spam_block_val, max_wait_hours):
    # Returns (is_accepted, description)
    if not spam_block_val:
        return True, "خالي من الحظر (No Spam Block)"
    
    current_time = time.time()
    
    # Numeric timestamp representation
    if isinstance(spam_block_val, (int, float)):
        if spam_block_val > 1000000000:
            remaining_hours = (spam_block_val - current_time) / 3600
            if remaining_hours <= 0:
                return True, "خالي من الحظر (انتهت مدة الحظر)"
            elif remaining_hours <= max_wait_hours:
                hours_str = f"{remaining_hours:.1f}"
                return True, f"محظور مؤقتاً (ينفك بعد {hours_str} ساعة)"
            else:
                hours_str = f"{remaining_hours:.1f}"
                return False, f"محظور مؤقتاً لمدة طويلة ({hours_str} ساعة)"
        else:
            # Probably boolean true (1) representing permanent/unspecified ban
            return False, "محظور (حظر دائم أو غير محدد)"
            
    # String representation
    if isinstance(spam_block_val, str):
        if spam_block_val.isdigit():
            val = int(spam_block_val)
            if val > 1000000000:
                remaining_hours = (val - current_time) / 3600
                if remaining_hours <= 0:
                    return True, "خالي من الحظر (انتهت مدة الحظر)"
                elif remaining_hours <= max_wait_hours:
                    hours_str = f"{remaining_hours:.1f}"
                    return True, f"محظور مؤقتاً (ينفك بعد {hours_str} ساعة)"
                else:
                    return False, f"محظور مؤقتاً لمدة طويلة ({remaining_hours:.1f} ساعة)"
            return False, "محظور (حظر دائم أو غير محدد)"
            
        # Common datetime formats
        for fmt in ('%d.%m.%Y %H:%M', '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
            try:
                dt = datetime.strptime(spam_block_val.strip(), fmt)
                dt_ts = dt.timestamp()
                remaining_hours = (dt_ts - current_time) / 3600
                if remaining_hours <= 0:
                    return True, "خالي من الحظر (انتهت مدة الحظر)"
                elif remaining_hours <= max_wait_hours:
                    hours_str = f"{remaining_hours:.1f}"
                    return True, f"محظور مؤقتاً (ينفك بعد {hours_str} ساعة)"
                else:
                    return False, f"محظور مؤقتاً لمدة طويلة ({hours_str} ساعة)"
            except Exception:
                continue
                
        # String flags check
        low = spam_block_val.lower().strip()
        if low in ('no', 'false', 'none', '0'):
            return True, "خالي من الحظر (No Spam Block)"
        if any(w in low for w in ['permanent', 'вечн', 'eternal', 'never', 'yes', 'true']):
            return False, "محظور (حظر دائم)"
            
        return False, f"محظور (حالة غير معروفة: {spam_block_val})"
        
    return False, "محظور (غير معروف)"

def send_telegram_alert(bot_token, chat_id, item, spam_status):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    item_id = item.get("item_id")
    price = item.get("price")
    title = item.get("title", "بدون عنوان")
    country = item.get("telegram_country", "غير معروف")
    is_premium = item.get("telegram_premium", 0)
    
    premium_str = "نعم (Premium)" if is_premium else "لا"
    
    text = (
        f"<b>🔔 حساب تليجرام جديد مطابق للفلاتر!</b>\n\n"
        f"<b>📝 العنوان:</b> {title}\n"
        f"<b>💵 السعر:</b> {price} ₽\n"
        f"<b>🌍 الدولة:</b> {country}\n"
        f"<b>🚫 حالة السبام:</b> {spam_status}\n"
        f"<b>✨ مميزات إضافية (Premium):</b> {premium_str}\n\n"
        f"🔗 <a href='https://lzt.market/{item_id}/'>اضغط هنا للشراء مباشرة من الموقع</a>"
    )
    
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code == 200:
            print(f"[Telegram] Alert sent for item {item_id}.")
            return True
        else:
            print(f"[Telegram] Failed to send alert: {r.status_code} - {r.text}")
            return False
    except Exception as e:
        print(f"[Telegram] Error sending message: {e}")
        return False

def monitor_lzt():
    config = load_config()
    
    lzt_token = config.get("lzt_api_token")
    tg_token = config.get("telegram_bot_token")
    tg_chat_id = config.get("telegram_chat_id")
    interval = config.get("check_interval_seconds", 10)
    
    filters = config.get("filters", {})
    pmin = filters.get("pmin", 50)
    pmax = filters.get("pmax", 1000)
    currency = filters.get("currency", "rub")
    target_countries = filters.get("countries", [])
    max_spam_hours = filters.get("spam_block_max_wait_hours", 72)
    
    # Normalize countries for case-insensitive local checks
    target_countries_norm = [c.lower().strip() for c in target_countries]
    
    headers = {
        "Authorization": f"Bearer {lzt_token}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # We will call the API using parameters
    # Note that we do not filter spam=no in API because we want to receive temporary spam blocks
    # We filter spam block locally in the code.
    api_params = {
        "pmin": pmin,
        "pmax": pmax,
        "currency": currency,
        "2fa": filters.get("2fa", "no"),
        "nsb": 1 if filters.get("nsb", True) else 0,
        "nsb_by_me": 1 if filters.get("nsb_by_me", True) else 0,
        "allow_geo_spamblock": 1 if filters.get("allow_geo_spamblock", False) else 0,
        "spam": "nomatter",
        "order_by": "pdate_to_down" # Get newest first
    }
    
    # Session age / validity duration filter (e.g. at least X days)
    if "birthday" in filters:
        api_params["birthday"] = filters.get("birthday")
    if "birthday_period" in filters:
        api_params["birthday_period"] = filters.get("birthday_period")
    if "daybreak" in filters:
        api_params["daybreak"] = filters.get("daybreak")
        
    # If the user specified countries in the config, let's also pass them to the API
    # directly as 'country[]' array parameters
    if target_countries:
        api_params["country[]"] = target_countries
        
    sent_alerts = load_sent_alerts()
    is_first_run = True # Flag to avoid spamming existing items on start/restart
    
    print("--------------------------------------------------")
    print(f"Starting Lolzteam Telegram Monitor...")
    print(f"Query URL: https://api.lzt.market/telegram")
    print(f"Checking every {interval} seconds...")
    print(f"Filters: Price {pmin}-{pmax} {currency.upper()}, 2FA: {filters.get('2fa')}, Countries: {len(target_countries)}")
    print("--------------------------------------------------")
    
    session = requests.Session()
    session.headers.update(headers)
    
    consecutive_errors = 0
    
    while True:
        try:
            # Query the Lolzteam API
            url = "https://api.lzt.market/telegram"
            # Some versions of API use prod-api.lzt.market
            # We'll use api.lzt.market first, but fallback if needed
            response = session.get(url, params=api_params, timeout=15)
            
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 30))
                print(f"[Warning] Rate limited (HTTP 429). Sleeping for {retry_after} seconds...")
                time.sleep(retry_after)
                continue
                
            if response.status_code != 200:
                print(f"[Error] LZT API returned code {response.status_code}: {response.text}")
                consecutive_errors += 1
                # If api.lzt.market fails persistently, try prod-api.lzt.market
                if consecutive_errors >= 3:
                    print("[System] Attempting fallback endpoint prod-api.lzt.market...")
                    url = "https://prod-api.lzt.market/telegram"
                    response = session.get(url, params=api_params, timeout=15)
                    if response.status_code == 200:
                        consecutive_errors = 0
                    else:
                        print(f"[Fallback Error] Fallback also returned {response.status_code}")
                
                time.sleep(min(60, interval * 2))
                continue
            
            consecutive_errors = 0
            data = response.json()
            
            # The JSON normally has 'items' or 'accounts' or 'listings'
            items = data.get("items") or data.get("accounts") or data.get("listings")
            if items is None:
                # Let's inspect data keys if items isn't found
                print(f"[Warning] Could not find 'items' key in API response. Keys found: {list(data.keys())}")
                # Sometimes it's a direct list, or another key
                if isinstance(data, list):
                    items = data
                else:
                    time.sleep(interval)
                    continue
            
            # If this is the first run and sent_alerts is empty (e.g. on Railway restart),
            # populate it with current items so we don't alert old listings
            if is_first_run and not sent_alerts:
                print("[System] First run detected. Pre-populating existing listings to avoid duplicate startup alerts...")
                for item in items:
                    item_id = item.get("item_id")
                    if item_id:
                        sent_alerts.add(str(item_id))
                save_sent_alerts(sent_alerts)
                is_first_run = False
                print(f"[System] Pre-populated {len(items)} items. Now monitoring for new listings.")
                time.sleep(interval)
                continue
                
            is_first_run = False
            new_alerts = 0

            for item in items:
                item_id = item.get("item_id")
                if not item_id:
                    continue
                    
                # Skip already alerted
                if str(item_id) in sent_alerts or item_id in sent_alerts:
                    continue
                
                # Check country locally
                country = item.get("telegram_country", "")
                if target_countries_norm:
                    if not country or country.lower().strip() not in target_countries_norm:
                        continue
                
                # Check spamblock locally
                spam_val = item.get("telegram_spam_block")
                is_accepted_spam, spam_status = parse_spamblock(spam_val, max_spam_hours)
                
                if not is_accepted_spam:
                    # Not accepted, skip
                    continue
                
                # If we get here, it matches!
                print(f"[Match Found] Item {item_id} - Price: {item.get('price')} RUB - Country: {country} - Spam: {spam_status}")
                
                # Send Alert
                success = send_telegram_alert(tg_token, tg_chat_id, item, spam_status)
                if success:
                    sent_alerts.add(str(item_id))
                    new_alerts += 1
            
            if new_alerts > 0:
                save_sent_alerts(sent_alerts)
                
        except requests.exceptions.RequestException as e:
            print(f"[Connection Error] Connection failed: {e}")
            time.sleep(min(60, interval * 2))
        except Exception as e:
            print(f"[Critical Error] Unexpected error in loop: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(interval)
            
        time.sleep(interval)

if __name__ == "__main__":
    try:
        monitor_lzt()
    except KeyboardInterrupt:
        print("\nMonitor stopped by user.")
        sys.exit(0)
