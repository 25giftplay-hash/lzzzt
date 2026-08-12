import os
import sys
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

def get_stats_summary(min_profit_usd=0.70):
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
    
    # Calculate how many new sales at min_profit_usd needed to recover current losses
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
# Configuration & Country Mapping
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
                return json.load(f)
        except Exception:
            pass
    return {}

COUNTRY_NAME_TO_CODE = {
    "ukraine": "UA", "united arab emirates": "AE", "russia": "RU", "saudi arabia": "SA",
    "italy": "IT", "mexico": "MX", "kazakhstan": "KZ", "latvia": "LV", "portugal": "PT",
    "kyrgyzstan": "KG", "tajikistan": "TJ", "egypt": "EG", "iraq": "IQ", "turkey": "TR",
    "colombia": "CO", "argentina": "AR", "netherlands": "NL", "united kingdom": "GB",
    "great britain": "GB", "spain": "ES", "india": "IN", "vietnam": "VN", "germany": "DE",
    "france": "FR", "united states": "US", "canada": "CA", "switzerland": "CH",
    "qatar": "QA", "bahrain": "BH", "kuwait": "KW", "oman": "OM", "south korea": "KR",
    "taiwan": "TW", "japan": "JP", "australia": "AU", "singapore": "SG", "indonesia": "ID",
    "thailand": "TH", "philippines": "PH", "brazil": "BR", "chile": "CL", "peru": "PE",
    "morocco": "MA", "algeria": "DZ", "tunisia": "TN", "lebanon": "LB", "jordan": "JO",
    "belarus": "BY", "denmark": "DK", "slovenia": "SI", "austria": "AT", "croatia": "HR"
}

def get_country_code(country_str):
    if not country_str:
        return ""
    c = str(country_str).strip()
    if len(c) == 2:
        return c.upper()
    return COUNTRY_NAME_TO_CODE.get(c.lower(), c.upper())

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
# Send Alert with Interactive Inline Keyboard
# -------------------------------------------------------------------
def send_telegram_alert(bot_token, chat_id, item, spam_status, sell_usd, best_bot, buy_usd, profit_usd):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    item_id = item.get("item_id")
    price_rub = item.get("price")
    title = item.get("title", "بدون عنوان")
    country = item.get("telegram_country", "غير معروف")
    is_premium = item.get("telegram_premium", 0)
    
    premium_str = "نعم (Premium)" if is_premium else "لا"
    ccode = get_country_code(country)
    country_display = f"{country} ({ccode})" if ccode and ccode != country else country
    
    rub_per_usd = 90.0
    sell_rub = sell_usd * rub_per_usd
    profit_rub = profit_usd * rub_per_usd
    
    text = (
        f"<b>🔔 صفقة جديدة مربحة! (+${profit_usd:.2f} USD)</b>\n\n"
        f"<b>📝 العنوان:</b> {title}\n"
        f"<b>💵 سعر الشراء من الموقع:</b> {price_rub} ₽ (≈ ${buy_usd:.2f} USD)\n"
        f"<b>🌍 الدولة:</b> {country_display}\n"
        f"<b>💰 أعلى سعر بيع لبوتاتك:</b> ${sell_usd:.2f} USD (≈ {sell_rub:.0f} ₽) <i>[{best_bot}]</i>\n"
        f"<b>💚 الربح الصافي المتوقع:</b> <b>+${profit_usd:.2f} USD</b> (≈ +{profit_rub:.0f} ₽)\n"
        f"<b>🚫 حالة السبام:</b> {spam_status}\n"
        f"<b>✨ مميزات إضافية (Premium):</b> {premium_str}\n\n"
        f"🔗 <a href='https://lzt.market/{item_id}/'>اضغط هنا للشراء مباشرة من الموقع</a>"
    )
    
    # Inline Keyboard Buttons
    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "🛒 تم الشراء (أكد الشراء لحساب الربح)", "callback_data": f"buy:{item_id}:{buy_usd:.2f}:{profit_usd:.2f}:{best_bot}:{ccode}"}
            ],
            [
                {"text": "❌ لم أشترِ / تجاهل", "callback_data": f"ignore:{item_id}"}
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
            print(f"[Telegram] Alert sent for item {item_id}.")
            return True
        else:
            print(f"[Telegram] Failed to send alert: {r.status_code} - {r.text}")
            return False
    except Exception as e:
        print(f"[Telegram] Error sending alert: {e}")
        return False

# -------------------------------------------------------------------
# Background Telegram Bot Polling Thread (Interactive Callbacks & Commands)
# -------------------------------------------------------------------
def telegram_bot_listener(bot_token, min_profit_usd=0.70):
    print("[Telegram Listener] Background bot listener started...")
    offset = 0
    base_url = f"https://api.telegram.org/bot{bot_token}/"
    
    while True:
        try:
            url = f"{base_url}getUpdates?offset={offset}&timeout=20"
            r = requests.get(url, timeout=25)
            if r.status_code != 200:
                time.sleep(5)
                continue
                
            data = r.json()
            results = data.get("result", [])
            
            for update in results:
                offset = update["update_id"] + 1
                
                # Handle Inline Button Clicks (Callback Queries)
                if "callback_query" in update:
                    cb = update["callback_query"]
                    cb_id = cb["id"]
                    cb_data = cb.get("data", "")
                    msg = cb.get("message", {})
                    chat_id = msg.get("chat", {}).get("id")
                    msg_id = msg.get("message_id")
                    
                    parts = cb_data.split(":")
                    action = parts[0]
                    
                    if action == "buy":
                        item_id = parts[1]
                        cost_usd = float(parts[2])
                        profit_usd = float(parts[3])
                        best_bot = parts[4] if len(parts) > 4 else "Bot"
                        country = parts[5] if len(parts) > 5 else "Unknown"
                        
                        # Log as bought in SQLite
                        log_bought_item(item_id, cost_usd, profit_usd, best_bot, country)
                        
                        # Edit message to show status options
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

                # Handle Text Commands (/stats, /reset_stats)
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
                            report += f"✨ <b>وضعك المالي ممتازة: لا توجد خسائر تحتاج لتعويض حالياً! 🎉</b>"
                            
                        requests.post(f"{base_url}sendMessage", json={"chat_id": chat_id, "text": report, "parse_mode": "HTML"})
                        
                    elif text == "/reset_stats":
                        reset_db_stats()
                        requests.post(f"{base_url}sendMessage", json={"chat_id": chat_id, "text": "♻️ تم تصفير جميع الإحصائيات والسجل المالي بنجاح."})

        except Exception as e:
            time.sleep(3)

# -------------------------------------------------------------------
# Main LZT Monitoring Loop
# -------------------------------------------------------------------
def monitor_lzt():
    init_db()
    config = load_config()
    
    lzt_token = config.get("lzt_api_token")
    tg_token = config.get("telegram_bot_token")
    tg_chat_id = config.get("telegram_chat_id")
    interval = config.get("check_interval_seconds", 10)
    filters = config.get("filters", {})
    
    min_profit_usd = filters.get("min_profit_usd", 0.70)
    rub_per_usd = 90.0 # Standard RUB per USD rate
    
    if not lzt_token or not tg_token or not tg_chat_id:
        print("Error: Missing credentials in config.json or environment variables.")
        sys.exit(1)

    # Start background listener thread for Telegram buttons & /stats command
    threading.Thread(target=telegram_bot_listener, args=(tg_token, min_profit_usd), daemon=True).start()

    # Send a startup notification to Telegram
    print("[Telegram] Sending startup notification...")
    startup_url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
    startup_text = (
        "🤖 <b>تم بدء تشغيل رادار الأرباح المتقدم لـ Lolzteam بنجاح!</b>\n"
        "البوت متصل بالمنصة ومزود بنظام الأزرار التفاعلية وحاسبة التعويض.\n\n"
        f"🎯 <b>الحد الأدنى للربح الصافي:</b> +${min_profit_usd:.2f} USD لكل صفقة\n"
        f"📊 أرسل الأمر <b>/stats</b> للبوت في أي وقت لمشاهدة التقرير المالي الصافي."
    )
    try:
        requests.post(startup_url, json={"chat_id": tg_chat_id, "text": startup_text, "parse_mode": "HTML"}, timeout=10)
    except Exception as e:
        print(f"[Telegram] Error sending startup notification: {e}")

    sent_alerts = load_sent_alerts()
    is_first_run = True
    
    print("--------------------------------------------------")
    print(f"Starting Lolzteam Telegram Profit Radar...")
    print(f"Checking every {interval} seconds...")
    print(f"Min Expected Profit Filter: +${min_profit_usd:.2f} USD")
    print("--------------------------------------------------")
    
    session = requests.Session()
    headers = {
        "Authorization": f"Bearer {lzt_token}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    url = "https://api.lzt.market/telegram"
    fallback_url = "https://prod-api.lzt.market/telegram"
    
    api_params = {
        "pmin": filters.get("pmin", 2),
        "pmax": filters.get("pmax", 500), # Allow broad scanning, we filter by profit locally!
        "currency": filters.get("currency", "rub"),
        "2fa": filters.get("2fa", "no"),
        "nsb": 1 if filters.get("nsb", True) else 0,
        "nsb_by_me": 1 if filters.get("nsb_by_me", True) else 0,
        "allow_geo_spamblock": 1 if filters.get("allow_geo_spamblock", False) else 0,
        "spam": "nomatter",
        "order_by": "pdate_to_down"
    }
    
    if filters.get("daybreak"):
        api_params["daybreak"] = filters.get("daybreak")
        
    consecutive_errors = 0
    
    while True:
        try:
            current_url = fallback_url if consecutive_errors >= 3 else url
            if consecutive_errors >= 3:
                print(f"[System] Attempting fallback endpoint {fallback_url}...")

            response = session.get(current_url, headers=headers, params=api_params, timeout=15)
            
            if response.status_code != 200:
                print(f"[Error] LZT API returned code {response.status_code}: {response.text}")
                consecutive_errors += 1
                time.sleep(min(60, interval * 2))
                continue

            consecutive_errors = 0
            data = response.json()
            items = data.get("items") or data.get("accounts") or data.get("listings") or []
            
            if is_first_run:
                print(f"[System] First run detected. Pre-populating {len(items)} existing items...")
                for item in items:
                    item_id = str(item.get("item_id"))
                    if item_id:
                        sent_alerts.add(item_id)
                save_sent_alerts(sent_alerts)
                is_first_run = False
                print(f"[System] Pre-populated {len(items)} items. Now monitoring for high-profit listings.")
                time.sleep(interval)
                continue

            sell_prices = load_sell_prices()
            max_wait_hours = filters.get("spam_block_max_wait_hours", 72)
            
            for item in items:
                item_id = str(item.get("item_id"))
                if not item_id or item_id in sent_alerts:
                    continue

                country_raw = item.get("telegram_country", "")
                ccode = get_country_code(country_raw)
                
                # Check sell prices for this country
                sell_info = sell_prices.get(ccode, {})
                if isinstance(sell_info, dict):
                    sell_usd = sell_info.get("best_usd", 0.0)
                    best_bot = sell_info.get("best_bot", "Bot")
                else:
                    sell_usd = float(sell_info) if sell_info else 0.0
                    best_bot = "Bot"
                    
                if not sell_usd or sell_usd <= 0:
                    sent_alerts.add(item_id)
                    continue

                buy_rub = float(item.get("price", 0))
                buy_usd = buy_rub / rub_per_usd
                expected_profit_usd = sell_usd - buy_usd

                # Filter by Minimum Net Profit Requirement (>= $0.70 USD)
                if expected_profit_usd < min_profit_usd:
                    sent_alerts.add(item_id)
                    continue

                # Check Spam Block Status
                spam_block_val = item.get("telegram_spam_block")
                is_accepted, spam_status = parse_spamblock(spam_block_val, max_wait_hours)
                
                if not is_accepted:
                    sent_alerts.add(item_id)
                    continue

                # High Profit Match Found! Send Interactive Alert
                print(f"[Profit Match Found] Item {item_id} | Country: {ccode} | Buy: ${buy_usd:.2f} | Sell: ${sell_usd:.2f} | Net Profit: +${expected_profit_usd:.2f} USD")
                
                success = send_telegram_alert(
                    tg_token, tg_chat_id, item, spam_status, 
                    sell_usd, best_bot, buy_usd, expected_profit_usd
                )
                
                if success:
                    sent_alerts.add(item_id)
                    save_sent_alerts(sent_alerts)
                    
        except requests.exceptions.RequestException as req_err:
            print(f"[Connection Error] Connection failed: {req_err}")
            time.sleep(15)
        except Exception as e:
            print(f"[Unexpected Error] {e}")
            time.sleep(interval)
            
        time.sleep(interval)

if __name__ == "__main__":
    monitor_lzt()
