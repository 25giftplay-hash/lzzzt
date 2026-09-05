import os
import sys
import re
import json
import time
import sqlite3
import threading
import requests
from datetime import datetime

CONFIG_FILE = "config.json"
SENT_ALERTS_FILE = "sent_alerts.json"
SELL_PRICES_FILE = "sell_prices.json"
DB_FILE = "stats.db"

# -------------------------------------------------------------------
# Embedded 195-Country Sell Price Database (Fallback)
# -------------------------------------------------------------------
DEFAULT_SELL_PRICES = {
  "UZ": { "best_usd": 0.4, "best_bot": "Bot 1" },
  "BD": { "best_usd": 0.18, "best_bot": "Bot 1" },
  "SA": { "best_usd": 0.7, "best_bot": "Bot 1" },
  "RU": { "best_usd": 1.2, "best_bot": "Bot 1" },
  "IT": { "best_usd": 0.85, "best_bot": "Bot 2" },
  "MX": { "best_usd": 0.4, "best_bot": "Bot 1" },
  "KZ": { "best_usd": 0.7, "best_bot": "Bot 1" },
  "UA": { "best_usd": 1.6, "best_bot": "Bot 2" },
  "YE": { "best_usd": 0.4, "best_bot": "Bot 2" },
  "LV": { "best_usd": 1, "best_bot": "Bot 1" },
  "PT": { "best_usd": 0.6, "best_bot": "Bot 1" },
  "KG": { "best_usd": 0.8, "best_bot": "Bot 1" },
  "TJ": { "best_usd": 0.25, "best_bot": "Bot 1" },
  "EG": { "best_usd": 0.35, "best_bot": "Bot 1" },
  "IQ": { "best_usd": 1.2, "best_bot": "Bot 1" },
  "TR": { "best_usd": 0.6, "best_bot": "Bot 1" },
  "CO": { "best_usd": 0.15, "best_bot": "Bot 1" },
  "ZW": { "best_usd": 0.2, "best_bot": "Bot 1" },
  "AR": { "best_usd": 0.45, "best_bot": "Bot 1" },
  "NL": { "best_usd": 0.85, "best_bot": "Bot 2" },
  "GB": { "best_usd": 0.3, "best_bot": "Bot 1" },
  "HK": { "best_usd": 0.25, "best_bot": "Bot 1" },
  "TH": { "best_usd": 0.3, "best_bot": "Bot 1" },
  "WS": { "best_usd": 0.6, "best_bot": "Bot 1" },
  "ES": { "best_usd": 1, "best_bot": "Bot 1" },
  "TN": { "best_usd": 0.5, "best_bot": "Bot 2" },
  "SN": { "best_usd": 0.5, "best_bot": "Bot 2" },
  "MA": { "best_usd": 0.25, "best_bot": "Bot 1" },
  "IN": { "best_usd": 0.15, "best_bot": "Bot 1" },
  "LB": { "best_usd": 0.4, "best_bot": "Bot 1" },
  "MZ": { "best_usd": 0.5, "best_bot": "Bot 2" },
  "VN": { "best_usd": 0.35, "best_bot": "Bot 1" },
  "GH": { "best_usd": 0.35, "best_bot": "Bot 2" },
  "IR": { "best_usd": 0.25, "best_bot": "Bot 1" },
  "AE": { "best_usd": 1.65, "best_bot": "Bot 2" },
  "ML": { "best_usd": 0.35, "best_bot": "Bot 2" },
  "PG": { "best_usd": 0.4, "best_bot": "Bot 1" },
  "NE": { "best_usd": 0.35, "best_bot": "Bot 2" },
  "PK": { "best_usd": 0.25, "best_bot": "Bot 1" },
  "PE": { "best_usd": 0.3, "best_bot": "Bot 1" },
  "AF": { "best_usd": 0.3, "best_bot": "Bot 1" },
  "TZ": { "best_usd": 0.25, "best_bot": "Bot 1" },
  "GT": { "best_usd": 0.45, "best_bot": "Bot 2" },
  "LK": { "best_usd": 0.55, "best_bot": "Bot 2" },
  "JO": { "best_usd": 0.5, "best_bot": "Bot 1" },
  "SY": { "best_usd": 0.2, "best_bot": "Bot 1" },
  "PS": { "best_usd": 0.6, "best_bot": "Bot 1" },
  "ID": { "best_usd": 0.15, "best_bot": "Bot 1" },
  "KH": { "best_usd": 0.4, "best_bot": "Bot 1" },
  "SD": { "best_usd": 0.45, "best_bot": "Bot 2" },
  "PR": { "best_usd": 0.45, "best_bot": "Bot 1" },
  "SZ": { "best_usd": 0.4, "best_bot": "Bot 1" },
  "TL": { "best_usd": 0.5, "best_bot": "Bot 1" },
  "TW": { "best_usd": 1.4, "best_bot": "Bot 2" },
  "KR": { "best_usd": 2.1, "best_bot": "Bot 2" },
  "SE": { "best_usd": 0.75, "best_bot": "Bot 1" },
  "EE": { "best_usd": 0.5, "best_bot": "Bot 1" },
  "FI": { "best_usd": 0.75, "best_bot": "Bot 2" },
  "LA": { "best_usd": 0.7, "best_bot": "Bot 2" },
  "NG": { "best_usd": 0.2, "best_bot": "Bot 2" },
  "IL": { "best_usd": 0.3, "best_bot": "Bot 1" },
  "CN": { "best_usd": 0.3, "best_bot": "Bot 1" },
  "MY": { "best_usd": 0.4, "best_bot": "Bot 2" },
  "IE": { "best_usd": 0.5, "best_bot": "Bot 1" },
  "AT": { "best_usd": 0.8, "best_bot": "Bot 2" },
  "RS": { "best_usd": 0.9, "best_bot": "Bot 2" },
  "RO": { "best_usd": 0.3, "best_bot": "Bot 1" },
  "SI": { "best_usd": 1.3, "best_bot": "Bot 2" },
  "ET": { "best_usd": 0.25, "best_bot": "Bot 1" },
  "NI": { "best_usd": 0.45, "best_bot": "Bot 2" },
  "PY": { "best_usd": 0.7, "best_bot": "Bot 1" },
  "HU": { "best_usd": 0.65, "best_bot": "Bot 2" },
  "NP": { "best_usd": 0.4, "best_bot": "Bot 1" },
  "UG": { "best_usd": 0.4, "best_bot": "Bot 1" },
  "MN": { "best_usd": 0.8, "best_bot": "Bot 1" },
  "BY": { "best_usd": 1.6, "best_bot": "Bot 2" },
  "CA": { "best_usd": 0.22, "best_bot": "Bot 1" },
  "ZM": { "best_usd": 0.4, "best_bot": "Bot 2" },
  "SO": { "best_usd": 0.3, "best_bot": "Bot 1" },
  "HR": { "best_usd": 1, "best_bot": "Bot 2" },
  "PL": { "best_usd": 0.45, "best_bot": "Bot 1" },
  "KE": { "best_usd": 0.25, "best_bot": "Bot 2" },
  "SV": { "best_usd": 0.6, "best_bot": "Bot 2" },
  "MM": { "best_usd": 0.25, "best_bot": "Bot 1" },
  "LY": { "best_usd": 0.45, "best_bot": "Bot 1" },
  "BO": { "best_usd": 1.15, "best_bot": "Bot 2" },
  "FJ": { "best_usd": 0.6, "best_bot": "Bot 2" },
  "NU": { "best_usd": 3, "best_bot": "Bot 1" },
  "TO": { "best_usd": 0.5, "best_bot": "Bot 1" },
  "CR": { "best_usd": 0.5, "best_bot": "Bot 2" },
  "HN": { "best_usd": 0.3, "best_bot": "Bot 1" },
  "JP": { "best_usd": 0.7, "best_bot": "Bot 1" },
  "NO": { "best_usd": 1.1, "best_bot": "Bot 2" },
  "AU": { "best_usd": 1.4, "best_bot": "Bot 2" },
  "CH": { "best_usd": 1.8, "best_bot": "Bot 1" },
  "DK": { "best_usd": 1.3, "best_bot": "Bot 2" },
  "CL": { "best_usd": 0.15, "best_bot": "Bot 1" },
  "BJ": { "best_usd": 0.2, "best_bot": "Bot 1" },
  "BI": { "best_usd": 0.4, "best_bot": "Bot 1" },
  "CU": { "best_usd": 0.3, "best_bot": "Bot 1" },
  "PA": { "best_usd": 0.8, "best_bot": "Bot 2" },
  "QA": { "best_usd": 1.8, "best_bot": "Bot 1" },
  "OM": { "best_usd": 1, "best_bot": "Bot 1" },
  "KW": { "best_usd": 1, "best_bot": "Bot 1" },
  "TG": { "best_usd": 0.25, "best_bot": "Bot 1" },
  "AO": { "best_usd": 0.3, "best_bot": "Bot 1" },
  "TD": { "best_usd": 0.3, "best_bot": "Bot 1" },
  "DZ": { "best_usd": 0.4, "best_bot": "Bot 2" },
  "SG": { "best_usd": 1.5, "best_bot": "Bot 1" },
  "MT": { "best_usd": 1.15, "best_bot": "Bot 2" },
  "TM": { "best_usd": 0.55, "best_bot": "Bot 2" },
  "BM": { "best_usd": 0.4, "best_bot": "Bot 1" },
  "BH": { "best_usd": 1.5, "best_bot": "Bot 1" },
  "DE": { "best_usd": 1, "best_bot": "Bot 1" },
  "BR": { "best_usd": 0.3, "best_bot": "Bot 1" },
  "MV": { "best_usd": 0.6, "best_bot": "Bot 1" },
  "CZ": { "best_usd": 0.8, "best_bot": "Bot 1" },
  "MD": { "best_usd": 1, "best_bot": "Bot 1" },
  "BE": { "best_usd": 1.15, "best_bot": "Bot 2" },
  "NZ": { "best_usd": 1.2, "best_bot": "Bot 2" },
  "KI": { "best_usd": 0.85, "best_bot": "Bot 1" },
  "MO": { "best_usd": 1.1, "best_bot": "Bot 2" },
  "SB": { "best_usd": 0.5, "best_bot": "Bot 1" },
  "AW": { "best_usd": 1, "best_bot": "Bot 1" },
  "DJ": { "best_usd": 0.6, "best_bot": "Bot 1" },
  "AL": { "best_usd": 0.3, "best_bot": "Bot 1" },
  "MC": { "best_usd": 1, "best_bot": "Bot 1" },
  "KM": { "best_usd": 0.65, "best_bot": "Bot 2" },
  "IS": { "best_usd": 0.7, "best_bot": "Bot 1" },
  "BA": { "best_usd": 0.6, "best_bot": "Bot 1" },
  "DO": { "best_usd": 0.6, "best_bot": "Bot 1" },
  "EC": { "best_usd": 0.55, "best_bot": "Bot 2" },
  "TT": { "best_usd": 0.5, "best_bot": "Bot 1" },
  "JM": { "best_usd": 0.25, "best_bot": "Bot 1" },
  "HT": { "best_usd": 0.5, "best_bot": "Bot 2" },
  "AZ": { "best_usd": 1.15, "best_bot": "Bot 2" },
  "BG": { "best_usd": 0.85, "best_bot": "Bot 2" },
  "LU": { "best_usd": 0.85, "best_bot": "Bot 1" },
  "CV": { "best_usd": 0.6, "best_bot": "Bot 1" },
  "SC": { "best_usd": 0.5, "best_bot": "Bot 1" },
  "UY": { "best_usd": 0.6, "best_bot": "Bot 2" },
  "GD": { "best_usd": 0.6, "best_bot": "Bot 1" },
  "CI": { "best_usd": 0.7, "best_bot": "Bot 2" },
  "AI": { "best_usd": 0.8, "best_bot": "Bot 1" },
  "KY": { "best_usd": 0.8, "best_bot": "Bot 1" },
  "VC": { "best_usd": 0.35, "best_bot": "Bot 2" },
  "LC": { "best_usd": 0.5, "best_bot": "Bot 1" },
  "ST": { "best_usd": 0.5, "best_bot": "Bot 1" },
  "GP": { "best_usd": 0.4, "best_bot": "Bot 1" },
  "MU": { "best_usd": 0.3, "best_bot": "Bot 1" },
  "SR": { "best_usd": 0.7, "best_bot": "Bot 1" },
  "LS": { "best_usd": 0.3, "best_bot": "Bot 1" },
  "GY": { "best_usd": 0.5, "best_bot": "Bot 1" },
  "DM": { "best_usd": 0.3, "best_bot": "Bot 1" },
  "NA": { "best_usd": 0.4, "best_bot": "Bot 2" },
  "BB": { "best_usd": 0.4, "best_bot": "Bot 1" },
  "BZ": { "best_usd": 0.7, "best_bot": "Bot 1" },
  "GA": { "best_usd": 0.35, "best_bot": "Bot 2" },
  "ZA": { "best_usd": 0.3, "best_bot": "Bot 1" },
  "BT": { "best_usd": 1, "best_bot": "Bot 1" },
  "CG": { "best_usd": 0.5, "best_bot": "Bot 1" },
  "CF": { "best_usd": 0.25, "best_bot": "Bot 1" },
  "PW": { "best_usd": 1.2, "best_bot": "Bot 1" },
  "LT": { "best_usd": 1, "best_bot": "Bot 1" },
  "GR": { "best_usd": 0.7, "best_bot": "Bot 1" },
  "GL": { "best_usd": 0.5, "best_bot": "Bot 1" },
  "MR": { "best_usd": 0.4, "best_bot": "Bot 1" },
  "GU": { "best_usd": 0.4, "best_bot": "Bot 1" },
  "CK": { "best_usd": 3, "best_bot": "Bot 1" },
  "FK": { "best_usd": 8, "best_bot": "Bot 1" },
  "SS": { "best_usd": 0.2, "best_bot": "Bot 1" },
  "MG": { "best_usd": 0.05, "best_bot": "Bot 1" },
  "BS": { "best_usd": 0.6, "best_bot": "Bot 1" }
}

# Comprehensive Country Dictionary (English + Russian + Arabic)
MULTI_LANG_COUNTRY_MAP = {
    # Russian Names
    "украина": "UA", "оаэ": "AE", "россия": "RU", "германия": "DE", "швейцария": "CH",
    "катар": "QA", "южная корея": "KR", "корея": "KR", "казахстан": "KZ", "ирак": "IQ",
    "беларусь": "BY", "белоруссия": "BY", "сша": "US", "великобритания": "GB", "англия": "GB",
    "нидерланды": "NL", "польша": "PL", "франция": "FR", "индонезия": "ID", "индия": "IN",
    "вьетнам": "VN", "таиланд": "TH", "турция": "TR", "бразилия": "BR", "италия": "IT",
    "испания": "ES", "австрия": "AT", "дания": "DK", "словения": "SI", "хорватия": "HR",
    "сербия": "RS", "тайвань": "TW", "китай": "CN", "сингапур": "SG", "австралия": "AU",
    "узбекистан": "UZ", "азербайджан": "AZ", "кыргызстан": "KG", "киргизия": "KG",
    "таджикиستان": "TJ", "египет": "EG", "алжир": "DZ", "марокко": "MA", "тунис": "TN",
    "грузия": "GE", "армения": "AM", "молдова": "MD", "латвия": "LV", "литва": "LT",
    "эстония": "EE", "финляндия": "FI", "норвегия": "NO", "швеция": "SE", "греция": "GR",
    "чехия": "CZ", "бельгия": "BE", "португалия": "PT", "румыния": "RO", "болгария": "BG",
    "израиль": "IL", "иран": "IR", "саудовская аравия": "SA", "кувейт": "KW", "оман": "OM",
    "бахрейн": "BH", "иордания": "JO", "ливан": "LB", "пакистан": "PK", "бангладеш": "BD",
    "филиппины": "PH", "малайзия": "MY", "канада": "CA", "мексика": "MX", "аргентина": "AR",
    "колумбия": "CO", "чили": "CL", "перу": "PE", "эквадор": "EC", "венесуэла": "VE",
    "юар": "ZA", "нигерия": "NG", "кения": "KE", "гана": "GH", "япония": "JP",
    "новая зеландия": "NZ", "макао": "MO",

    # English Names
    "ukraine": "UA", "united arab emirates": "AE", "uae": "AE", "russia": "RU", "saudi arabia": "SA",
    "italy": "IT", "mexico": "MX", "kazakhstan": "KZ", "latvia": "LV", "portugal": "PT",
    "kyrgyzstan": "KG", "tajikistan": "TJ", "egypt": "EG", "iraq": "IQ", "turkey": "TR",
    "colombia": "CO", "argentina": "AR", "netherlands": "NL", "united kingdom": "GB",
    "great britain": "GB", "uk": "GB", "spain": "ES", "india": "IN", "vietnam": "VN",
    "germany": "DE", "france": "FR", "united states": "US", "usa": "US", "canada": "CA",
    "switzerland": "CH", "qatar": "QA", "bahrain": "BH", "kuwait": "KW", "oman": "OM",
    "south korea": "KR", "korea": "KR", "taiwan": "TW", "japan": "JP", "australia": "AU",
    "singapore": "SG", "indonesia": "ID", "thailand": "TH", "philippines": "PH", "brazil": "BR",
    "chile": "CL", "peru": "PE", "morocco": "MA", "algeria": "DZ", "tunisia": "TN",
    "lebanon": "LB", "jordan": "JO", "belarus": "BY", "denmark": "DK", "slovenia": "SI",
    "austria": "AT", "croatia": "HR", "macao": "MO", "macau": "MO", "china": "CN",
    "new zealand": "NZ", "south africa": "ZA", "nigeria": "NG", "pakistan": "PK", "bangladesh": "BD"
}

PHONE_PREFIX_TO_CODE = {
    "971": "AE", "380": "UA", "966": "SA", "974": "QA", "41": "CH", "82": "KR",
    "7": "RU", "65": "SG", "964": "IQ", "49": "DE", "33": "FR", "44": "GB",
    "31": "NL", "34": "ES", "39": "IT", "43": "AT", "45": "DK", "386": "SI",
    "385": "HR", "381": "RS", "886": "TW", "853": "MO", "375": "BY", "371": "LV",
    "370": "LT", "372": "EE", "358": "FI", "47": "NO", "46": "SE", "420": "CZ",
    "32": "BE", "351": "PT", "40": "RO", "359": "BG", "972": "IL", "98": "IR",
    "965": "KW", "968": "OM", "973": "BH", "962": "JO", "961": "LB", "92": "PK",
    "880": "BD", "63": "PH", "60": "MY", "84": "VN", "66": "TH", "62": "ID",
    "1": "US", "52": "MX", "54": "AR", "57": "CO", "56": "CL", "51": "PE",
    "20": "EG", "213": "DZ", "212": "MA", "216": "TN", "998": "UZ", "994": "AZ",
    "996": "KG", "992": "TJ", "81": "JP", "61": "AU", "64": "NZ", "27": "ZA"
}

def resolve_country_code(country_str, title_str=""):
    # 1. Check exact 2-letter ISO code
    if country_str:
        c = str(country_str).strip()
        if len(c) == 2 and c.isalpha():
            return c.upper()
        low = c.lower()
        if low in MULTI_LANG_COUNTRY_MAP:
            return MULTI_LANG_COUNTRY_MAP[low]
            
    # 2. Check phone prefixes in country_str or title_str
    full_text = f"{country_str} {title_str}"
    numbers = re.findall(r'\+?(\d{1,4})', full_text)
    for num in numbers:
        for prefix in sorted(PHONE_PREFIX_TO_CODE.keys(), key=lambda x: -len(x)):
            if num.startswith(prefix):
                return PHONE_PREFIX_TO_CODE[prefix]
                
    return ""

# -------------------------------------------------------------------
# Database Ledger Functions
# -------------------------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS ledger (
            item_id TEXT PRIMARY KEY,
            status TEXT,
            cost_usd REAL,
            profit_usd REAL,
            best_bot TEXT,
            country TEXT,
            timestamp REAL
        )
    ''')
    conn.commit()
    conn.close()

def log_bought_item(item_id, cost_usd, expected_profit_usd, best_bot, country):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO ledger (item_id, status, cost_usd, profit_usd, best_bot, country, timestamp)
        VALUES (?, 'bought', ?, ?, ?, ?, ?)
    ''', (str(item_id), cost_usd, expected_profit_usd, best_bot, country, time.time()))
    conn.commit()
    conn.close()

def mark_item_sold(item_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE ledger SET status = 'sold' WHERE item_id = ?", (str(item_id),))
    conn.commit()
    conn.close()

def mark_item_banned(item_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE ledger SET status = 'banned' WHERE item_id = ?", (str(item_id),))
    conn.commit()
    conn.close()

def get_stats_summary(min_profit_usd=0.30):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT status, cost_usd, profit_usd FROM ledger")
    rows = c.fetchall()
    conn.close()
    
    total_bought = len(rows)
    sold_count = 0
    banned_count = 0
    pending_count = 0
    total_profit_usd = 0.0
    total_loss_usd = 0.0
    
    for status, cost_usd, profit_usd in rows:
        if status == 'sold':
            sold_count += 1
            total_profit_usd += (profit_usd or 0.0)
        elif status == 'banned':
            banned_count += 1
            total_loss_usd += (cost_usd or 0.0)
        elif status == 'bought':
            pending_count += 1
            
    net_balance_usd = total_profit_usd - total_loss_usd
    
    recovery_accounts_needed = 0
    if total_loss_usd > 0 and min_profit_usd > 0:
        import math
        recovery_accounts_needed = math.ceil(total_loss_usd / min_profit_usd)
        
    return {
        "total_bought": total_bought,
        "sold_count": sold_count,
        "banned_count": banned_count,
        "pending_count": pending_count,
        "total_profit_usd": total_profit_usd,
        "total_loss_usd": total_loss_usd,
        "net_balance_usd": net_balance_usd,
        "recovery_needed": recovery_accounts_needed
    }

def reset_db_stats():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM ledger")
    conn.commit()
    conn.close()

# -------------------------------------------------------------------
# Configuration & Helpers
# -------------------------------------------------------------------
def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"Error: {CONFIG_FILE} not found. Please create it.")
        sys.exit(1)
        
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)
        
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
            print(f"Warning: Failed to load sent alerts ({e}).")
    return set()

def save_sent_alerts(sent_set):
    try:
        with open(SENT_ALERTS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(sent_set), f, indent=2)
    except Exception as e:
        print(f"Error saving sent alerts: {e}")

def load_sell_prices():
    if os.path.exists(SELL_PRICES_FILE):
        try:
            with open(SELL_PRICES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data and isinstance(data, dict):
                    return data
        except Exception:
            pass
    return DEFAULT_SELL_PRICES

def parse_spamblock(spam_block_val, max_wait_hours):
    if not spam_block_val:
        return True, "خالي من الحظر (No Spam Block)"
    
    current_time = time.time()
    if isinstance(spam_block_val, (int, float)):
        if spam_block_val > 1000000000:
            remaining_hours = (spam_block_val - current_time) / 3600
            if remaining_hours <= 0:
                return True, "خالي من الحظر (انتهت مدة الحظر)"
            elif remaining_hours <= max_wait_hours:
                return True, f"محظور مؤقتاً (ينفك بعد {remaining_hours:.1f} ساعة)"
            else:
                return False, f"محظور مؤقتاً لمدة طويلة ({remaining_hours:.1f} ساعة)"
        else:
            return False, "محظور (حظر دائم أو غير محدد)"
            
    if isinstance(spam_block_val, str):
        if spam_block_val.isdigit():
            val = int(spam_block_val)
            if val > 1000000000:
                remaining_hours = (val - current_time) / 3600
                if remaining_hours <= 0:
                    return True, "خالي من الحظر (انتهت مدة الحظر)"
                elif remaining_hours <= max_wait_hours:
                    return True, f"محظور مؤقتاً (ينفك بعد {remaining_hours:.1f} ساعة)"
                else:
                    return False, f"محظور مؤقتاً لمدة طويلة ({remaining_hours:.1f} ساعة)"
            return False, "محظور (حظر دائم)"
            
        for fmt in ('%d.%m.%Y %H:%M', '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
            try:
                dt = datetime.strptime(spam_block_val.strip(), fmt)
                remaining_hours = (dt.timestamp() - current_time) / 3600
                if remaining_hours <= 0:
                    return True, "خالي من الحظر (انتهت مدة الحظر)"
                elif remaining_hours <= max_wait_hours:
                    return True, f"محظور مؤقتاً (ينفك بعد {remaining_hours:.1f} ساعة)"
                else:
                    return False, f"محظور مؤقتاً لمدة طويلة ({remaining_hours:.1f} ساعة)"
            except Exception:
                continue
                
        low = spam_block_val.lower().strip()
        if low in ('no', 'false', 'none', '0'):
            return True, "خالي من الحظر (No Spam Block)"
        if any(w in low for w in ['permanent', 'вечн', 'eternal', 'never', 'yes', 'true']):
            return False, "محظور (حظر دائم)"
            
        return False, f"محظور (حالة غير معروفة: {spam_block_val})"
        
    return False, "محظور (غير معروف)"

# -------------------------------------------------------------------
# Fast Buy Action via Lolzteam API
# -------------------------------------------------------------------
def execute_lzt_fast_buy(lzt_token, item_id):
    headers = {
        "Authorization": f"Bearer {lzt_token}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    # 1. Try fast-buy endpoint
    url_fast = f"https://api.lzt.market/{item_id}/fast-buy"
    try:
        r = requests.post(url_fast, headers=headers, timeout=12)
        if r.status_code == 200:
            return True, r.json()
    except Exception:
        pass
        
    # 2. Try reserve then confirm-buy
    try:
        url_res = f"https://api.lzt.market/{item_id}/reserve"
        r_res = requests.post(url_res, headers=headers, timeout=10)
        if r_res.status_code == 200:
            url_conf = f"https://api.lzt.market/{item_id}/confirm-buy"
            r_conf = requests.post(url_conf, headers=headers, timeout=10)
            if r_conf.status_code == 200:
                return True, r_conf.json()
        return False, r_res.json() if r_res.status_code != 200 else {"error": "Confirm failed"}
    except Exception as e:
        return False, {"error": str(e)}

# -------------------------------------------------------------------
# Send Alert Function (With Fast-Buy & Manual-Buy Buttons)
# -------------------------------------------------------------------
def send_telegram_alert(bot_token, chat_id, item, spam_status, sell_usd, best_bot, buy_usd, profit_usd, stream_type="aged"):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    item_id = item.get("item_id")
    price_rub = item.get("price")
    title = item.get("title", "بدون عنوان")
    country = item.get("telegram_country", "غير معروف")
    is_premium = item.get("telegram_premium", 0)
    
    premium_str = "نعم (Premium)" if is_premium else "لا"
    ccode = resolve_country_code(country, title)
    country_display = f"{country} ({ccode})" if ccode and ccode != country else country
    
    rub_per_usd = 90.0
    sell_rub = sell_usd * rub_per_usd
    profit_rub = profit_usd * rub_per_usd
    
    if stream_type == "fresh":
        header = f"<b>⚡ [صيد خاطف ⚡] حساب جديد بسعر {price_rub} ₽ (≤ 40 ₽ | خالٍ من السبام)</b>"
        note = "<b>⚡ نوع الصفقة:</b> حساب طازج/جديد بسعر رخيص وخالٍ تماماً من حظر السبام (0% Spam)."
    else:
        header = f"<b>🔔 [حساب معتق 24H+] صفقة مربحة (+${profit_usd:.2f} USD)</b>"
        note = "<b>⏳ عمر الجلسة:</b> متصل منذ 24H+ (سهل طرد الجلسات من الموقع مباشرة)."

    text = (
        f"{header}\n\n"
        f"<b>📝 العنوان:</b> {title}\n"
        f"<b>💵 سعر الشراء:</b> {price_rub} ₽ (≈ ${buy_usd:.2f} USD)\n"
        f"<b>🌍 الدولة:</b> {country_display}\n"
        f"<b>💰 أعلى سعر بيع لبوتاتك:</b> ${sell_usd:.2f} USD (≈ {sell_rub:.0f} ₽) <i>[{best_bot}]</i>\n"
        f"<b>💚 الربح الصافي المتوقع:</b> <b>+${profit_usd:.2f} USD</b> (≈ +{profit_rub:.0f} ₽)\n"
        f"<b>🚫 حالة السبام:</b> {spam_status}\n"
        f"<b>✨ مميزات إضافية (Premium):</b> {premium_str}\n"
        f"{note}\n\n"
        f"🔗 <a href='https://lzt.market/{item_id}/'>اضغط هنا للشراء يدوياً من الموقع</a>"
    )
    
    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "⚡ شراء فوري من رصيدي ⚡", "callback_data": f"fastbuy:{item_id}:{buy_usd:.2f}:{profit_usd:.2f}:{best_bot}:{ccode}"}
            ],
            [
                {"text": "🛒 تم الشراء يدوياً", "callback_data": f"buy:{item_id}:{buy_usd:.2f}:{profit_usd:.2f}:{best_bot}:{ccode}"},
                {"text": "❌ تجاهل", "callback_data": f"ignore:{item_id}"}
            ]
        ]
    }
    
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": reply_markup
    }
    
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code == 200:
            print(f"[Telegram] Alert sent for item {item_id} ({stream_type}).")
            return True
        else:
            print(f"[Telegram] Failed to send alert: {r.status_code} - {r.text}")
            return False
    except Exception as e:
        print(f"[Telegram] Error sending alert: {e}")
        return False

# -------------------------------------------------------------------
# Price List Text Parser from Forwarded Messages
# -------------------------------------------------------------------
def parse_and_update_prices_from_text(text):
    sell_prices = load_sell_prices()
    updated_count = 0
    
    # Matches patterns like "+971: 1.65$", "AE: 1.65$", "Algeria (+213): 0.4$"
    lines = text.split('\n')
    for line in lines:
        # Pattern 1: (+code) ... 1.5$
        m_phone = re.search(r'\(\+(\d+)\).*?:\s*([0-9.]+)[\$]?', line)
        if m_phone:
            phone_code = m_phone.group(1)
            price = float(m_phone.group(2))
            ccode = PHONE_PREFIX_TO_CODE.get(phone_code)
            if ccode:
                if ccode not in sell_prices:
                    sell_prices[ccode] = {"best_usd": price, "best_bot": "Updated Bot"}
                else:
                    if price > sell_prices[ccode].get("best_usd", 0):
                        sell_prices[ccode]["best_usd"] = price
                        sell_prices[ccode]["best_bot"] = "Updated Bot"
                updated_count += 1
                continue
                
        # Pattern 2: [country]-CC: 1.5$
        m_code = re.search(r'[–-]([A-Za-z]{2}):\s*([0-9.]+)[\$]?', line)
        if m_code:
            ccode = m_code.group(1).upper()
            price = float(m_code.group(2))
            if ccode not in sell_prices:
                sell_prices[ccode] = {"best_usd": price, "best_bot": "Updated Bot"}
            else:
                if price > sell_prices[ccode].get("best_usd", 0):
                    sell_prices[ccode]["best_usd"] = price
                    sell_prices[ccode]["best_bot"] = "Updated Bot"
            updated_count += 1
            
    if updated_count > 0:
        try:
            with open(SELL_PRICES_FILE, "w", encoding="utf-8") as f:
                json.dump(sell_prices, f, indent=2)
        except Exception:
            pass
            
    return updated_count, len(sell_prices)

# -------------------------------------------------------------------
# Background Telegram Listener (Callbacks, Fast-Buy & Commands)
# -------------------------------------------------------------------
def telegram_bot_listener(bot_token, lzt_token, min_profit_usd=0.30):
    print("[Telegram Listener] Background bot listener started...")
    offset = 0
    base_url = f"https://api.telegram.org/bot{bot_token}/"
    
    while True:
        try:
            url = f"{base_url}getUpdates?offset={offset}&timeout=20"
            r = requests.get(url, timeout=25)
            if r.status_code != 200:
                time.sleep(2)
                continue
                
            data = r.json()
            results = data.get("result", [])
            
            for update in results:
                offset = update["update_id"] + 1
                
                # Handle Inline Button Clicks (Callbacks)
                if "callback_query" in update:
                    cb = update["callback_query"]
                    cb_id = cb["id"]
                    cb_data = cb.get("data", "")
                    msg = cb.get("message", {})
                    chat_id = msg.get("chat", {}).get("id")
                    msg_id = msg.get("message_id")
                    
                    parts = cb_data.split(":")
                    action = parts[0]
                    
                    if action == "fastbuy":
                        item_id = parts[1]
                        cost_usd = float(parts[2])
                        profit_usd = float(parts[3])
                        best_bot = parts[4] if len(parts) > 4 else "Bot"
                        country = parts[5] if len(parts) > 5 else "Unknown"
                        
                        requests.post(f"{base_url}answerCallbackQuery", json={"callback_query_id": cb_id, "text": "⚡ جاري الشراء الفوري عبر الـ API..."})
                        
                        # Execute Fast-Buy
                        success, buy_resp = execute_lzt_fast_buy(lzt_token, item_id)
                        
                        if success:
                            log_bought_item(item_id, cost_usd, profit_usd, best_bot, country)
                            edit_text = (
                                msg.get("text", "") + "\n\n"
                                f"🎉 <b>تم شراء الحساب بنجاح وفوراً من رصيدك عبر API! ⚡</b>\n"
                                f"🔗 <a href='https://lzt.market/{item_id}/'>اضغط هنا لفتح وتحميل بيانات الحساب</a>\n\n"
                                f"<i>اختر حالة البيع لتسجيل الأرباح أو الخسائر في السجل المالي /stats:</i>"
                            )
                            edit_markup = {
                                "inline_keyboard": [
                                    [
                                        {"text": "✅ تم البيع بنجاح للبوت", "callback_data": f"sold:{item_id}"},
                                        {"text": "💔 تم حظره / سحبه (خسارة)", "callback_data": f"banned:{item_id}"}
                                    ]
                                ]
                            }
                        else:
                            edit_text = (
                                msg.get("text", "") + "\n\n"
                                f"❌ <b>فشل الشراء:</b> الحساب تم بيعه بالفعل لشخص آخر في الموقع أو الرصيد غير كافٍ!"
                            )
                            edit_markup = {"inline_keyboard": []}
                            
                        requests.post(f"{base_url}editMessageText", json={
                            "chat_id": chat_id,
                            "message_id": msg_id,
                            "text": edit_text,
                            "parse_mode": "HTML",
                            "reply_markup": edit_markup
                        })
                        
                    elif action == "buy":
                        item_id = parts[1]
                        cost_usd = float(parts[2])
                        profit_usd = float(parts[3])
                        best_bot = parts[4] if len(parts) > 4 else "Bot"
                        country = parts[5] if len(parts) > 5 else "Unknown"
                        
                        log_bought_item(item_id, cost_usd, profit_usd, best_bot, country)
                        
                        edit_text = (
                            msg.get("text", "") + "\n\n"
                            f"<b>🛒 تم تأكيد شراء هذا الحساب! (تكلفة الشراء: ${cost_usd:.2f} USD)</b>\n"
                            f"<i>اختر حالة البيع لتسجيل الأرباح أو الخسائر في السجل المالي:</i>"
                        )
                        edit_markup = {
                            "inline_keyboard": [
                                [
                                    {"text": "✅ تم البيع بنجاح للبوت", "callback_data": f"sold:{item_id}"},
                                    {"text": "💔 تم حظره / سحبه (خسارة)", "callback_data": f"banned:{item_id}"}
                                ]
                            ]
                        }
                        
                        requests.post(f"{base_url}editMessageText", json={
                            "chat_id": chat_id,
                            "message_id": msg_id,
                            "text": edit_text,
                            "parse_mode": "HTML",
                            "reply_markup": edit_markup
                        })
                        requests.post(f"{base_url}answerCallbackQuery", json={"callback_query_id": cb_id, "text": "تم تسجيل شراء الحساب!"})
                        
                    elif action == "sold":
                        item_id = parts[1]
                        mark_item_sold(item_id)
                        
                        edit_text = (
                            msg.get("text", "") + "\n\n"
                            f"<b>✅ تم تسجيل البيع بنجاح! 🎉 (أضيفت الأرباح لتقريرك المالي /stats)</b>"
                        )
                        requests.post(f"{base_url}editMessageText", json={
                            "chat_id": chat_id,
                            "message_id": msg_id,
                            "text": edit_text,
                            "parse_mode": "HTML"
                        })
                        requests.post(f"{base_url}answerCallbackQuery", json={"callback_query_id": cb_id, "text": "مبروك! تم تسجيل أرباح البيع."})
                        
                    elif action == "banned":
                        item_id = parts[1]
                        mark_item_banned(item_id)
                        
                        edit_text = (
                            msg.get("text", "") + "\n\n"
                            f"<b>💔 تم تسجيل الخسارة. (تم تحديث حاسبة التعويض في /stats)</b>"
                        )
                        requests.post(f"{base_url}editMessageText", json={
                            "chat_id": chat_id,
                            "message_id": msg_id,
                            "text": edit_text,
                            "parse_mode": "HTML"
                        })
                        requests.post(f"{base_url}answerCallbackQuery", json={"callback_query_id": cb_id, "text": "تم تسجيل الخسارة والتحديث."})
                        
                    elif action == "ignore":
                        requests.post(f"{base_url}editMessageText", json={
                            "chat_id": chat_id,
                            "message_id": msg_id,
                            "text": msg.get("text", "") + "\n\n<i>❌ تم تجاهل هذا الحساب (لم يُحسب في الأرباح أو الخسائر).</i>",
                            "parse_mode": "HTML"
                        })
                        requests.post(f"{base_url}answerCallbackQuery", json={"callback_query_id": cb_id, "text": "تم التجاهل."})

                # Handle Text Messages & Forwarded Price Lists
                if "message" in update:
                    m = update["message"]
                    chat_id = m.get("chat", {}).get("id")
                    text = m.get("text", "").strip()
                    
                    if text in ("/stats", "/start"):
                        stats = get_stats_summary(min_profit_usd)
                        report = (
                            f"📊 <b>التقرير المالي وإحصائيات التجار المباشرة:</b>\n"
                            f"--------------------------------------------------\n"
                            f"🛒 <b>إجمالي الحسابات المشتراة:</b> {stats['total_bought']}\n"
                            f"✅ <b>حسابات تم بيعها بنجاح:</b> {stats['sold_count']}\n"
                            f"💔 <b>حسابات خاسرة (حظر/سحب):</b> {stats['banned_count']}\n"
                            f"⏳ <b>حسابات قيد الانتظار:</b> {stats['pending_count']}\n\n"
                            f"💵 <b>إجمالي الأرباح المحققة:</b> +${stats['total_profit_usd']:.2f} USD\n"
                            f"💸 <b>إجمالي الخسائر:</b> -${stats['total_loss_usd']:.2f} USD\n"
                            f"⚖️ <b>صافي الربح الفعلي الحقيقي:</b> <b>+${stats['net_balance_usd']:.2f} USD</b>\n"
                            f"--------------------------------------------------\n"
                        )
                        if stats['recovery_needed'] > 0:
                            report += f"🎯 <b>حاسبة التعويض:</b> تحتاج لبيع <b>{stats['recovery_needed']} حسابات</b> جديدة بربح ${min_profit_usd:.2f} لتعويض كافة الخسائر الحالية!"
                        else:
                            report += f"✨ <b>وضعك المالي ممتاز: لا توجد خسائر تحتاج لتعويض حالياً! 🎉</b>"
                            
                        requests.post(f"{base_url}sendMessage", json={"chat_id": chat_id, "text": report, "parse_mode": "HTML"})
                        
                    elif text == "/reset_stats":
                        reset_db_stats()
                        requests.post(f"{base_url}sendMessage", json={"chat_id": chat_id, "text": "♻️ تم تصفير جميع الإحصائيات والسجل المالي بنجاح."})
                        
                    # Check if user sent/forwarded a price list
                    elif any(ch in text for ch in ("$", "Free:", "–", ":")) and len(text) > 40:
                        updated_cnt, total_cnt = parse_and_update_prices_from_text(text)
                        if updated_cnt > 0:
                            reply_msg = (
                                f"✅ <b>تم تحديث أسعار البيع بنجاح!</b>\n"
                                f"🔄 تم تحديث أسعار <b>{updated_cnt} دولة</b> ومقارنتها بأفضل الأسعار.\n"
                                f"🌍 إجمالي الدول المسجلة في قاعدة البوت الآن: <b>{total_cnt} دولة</b>."
                            )
                            requests.post(f"{base_url}sendMessage", json={"chat_id": chat_id, "text": reply_msg, "parse_mode": "HTML"})

        except Exception as e:
            time.sleep(2)

# -------------------------------------------------------------------
# Helper to Process Listings for Both Streams
# -------------------------------------------------------------------
def process_stream_items(items, stream_type, min_profit_usd, max_price_rub, max_wait_hours, rub_per_usd, sell_prices, sent_alerts, tg_token, tg_chat_id, lzt_token, auto_buy_enabled, auto_buy_min_profit_usd):
    for item in items:
        item_id = str(item.get("item_id"))
        if not item_id or item_id in sent_alerts:
            continue

        buy_rub = float(item.get("price", 0))
        if max_price_rub and buy_rub > max_price_rub:
            sent_alerts.add(item_id)
            continue

        country_raw = item.get("telegram_country", "")
        title_raw = item.get("title", "")
        ccode = resolve_country_code(country_raw, title_raw)
        
        sell_info = sell_prices.get(ccode, {})
        if isinstance(sell_info, dict):
            sell_usd = sell_info.get("best_usd", 0.0)
            best_bot = sell_info.get("best_bot", "Bot")
        else:
            sell_usd = float(sell_info) if sell_info else 0.0
            best_bot = "Bot"
            
        if not sell_usd or sell_usd <= 0:
            fallback_info = DEFAULT_SELL_PRICES.get(ccode, {})
            sell_usd = fallback_info.get("best_usd", 0.0)
            best_bot = fallback_info.get("best_bot", "Bot")

        if not sell_usd or sell_usd <= 0:
            if buy_rub <= 40:
                sell_usd = 0.80
                best_bot = "Market"
            else:
                sent_alerts.add(item_id)
                continue

        buy_usd = buy_rub / rub_per_usd
        expected_profit_usd = sell_usd - buy_usd

        # Profit Filter
        if expected_profit_usd < min_profit_usd:
            sent_alerts.add(item_id)
            continue

        # Check Spam Block
        spam_block_val = item.get("telegram_spam_block")
        
        if stream_type == "fresh":
            if spam_block_val:
                low = str(spam_block_val).lower().strip()
                if low not in ('no', 'false', 'none', '0', ''):
                    sent_alerts.add(item_id)
                    continue
            spam_status = "خالٍ تماماً من السبام (0% Spam)"
        else:
            is_accepted, spam_status = parse_spamblock(spam_block_val, max_wait_hours)
            if not is_accepted:
                sent_alerts.add(item_id)
                continue

        # Check for Auto-Snipe (Automatic Fast-Buy for High Profit Deals)
        if auto_buy_enabled and expected_profit_usd >= auto_buy_min_profit_usd:
            print(f"[AUTO-SNIPE TRIGGERED] Buying Item {item_id} automatically via API! (Expected Profit: +${expected_profit_usd:.2f})")
            buy_ok, buy_resp = execute_lzt_fast_buy(lzt_token, item_id)
            if buy_ok:
                log_bought_item(item_id, buy_usd, expected_profit_usd, best_bot, ccode)
                sent_alerts.add(item_id)
                save_sent_alerts(sent_alerts)
                
                # Send Auto-Snipe Success Notification
                auto_text = (
                    f"🎯 <b>[تم القنص الآلي والشراء بنجاح! ⚡]</b>\n\n"
                    f"<b>📝 العنوان:</b> {item.get('title', 'بدون عنوان')}\n"
                    f"<b>💵 سعر الشراء:</b> {buy_rub} ₽ (≈ ${buy_usd:.2f} USD)\n"
                    f"<b>🌍 الدولة:</b> {country_raw} ({ccode})\n"
                    f"<b>💰 أعلى سعر بيع لبوتاتك:</b> ${sell_usd:.2f} USD <i>[{best_bot}]</i>\n"
                    f"<b>💚 الربح الصافي المتوقع:</b> <b>+${expected_profit_usd:.2f} USD</b>\n"
                    f"<b>⚡ السرعة:</b> تم حجز وشراء الحساب آلياً عبر API في 0.2 ثانية!\n\n"
                    f"🔗 <a href='https://lzt.market/{item_id}/'>اضغط هنا لفتح وتحميل بيانات الحساب</a>\n\n"
                    f"<i>اختر حالة البيع لتسجيل الأرباح في السجل المالي /stats:</i>"
                )
                auto_markup = {
                    "inline_keyboard": [
                        [
                            {"text": "✅ تم البيع بنجاح للبوت", "callback_data": f"sold:{item_id}"},
                            {"text": "💔 تم حظره / سحبه (خسارة)", "callback_data": f"banned:{item_id}"}
                        ]
                    ]
                }
                requests.post(f"https://api.telegram.org/bot{tg_token}/sendMessage", json={
                    "chat_id": tg_chat_id, "text": auto_text, "parse_mode": "HTML", "reply_markup": auto_markup
                })
                continue

        # Send Standard Telegram Alert for Matched Item
        print(f"[{stream_type.upper()} Match] Item {item_id} | Country: {ccode} | Buy: {buy_rub} RUB (${buy_usd:.2f}) | Sell: ${sell_usd:.2f} | Profit: +${expected_profit_usd:.2f} USD")
        
        success = send_telegram_alert(
            tg_token, tg_chat_id, item, spam_status, 
            sell_usd, best_bot, buy_usd, expected_profit_usd, stream_type=stream_type
        )
        
        if success:
            sent_alerts.add(item_id)
            save_sent_alerts(sent_alerts)

# -------------------------------------------------------------------
# Main Intensive Dual-Stream LZT Monitoring Loop (3s Interval)
# -------------------------------------------------------------------
def monitor_lzt():
    init_db()
    config = load_config()
    
    lzt_token = config.get("lzt_api_token")
    tg_token = config.get("telegram_bot_token")
    tg_chat_id = config.get("telegram_chat_id")
    interval = config.get("check_interval_seconds", 3)
    filters = config.get("filters", {})
    
    min_profit_usd = filters.get("min_profit_usd", 0.30)
    auto_buy_enabled = filters.get("auto_buy_enabled", True)
    auto_buy_min_profit_usd = filters.get("auto_buy_min_profit_usd", 0.80)
    fresh_max_price_rub = filters.get("fresh_max_price_rub", 40)
    max_wait_hours = filters.get("spam_block_max_wait_hours", 72)
    rub_per_usd = 90.0
    
    if not lzt_token or not tg_token or not tg_chat_id:
        print("Error: Missing credentials in config.json or environment variables.")
        sys.exit(1)

    threading.Thread(target=telegram_bot_listener, args=(tg_token, lzt_token, min_profit_usd), daemon=True).start()

    sent_alerts = load_sent_alerts()
    
    print("--------------------------------------------------")
    print(f"Starting Ultra-Smart Dual-Stream Telegram Monitor (3s loop)...")
    print(f"Auto-Snipe: Enabled for deals with profit >= +${auto_buy_min_profit_usd:.2f} USD")
    print(f"Stream 1 (Aged 24H+): Min Profit +${min_profit_usd:.2f} USD")
    print(f"Stream 2 (Fresh Cheap ⚡): Max Price {fresh_max_price_rub} RUB, 0% Spam")
    print("--------------------------------------------------")
    
    session = requests.Session()
    headers = {
        "Authorization": f"Bearer {lzt_token}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    url = "https://api.lzt.market/telegram"
    fallback_url = "https://prod-api.lzt.market/telegram"
    consecutive_errors = 0

    # Clean initial pre-population of all existing market items so no old accounts are alerted
    try:
        print("[System] Pre-populating existing market items to avoid duplicate old alerts...")
        r_init = session.get(url, headers=headers, params={"pmin": 2, "pmax": 500, "currency": "rub", "order_by": "pdate_to_down"}, timeout=10)
        if r_init.status_code == 200:
            init_items = r_init.json().get("items") or r_init.json().get("accounts") or []
            for item in init_items:
                item_id = str(item.get("item_id"))
                if item_id:
                    sent_alerts.add(item_id)
            save_sent_alerts(sent_alerts)
            print(f"[System] Successfully pre-populated {len(init_items)} existing items. Monitoring active!")
    except Exception as e:
        print(f"[Warning] Initial pre-population error: {e}")
    
    while True:
        try:
            current_url = fallback_url if consecutive_errors >= 3 else url
            sell_prices = load_sell_prices()

            # Query 1: Stream 1 (Aged 24H+ Accounts)
            params_aged = {
                "pmin": filters.get("pmin", 2),
                "pmax": filters.get("pmax", 500),
                "currency": filters.get("currency", "rub"),
                "2fa": "no",
                "nsb": 1,
                "nsb_by_me": 1,
                "allow_geo_spamblock": 0,
                "spam": "nomatter",
                "daybreak": 1,
                "order_by": "pdate_to_down"
            }
            
            resp_aged = session.get(current_url, headers=headers, params=params_aged, timeout=10)
            if resp_aged.status_code == 200:
                consecutive_errors = 0
                items_aged = resp_aged.json().get("items") or resp_aged.json().get("accounts") or []
                process_stream_items(items_aged, "aged", min_profit_usd, None, max_wait_hours, rub_per_usd, sell_prices, sent_alerts, tg_token, tg_chat_id, lzt_token, auto_buy_enabled, auto_buy_min_profit_usd)

            # Query 2: Stream 2 (Fresh Cheap <= 40 RUB Accounts, No Spam)
            params_fresh = {
                "pmin": filters.get("pmin", 2),
                "pmax": fresh_max_price_rub,
                "currency": filters.get("currency", "rub"),
                "2fa": "no",
                "nsb": 1,
                "nsb_by_me": 1,
                "allow_geo_spamblock": 0,
                "spam": "no",
                "order_by": "pdate_to_down"
            }
            
            resp_fresh = session.get(current_url, headers=headers, params=params_fresh, timeout=10)
            if resp_fresh.status_code == 200:
                consecutive_errors = 0
                items_fresh = resp_fresh.json().get("items") or resp_fresh.json().get("accounts") or []
                process_stream_items(items_fresh, "fresh", 0.15, fresh_max_price_rub, max_wait_hours, rub_per_usd, sell_prices, sent_alerts, tg_token, tg_chat_id, lzt_token, auto_buy_enabled, auto_buy_min_profit_usd)

        except requests.exceptions.RequestException as req_err:
            print(f"[Connection Error] {req_err}")
            consecutive_errors += 1
            time.sleep(5)
        except Exception as e:
            print(f"[Unexpected Error] {e}")
            time.sleep(interval)
            
        time.sleep(interval)

if __name__ == "__main__":
    monitor_lzt()
