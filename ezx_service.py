import os
import sys
import re
import time
import json
import asyncio
import threading
import requests
from datetime import datetime

API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"
SESSION_STRING_FILE = os.path.join(os.path.dirname(__file__), "ezx_string_session.txt")
BOT_USERNAME = "ezxtg_bot"
CHECK_INTERVAL_SECONDS = 600  # Check every 10 minutes
REMINDER_INTERVAL_SECONDS = 300  # Remind every 5 minutes
MAX_REMINDERS = 10

EZX_ACTIVE_REMINDERS = {}  # alert_key: {"reminders_left": 9, "text": ..., "markup": ..., "chat_id": ..., "bot_token": ...}
EZX_ACKNOWLEDGED = set()
_LOCK = threading.Lock()

def stop_ezx_reminder(alert_key):
    with _LOCK:
        if alert_key in EZX_ACTIVE_REMINDERS:
            del EZX_ACTIVE_REMINDERS[alert_key]
        EZX_ACKNOWLEDGED.add(alert_key)
    print(f"[EZX Service] Acknowledged alert: {alert_key}. Stopped reminders.")

def is_syria_match(cname, prefix, btn_text):
    text_combined = f"{cname} {prefix} {btn_text}".lower()
    syria_variants = ["سوريا", "سورية", "سريا", "سوريه", "syria", "syr", "+963", "963"]
    return any(v in text_combined for v in syria_variants)

def is_cheap_spam(cname, prefix, btn_text, is_fake_cat=False):
    is_spam_tag = is_fake_cat or any(w in btn_text.lower() for w in ["مزيف", "سبام", "fake", "spam", "s~f", "s-f"])
    if not is_spam_tag:
        return False
    prices = [float(x) for x in re.findall(r'(\d+(?:\.\d+)?)', btn_text)]
    return bool(prices and min(prices) < 0.11)

def run_ezx_cloud_monitor(tg_token, tg_chat_id, session_str=None):
    if not session_str:
        if os.path.exists(SESSION_STRING_FILE):
            try:
                with open(SESSION_STRING_FILE, "r", encoding="utf-8") as f:
                    session_str = f.read().strip()
            except Exception as e:
                print(f"[EZX Cloud Monitor] Error reading session file: {e}")

    if not session_str:
        print("[EZX Cloud Monitor] No session string available. EZX Cloud Monitor disabled.")
        return

    print("==================================================")
    print("🚀 Starting EZX 24/7 Cloud Stock Monitor & Persistent Reminder Engine...")
    print(f"Target: Syria (Any Price) + Spam Accounts (< $0.11)")
    print(f"Check Interval: Every 10 mins | Reminder: Every 5 mins (up to 10 times)")
    print("==================================================")

    # 1. Background Persistent Reminder Loop (Every 5 minutes)
    def reminder_loop():
        while True:
            try:
                time.sleep(REMINDER_INTERVAL_SECONDS)
                with _LOCK:
                    keys = list(EZX_ACTIVE_REMINDERS.keys())
                
                for k in keys:
                    with _LOCK:
                        item = EZX_ACTIVE_REMINDERS.get(k)
                        if not item:
                            continue
                        if item["reminders_left"] <= 0:
                            del EZX_ACTIVE_REMINDERS[k]
                            continue
                        item["reminders_left"] -= 1
                        remind_num = MAX_REMINDERS - item["reminders_left"]
                        bot_token = item["bot_token"]
                        chat_id = item["chat_id"]
                        raw_text = item["text"]
                        markup = item["markup"]

                    base_url = f"https://api.telegram.org/bot{bot_token}/"
                    reminder_text = (
                        f"⏰ <b>[تذكير متكرر {remind_num}/{MAX_REMINDERS} - صفقة معلقة ⚠️]</b>\n"
                        f"<i>لم يتم الضغط على 'تم التحقق' بعد! الحسابات ما زالت تنتظرك:</i>\n\n"
                        f"{raw_text}"
                    )
                    try:
                        requests.post(f"{base_url}sendMessage", json={
                            "chat_id": chat_id,
                            "text": reminder_text,
                            "parse_mode": "HTML",
                            "reply_markup": markup
                        }, timeout=10)
                        print(f"[EZX Reminder] Sent reminder {remind_num}/{MAX_REMINDERS} for {k}")
                    except Exception as req_err:
                        print(f"[EZX Reminder Request Error]: {req_err}")

            except Exception as e:
                print(f"[EZX Reminder Loop Error]: {e}")

    threading.Thread(target=reminder_loop, daemon=True).start()

    # 2. Asynchronous Telethon Checker Loop (Every 10 minutes)
    async def async_checker():
        from telethon import TelegramClient
        from telethon.sessions import StringSession

        categories = [
            {"path": ["buy_sessions", "sess_cat_new"], "name": "شراء الجلسات (حسابات جديدة 🆕)", "is_fake": False},
            {"path": ["buy", "buy_category_new"], "name": "شراء الأرقام (حسابات جديدة 🆕)", "is_fake": False}
        ]

        while True:
            client = None
            try:
                client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
                await client.connect()

                if not await client.is_user_authorized():
                    print("[EZX Cloud Monitor] Client not authorized!")
                    await client.disconnect()
                    await asyncio.sleep(600)
                    continue

                bot = await client.get_input_entity(BOT_USERNAME)
                base_url = f"https://api.telegram.org/bot{tg_token}/"

                for cat in categories:
                    try:
                        await client.send_message(bot, "/start")
                        await asyncio.sleep(2.5)

                        # Step 1
                        msgs = await client.get_messages(bot, limit=1)
                        if not msgs or not msgs[0].reply_markup:
                            continue

                        btn1 = cat["path"][0]
                        clicked1 = False
                        for row in msgs[0].reply_markup.rows:
                            for b in row.buttons:
                                d = getattr(b, 'data', b'').decode('utf-8', errors='ignore')
                                if d == btn1:
                                    await msgs[0].click(data=b.data)
                                    clicked1 = True
                                    break
                            if clicked1:
                                break

                        if not clicked1:
                            continue

                        await asyncio.sleep(2.5)

                        # Step 2
                        msgs = await client.get_messages(bot, limit=1)
                        if not msgs or not msgs[0].reply_markup:
                            continue

                        btn2 = cat["path"][1]
                        clicked2 = False
                        for row in msgs[0].reply_markup.rows:
                            for b in row.buttons:
                                d = getattr(b, 'data', b'').decode('utf-8', errors='ignore')
                                if d == btn2:
                                    await msgs[0].click(data=b.data)
                                    clicked2 = True
                                    break
                            if clicked2:
                                break

                        if not clicked2:
                            continue

                        await asyncio.sleep(2.5)

                        # Parse items
                        msgs = await client.get_messages(bot, limit=1)
                        if not msgs or not msgs[0].reply_markup:
                            continue

                        resp = msgs[0]
                        for row in resp.reply_markup.rows:
                            for b in row.buttons:
                                btext = b.text.strip()
                                if "رجوع" in btext:
                                    continue
                                m = re.search(r'^(.*?)\s*\[(\d+)\]\s*\((.*?)\)', btext)
                                if not m:
                                    continue
                                cname = m.group(1).strip()
                                count = int(m.group(2))
                                price = m.group(3).strip()
                                cb_data = getattr(b, 'data', b'').decode('utf-8', errors='ignore')
                                pref_m = re.search(r'(\+\d+)', cb_data)
                                prefix = pref_m.group(1) if pref_m else ""

                                if count <= 0:
                                    continue

                                is_syria = is_syria_match(cname, prefix, btext)
                                is_cheap = is_cheap_spam(cname, prefix, btext, is_fake_cat=cat["is_fake"])

                                if is_syria or is_cheap:
                                    alert_key = f"ezx_{prefix}_{cname}_{count}_{price}".replace(" ", "_")
                                    with _LOCK:
                                        if alert_key in EZX_ACKNOWLEDGED or alert_key in EZX_ACTIVE_REMINDERS:
                                            continue

                                    tag_header = "🇸🇾 <b>[صيد VIP عاجل: توفر حسابات سوريا في البوت! 💎]</b>" if is_syria else "⚡ <b>[صيدة لقطة: حسابات سبام رخيصة جداً < 0.11$! 🎯]</b>"
                                    reason_tag = "طلب خاص: سوريا (بأي سعر)" if is_syria else "طلب خاص: سبام رخيص أقل من 0.11$"

                                    alert_text = (
                                        f"{tag_header}\n"
                                        f"━━━━━━━━━━━━━━━━━━━━\n"
                                        f"🎯 <b>النوع:</b> {cat['name']}\n"
                                        f"🌍 <b>الدولة:</b> <b>{cname}</b> ({prefix})\n"
                                        f"📦 <b>الكمية المتاحة:</b> <b>{count} حساب</b>\n"
                                        f"💵 <b>السعر في البوت:</b> <code>{price}</code>\n"
                                        f"💡 <b>السبب:</b> {reason_tag}\n"
                                        f"⏰ <b>وقت الرصد:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                                        f"━━━━━━━━━━━━━━━━━━━━\n"
                                        f"⚠️ <b>تنبيه تذكير نشط:</b> سيعيد البوت التذكير كل 5 دقائق (حتى 10 مرات) حتى تضغط زر التحقق أدناه!"
                                    )

                                    reply_markup = {
                                        "inline_keyboard": [
                                            [
                                                {"text": "✅ تم التحقق (إيقاف التنبيهات)", "callback_data": f"ack_ezx:{alert_key}"}
                                            ],
                                            [
                                                {"text": "🛒 فتح بوت EZX والشراء فوراً", "url": "https://t.me/ezxtg_bot"}
                                            ]
                                        ]
                                    }

                                    # Send initial alert via user's Telegram Monitor Bot!
                                    try:
                                        r_sent = requests.post(f"{base_url}sendMessage", json={
                                            "chat_id": tg_chat_id,
                                            "text": alert_text,
                                            "parse_mode": "HTML",
                                            "reply_markup": reply_markup
                                        }, timeout=10)
                                        if r_sent.status_code == 200:
                                            print(f"[EZX Cloud Monitor] Alert successfully sent for {cname} ({prefix})!")
                                    except Exception as send_err:
                                        print(f"[EZX Cloud Monitor] Error sending alert: {send_err}")

                                    # Register in persistent reminder engine
                                    with _LOCK:
                                        EZX_ACTIVE_REMINDERS[alert_key] = {
                                            "reminders_left": MAX_REMINDERS - 1,
                                            "text": alert_text,
                                            "markup": reply_markup,
                                            "chat_id": tg_chat_id,
                                            "bot_token": tg_token
                                        }

                    except Exception as cat_err:
                        print(f"[EZX Category Check Error]: {cat_err}")

                await client.disconnect()

            except Exception as loop_err:
                print(f"[EZX Async Loop Error]: {loop_err}")
                if client and client.is_connected():
                    try:
                        await client.disconnect()
                    except Exception:
                        pass

            # Sleep 10 minutes until next full scan
            await asyncio.sleep(CHECK_INTERVAL_SECONDS)

    asyncio.run(async_checker())
