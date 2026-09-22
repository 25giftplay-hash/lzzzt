import html
import os
import sys
import re
import json
import time
import sqlite3
import threading
import requests
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

CONFIG_FILE = "config.json"
SENT_ALERTS_FILE = "sent_alerts.json"
SELL_PRICES_FILE = "sell_prices.json"
DB_FILE = "stats.db"

# Auto-Buy Rate Limit Tracking (Safeguard)
AUTO_BUY_TIMESTAMPS = []
AUTO_BUY_LOCK = threading.Lock()

# -------------------------------------------------------------------
# Embedded 195-Country Sell Price Database (Fallback)
# -------------------------------------------------------------------
DEFAULT_SELL_PRICES = {
  "FK": {
    "best_usd": 8,
    "best_bot": "Bot 1"
  },
  "XK": {
    "best_usd": 1.2,
    "best_bot": "Bot 3 (New Bot)"
  },
  "SN": {
    "best_usd": 0.45,
    "best_bot": "Bot 1"
  },
  "BN": {
    "best_usd": 1.8,
    "best_bot": "Bot 1"
  },
  "NR": {
    "best_usd": 1.5,
    "best_bot": "Bot 3 (New Bot)"
  },
  "BE": {
    "best_usd": 1.15,
    "best_bot": "Bot 1"
  },
  "IS": {
    "best_usd": 0.8,
    "best_bot": "Bot 1"
  },
  "FM": {
    "best_usd": 0.75,
    "best_bot": "Bot 1"
  },
  "FO": {
    "best_usd": 2,
    "best_bot": "Bot 1"
  },
  "GD": {
    "best_usd": 0.5,
    "best_bot": "Bot 1"
  },
  "AD": {
    "best_usd": 0.6,
    "best_bot": "Bot 1"
  },
  "AS": {
    "best_usd": 0.9,
    "best_bot": "Bot 1"
  },
  "BQ": {
    "best_usd": 0.75,
    "best_bot": "Bot 1"
  },
  "HR": {
    "best_usd": 0.7,
    "best_bot": "Bot 1"
  },
  "CW": {
    "best_usd": 0.65,
    "best_bot": "Bot 1"
  },
  "SR": {
    "best_usd": 0.95,
    "best_bot": "Bot 3 (New Bot)"
  },
  "QA": {
    "best_usd": 1.5,
    "best_bot": "Bot 3 (New Bot)"
  },
  "LT": {
    "best_usd": 1.5,
    "best_bot": "Bot 3 (New Bot)"
  },
  "KM": {
    "best_usd": 0.65,
    "best_bot": "Bot 2"
  },
  "KN": {
    "best_usd": 0.65,
    "best_bot": "Bot 1"
  },
  "AI": {
    "best_usd": 0.75,
    "best_bot": "Bot 1"
  },
  "AC": {
    "best_usd": 3,
    "best_bot": "Bot 1"
  },
  "AW": {
    "best_usd": 1,
    "best_bot": "Bot 1"
  },
  "MH": {
    "best_usd": 1,
    "best_bot": "Bot 1"
  },
  "KY": {
    "best_usd": 0.8,
    "best_bot": "Bot 1"
  },
  "CC": {
    "best_usd": 0.8,
    "best_bot": "Bot 1"
  },
  "BV": {
    "best_usd": 0.8,
    "best_bot": "Bot 1"
  },
  "BL": {
    "best_usd": 0.85,
    "best_bot": "Bot 1"
  },
  "DG": {
    "best_usd": 0.75,
    "best_bot": "Bot 1"
  },
  "GE": {
    "best_usd": 1.1,
    "best_bot": "Bot 1"
  },
  "GI": {
    "best_usd": 2.5,
    "best_bot": "Bot 1"
  },
  "GM": {
    "best_usd": 0.35,
    "best_bot": "Bot 1 & 2"
  },
  "IC": {
    "best_usd": 0.7,
    "best_bot": "Bot 1"
  },
  "IM": {
    "best_usd": 0.65,
    "best_bot": "Bot 1"
  },
  "LC": {
    "best_usd": 0.65,
    "best_bot": "Bot 1"
  },
  "KP": {
    "best_usd": 3,
    "best_bot": "Bot 1"
  },
  "LI": {
    "best_usd": 0.7,
    "best_bot": "Bot 1"
  },
  "MW": {
    "best_usd": 0.5,
    "best_bot": "Bot 1"
  },
  "PN": {
    "best_usd": 0.7,
    "best_bot": "Bot 1"
  },
  "SM": {
    "best_usd": 1,
    "best_bot": "Bot 1"
  },
  "SE": {
    "best_usd": 1.1,
    "best_bot": "Bot 3 (New Bot)"
  },
  "SH": {
    "best_usd": 4,
    "best_bot": "Bot 1"
  },
  "TV": {
    "best_usd": 1,
    "best_bot": "Bot 1"
  },
  "TK": {
    "best_usd": 2,
    "best_bot": "Bot 1"
  },
  "VI": {
    "best_usd": 0.3,
    "best_bot": "Bot 1"
  },
  "BT": {
    "best_usd": 1.1,
    "best_bot": "Bot 1"
  },
  "KE": {
    "best_usd": 0.35,
    "best_bot": "Bot 1"
  },
  "CK": {
    "best_usd": 5,
    "best_bot": "Bot 1"
  },
  "PS": {
    "best_usd": 1,
    "best_bot": "Bot 1"
  },
  "MC": {
    "best_usd": 1,
    "best_bot": "Bot 1 & 2"
  },
  "MT": {
    "best_usd": 1.2,
    "best_bot": "Bot 3 (New Bot)"
  },
  "BA": {
    "best_usd": 1,
    "best_bot": "Bot 3 (New Bot)"
  },
  "BB": {
    "best_usd": 0.5,
    "best_bot": "Bot 1"
  },
  "PA": {
    "best_usd": 0.8,
    "best_bot": "Bot 2"
  },
  "AM": {
    "best_usd": 0.45,
    "best_bot": "Bot 1"
  },
  "VE": {
    "best_usd": 0.95,
    "best_bot": "Bot 3 (New Bot)"
  },
  "BH": {
    "best_usd": 1.7,
    "best_bot": "Bot 3 (New Bot)"
  },
  "BZ": {
    "best_usd": 1,
    "best_bot": "Bot 3 (New Bot)"
  },
  "AZ": {
    "best_usd": 1.3,
    "best_bot": "Bot 3 (New Bot)"
  },
  "SV": {
    "best_usd": 0.7,
    "best_bot": "Bot 1"
  },
  "WF": {
    "best_usd": 1,
    "best_bot": "Bot 1"
  },
  "PE": {
    "best_usd": 0.45,
    "best_bot": "Bot 3 (New Bot)"
  },
  "LA": {
    "best_usd": 0.8,
    "best_bot": "Bot 3 (New Bot)"
  },
  "DO": {
    "best_usd": 0.6,
    "best_bot": "Bot 2"
  },
  "MO": {
    "best_usd": 1.7,
    "best_bot": "Bot 3 (New Bot)"
  },
  "LV": {
    "best_usd": 1.4,
    "best_bot": "Bot 3 (New Bot)"
  },
  "CR": {
    "best_usd": 0.55,
    "best_bot": "Bot 3 (New Bot)"
  },
  "CY": {
    "best_usd": 1,
    "best_bot": "Bot 1"
  },
  "LU": {
    "best_usd": 0.9,
    "best_bot": "Bot 1"
  },
  "MM": {
    "best_usd": 0.3,
    "best_bot": "Bot 1"
  },
  "NO": {
    "best_usd": 1.5,
    "best_bot": "Bot 3 (New Bot)"
  },
  "SK": {
    "best_usd": 1.1,
    "best_bot": "Bot 2"
  },
  "SG": {
    "best_usd": 1.5,
    "best_bot": "Bot 1"
  },
  "RW": {
    "best_usd": 0.3,
    "best_bot": "Bot 2"
  },
  "MD": {
    "best_usd": 1.35,
    "best_bot": "Bot 3 (New Bot)"
  },
  "CZ": {
    "best_usd": 0.75,
    "best_bot": "Bot 1"
  },
  "SI": {
    "best_usd": 1.3,
    "best_bot": "Bot 3 (New Bot)"
  },
  "LK": {
    "best_usd": 0.4,
    "best_bot": "Bot 1 & 2"
  },
  "NZ": {
    "best_usd": 1.2,
    "best_bot": "Bot 3 (New Bot)"
  },
  "GF": {
    "best_usd": 0.7,
    "best_bot": "Bot 3 (New Bot)"
  },
  "NE": {
    "best_usd": 0.35,
    "best_bot": "Bot 2"
  },
  "CM": {
    "best_usd": 0.1,
    "best_bot": "Bot 1"
  },
  "TG": {
    "best_usd": 0.3,
    "best_bot": "Bot 3 (New Bot)"
  },
  "UY": {
    "best_usd": 0.72,
    "best_bot": "Bot 3 (New Bot)"
  },
  "MU": {
    "best_usd": 0.3,
    "best_bot": "Bot 1"
  },
  "CF": {
    "best_usd": 0.4,
    "best_bot": "Bot 3 (New Bot)"
  },
  "FI": {
    "best_usd": 0.8,
    "best_bot": "Bot 3 (New Bot)"
  },
  "KR": {
    "best_usd": 2.5,
    "best_bot": "Bot 1"
  },
  "BO": {
    "best_usd": 1.4,
    "best_bot": "Bot 3 (New Bot)"
  },
  "BJ": {
    "best_usd": 0.3,
    "best_bot": "Bot 3 (New Bot)"
  },
  "BG": {
    "best_usd": 1.1,
    "best_bot": "Bot 3 (New Bot)"
  },
  "BI": {
    "best_usd": 0.35,
    "best_bot": "Bot 2"
  },
  "BY": {
    "best_usd": 1.8,
    "best_bot": "Bot 3 (New Bot)"
  },
  "GN": {
    "best_usd": 0.4,
    "best_bot": "Bot 1"
  },
  "ML": {
    "best_usd": 0.4,
    "best_bot": "Bot 3 (New Bot)"
  },
  "NU": {
    "best_usd": 1,
    "best_bot": "Bot 1"
  },
  "MZ": {
    "best_usd": 0.5,
    "best_bot": "Bot 2"
  },
  "RO": {
    "best_usd": 1,
    "best_bot": "Bot 3 (New Bot)"
  },
  "ZM": {
    "best_usd": 0.4,
    "best_bot": "Bot 2"
  },
  "NC": {
    "best_usd": 1,
    "best_bot": "Bot 1"
  },
  "VN": {
    "best_usd": 0.55,
    "best_bot": "Bot 1"
  },
  "NP": {
    "best_usd": 0.45,
    "best_bot": "Bot 3 (New Bot)"
  },
  "PL": {
    "best_usd": 0.6,
    "best_bot": "Bot 3 (New Bot)"
  },
  "GY": {
    "best_usd": 0.55,
    "best_bot": "Bot 1"
  },
  "NF": {
    "best_usd": 1,
    "best_bot": "Bot 1"
  },
  "EC": {
    "best_usd": 0.7,
    "best_bot": "Bot 1"
  },
  "TM": {
    "best_usd": 0.7,
    "best_bot": "Bot 3 (New Bot)"
  },
  "BM": {
    "best_usd": 0.4,
    "best_bot": "Bot 1"
  },
  "AX": {
    "best_usd": 1,
    "best_bot": "Bot 1"
  },
  "CP": {
    "best_usd": 1,
    "best_bot": "Bot 1"
  },
  "EA": {
    "best_usd": 0.7,
    "best_bot": "Bot 1"
  },
  "GH": {
    "best_usd": 0.35,
    "best_bot": "Bot 3 (New Bot)"
  },
  "GS": {
    "best_usd": 1,
    "best_bot": "Bot 1"
  },
  "EU": {
    "best_usd": 1,
    "best_bot": "Bot 1"
  },
  "HM": {
    "best_usd": 1,
    "best_bot": "Bot 1"
  },
  "MF": {
    "best_usd": 1,
    "best_bot": "Bot 1"
  },
  "MP": {
    "best_usd": 0.8,
    "best_bot": "Bot 1"
  },
  "MS": {
    "best_usd": 0.7,
    "best_bot": "Bot 1"
  },
  "PM": {
    "best_usd": 1,
    "best_bot": "Bot 1"
  },
  "PG": {
    "best_usd": 0.45,
    "best_bot": "Bot 3 (New Bot)"
  },
  "TZ": {
    "best_usd": 0.4,
    "best_bot": "Bot 3 (New Bot)"
  },
  "OM": {
    "best_usd": 1,
    "best_bot": "Bot 3 (New Bot)"
  },
  "UA": {
    "best_usd": 1.65,
    "best_bot": "Bot 3 (New Bot)"
  },
  "RS": {
    "best_usd": 0.8,
    "best_bot": "Bot 1"
  },
  "AE": {
    "best_usd": 1.6,
    "best_bot": "Bot 3 (New Bot)"
  },
  "VG": {
    "best_usd": 0.6,
    "best_bot": "Bot 1"
  },
  "ID": {
    "best_usd": 0.3,
    "best_bot": "Bot 1"
  },
  "NI": {
    "best_usd": 0.5,
    "best_bot": "Bot 2"
  },
  "AQ": {
    "best_usd": 1,
    "best_bot": "Bot 1"
  },
  "CX": {
    "best_usd": 1,
    "best_bot": "Bot 1"
  },
  "GR": {
    "best_usd": 1,
    "best_bot": "Bot 1"
  },
  "KZ": {
    "best_usd": 0.95,
    "best_bot": "Bot 1"
  },
  "RU": {
    "best_usd": 0.9,
    "best_bot": "Bot 1"
  },
  "GA": {
    "best_usd": 0.68,
    "best_bot": "Bot 3 (New Bot)"
  },
  "HU": {
    "best_usd": 1.1,
    "best_bot": "Bot 3 (New Bot)"
  },
  "MG": {
    "best_usd": 0.15,
    "best_bot": "Bot 1"
  },
  "EH": {
    "best_usd": 0.4,
    "best_bot": "Bot 1"
  },
  "SX": {
    "best_usd": 0.7,
    "best_bot": "Bot 1"
  },
  "PW": {
    "best_usd": 0.7,
    "best_bot": "Bot 1"
  },
  "VA": {
    "best_usd": 0.5,
    "best_bot": "Bot 1"
  },
  "TA": {
    "best_usd": 0.7,
    "best_bot": "Bot 1"
  },
  "SJ": {
    "best_usd": 1,
    "best_bot": "Bot 1"
  },
  "UN": {
    "best_usd": 0.7,
    "best_bot": "Bot 1"
  },
  "NG": {
    "best_usd": 0.24,
    "best_bot": "Bot 3 (New Bot)"
  },
  "TF": {
    "best_usd": 0.75,
    "best_bot": "Bot 1"
  },
  "UM": {
    "best_usd": 0.2,
    "best_bot": "Bot 1"
  },
  "ZA": {
    "best_usd": 0.1,
    "best_bot": "Bot 1"
  },
  "CH": {
    "best_usd": 1.75,
    "best_bot": "Bot 1"
  },
  "KW": {
    "best_usd": 1.4,
    "best_bot": "Bot 1"
  },
  "MQ": {
    "best_usd": 0.35,
    "best_bot": "Bot 1"
  },
  "ER": {
    "best_usd": 0.55,
    "best_bot": "Bot 2"
  },
  "IO": {
    "best_usd": 0.7,
    "best_bot": "Bot 1"
  },
  "LS": {
    "best_usd": 0.45,
    "best_bot": "Bot 3 (New Bot)"
  },
  "TC": {
    "best_usd": 0.35,
    "best_bot": "Bot 1"
  },
  "IQ": {
    "best_usd": 2.5,
    "best_bot": "Bot 3 (New Bot)"
  },
  "CO": {
    "best_usd": 0.2,
    "best_bot": "Bot 1"
  },
  "PR": {
    "best_usd": 0.4,
    "best_bot": "Bot 1 & 2"
  },
  "AU": {
    "best_usd": 1.5,
    "best_bot": "Bot 3 (New Bot)"
  },
  "TW": {
    "best_usd": 1.6,
    "best_bot": "Bot 3 (New Bot)"
  },
  "HK": {
    "best_usd": 0.65,
    "best_bot": "Bot 1"
  },
  "UG": {
    "best_usd": 0.4,
    "best_bot": "Bot 3 (New Bot)"
  },
  "CV": {
    "best_usd": 0.6,
    "best_bot": "Bot 1"
  },
  "TJ": {
    "best_usd": 0.5,
    "best_bot": "Bot 3 (New Bot)"
  },
  "PK": {
    "best_usd": 0.35,
    "best_bot": "Bot 1"
  },
  "MR": {
    "best_usd": 0.55,
    "best_bot": "Bot 3 (New Bot)"
  },
  "SZ": {
    "best_usd": 0.5,
    "best_bot": "Bot 2"
  },
  "FR": {
    "best_usd": 0.9,
    "best_bot": "Bot 3 (New Bot)"
  },
  "CI": {
    "best_usd": 0.75,
    "best_bot": "Bot 3 (New Bot)"
  },
  "IE": {
    "best_usd": 0.6,
    "best_bot": "Bot 3 (New Bot)"
  },
  "JO": {
    "best_usd": 0.85,
    "best_bot": "Bot 1"
  },
  "DE": {
    "best_usd": 1.2,
    "best_bot": "Bot 3 (New Bot)"
  },
  "IR": {
    "best_usd": 0.35,
    "best_bot": "Bot 3 (New Bot)"
  },
  "KH": {
    "best_usd": 0.8,
    "best_bot": "Bot 3 (New Bot)"
  },
  "AT": {
    "best_usd": 0.8,
    "best_bot": "Bot 3 (New Bot)"
  },
  "EE": {
    "best_usd": 0.7,
    "best_bot": "Bot 1"
  },
  "UZ": {
    "best_usd": 0.55,
    "best_bot": "Bot 1"
  },
  "AR": {
    "best_usd": 0.55,
    "best_bot": "Bot 3 (New Bot)"
  },
  "SB": {
    "best_usd": 0.6,
    "best_bot": "Bot 1"
  },
  "GB": {
    "best_usd": 0.4,
    "best_bot": "Bot 1"
  },
  "JM": {
    "best_usd": 0.4,
    "best_bot": "Bot 1"
  },
  "YE": {
    "best_usd": 0.5,
    "best_bot": "Bot 3 (New Bot)"
  },
  "ES": {
    "best_usd": 1,
    "best_bot": "Bot 3 (New Bot)"
  },
  "GP": {
    "best_usd": 0.85,
    "best_bot": "Bot 3 (New Bot)"
  },
  "TO": {
    "best_usd": 0.6,
    "best_bot": "Bot 1"
  },
  "PT": {
    "best_usd": 0.65,
    "best_bot": "Bot 1"
  },
  "SY": {
    "best_usd": 0.7,
    "best_bot": "Bot 1"
  },
  "ZW": {
    "best_usd": 0.3,
    "best_bot": "Bot 1"
  },
  "EG": {
    "best_usd": 0.42,
    "best_bot": "Bot 2"
  },
  "MX": {
    "best_usd": 0.52,
    "best_bot": "Bot 3 (New Bot)"
  },
  "MN": {
    "best_usd": 1.1,
    "best_bot": "Bot 3 (New Bot)"
  },
  "AO": {
    "best_usd": 0.3,
    "best_bot": "Bot 3 (New Bot)"
  },
  "NL": {
    "best_usd": 1.14,
    "best_bot": "Bot 3 (New Bot)"
  },
  "IL": {
    "best_usd": 0.2,
    "best_bot": "Bot 1"
  },
  "BR": {
    "best_usd": 0.4,
    "best_bot": "Bot 3 (New Bot)"
  },
  "MV": {
    "best_usd": 1,
    "best_bot": "Bot 3 (New Bot)"
  },
  "CU": {
    "best_usd": 0.45,
    "best_bot": "Bot 3 (New Bot)"
  },
  "PY": {
    "best_usd": 0.5,
    "best_bot": "Bot 1"
  },
  "SD": {
    "best_usd": 0.2,
    "best_bot": "Bot 1"
  },
  "GL": {
    "best_usd": 0.7,
    "best_bot": "Bot 1"
  },
  "CL": {
    "best_usd": 0.25,
    "best_bot": "Bot 1"
  },
  "FJ": {
    "best_usd": 0.6,
    "best_bot": "Bot 1 & 2"
  },
  "HN": {
    "best_usd": 0.5,
    "best_bot": "Bot 3 (New Bot)"
  },
  "MY": {
    "best_usd": 0.35,
    "best_bot": "Bot 1"
  },
  "CA": {
    "best_usd": 0.25,
    "best_bot": "Bot 1"
  },
  "KG": {
    "best_usd": 0.9,
    "best_bot": "Bot 1"
  },
  "JP": {
    "best_usd": 0.85,
    "best_bot": "Bot 1"
  },
  "DJ": {
    "best_usd": 0.65,
    "best_bot": "Bot 1"
  },
  "BD": {
    "best_usd": 0.2,
    "best_bot": "Bot 1"
  },
  "TR": {
    "best_usd": 0.55,
    "best_bot": "Bot 1"
  },
  "US": {
    "best_usd": 0.22,
    "best_bot": "Bot 1"
  },
  "TD": {
    "best_usd": 0.5,
    "best_bot": "Bot 3 (New Bot)"
  },
  "LB": {
    "best_usd": 0.6,
    "best_bot": "Bot 3 (New Bot)"
  },
  "ME": {
    "best_usd": 0.55,
    "best_bot": "Bot 1"
  },
  "SA": {
    "best_usd": 0.6,
    "best_bot": "Bot 1"
  },
  "GW": {
    "best_usd": 0.5,
    "best_bot": "Bot 1"
  },
  "GQ": {
    "best_usd": 0.4,
    "best_bot": "Bot 1"
  },
  "NA": {
    "best_usd": 0.4,
    "best_bot": "Bot 2"
  },
  "IN": {
    "best_usd": 0.25,
    "best_bot": "Bot 3 (New Bot)"
  },
  "BF": {
    "best_usd": 0.35,
    "best_bot": "Bot 2"
  },
  "IT": {
    "best_usd": 0.75,
    "best_bot": "Bot 3 (New Bot)"
  },
  "KI": {
    "best_usd": 0.4,
    "best_bot": "Bot 2"
  },
  "WS": {
    "best_usd": 0.35,
    "best_bot": "Bot 2"
  },
  "ST": {
    "best_usd": 0.4,
    "best_bot": "Bot 2"
  },
  "SL": {
    "best_usd": 0.2,
    "best_bot": "Bot 2"
  },
  "TT": {
    "best_usd": 0.5,
    "best_bot": "Bot 2"
  },
  "VU": {
    "best_usd": 0.4,
    "best_bot": "Bot 2"
  },
  "AF": {
    "best_usd": 0.4,
    "best_bot": "Bot 3 (New Bot)"
  },
  "MA": {
    "best_usd": 0.3,
    "best_bot": "Bot 3 (New Bot)"
  },
  "SO": {
    "best_usd": 0.35,
    "best_bot": "Bot 3 (New Bot)"
  },
  "DZ": {
    "best_usd": 0.5,
    "best_bot": "Bot 3 (New Bot)"
  },
  "HT": {
    "best_usd": 0.3,
    "best_bot": "Bot 3 (New Bot)"
  },
  "AL": {
    "best_usd": 0.7,
    "best_bot": "Bot 3 (New Bot)"
  },
  "TN": {
    "best_usd": 0.45,
    "best_bot": "Bot 3 (New Bot)"
  },
  "TL": {
    "best_usd": 0.7,
    "best_bot": "Bot 3 (New Bot)"
  }
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
    "95": "MM", "86": "CN", "62": "ID", "91": "IN", "234": "NG", "92": "PK", "232": "SL",
    "226": "BF", "254": "KE", "261": "MG", "1849": "DO", "1829": "DO", "1809": "DO",
    "263": "ZW", "63": "PH", "93": "AF", "233": "GH", "252": "SO", "244": "AO", "255": "TZ",
    "212": "MA", "229": "BJ", "227": "NE", "228": "TG", "249": "SD", "236": "CF", "977": "NP",
    "509": "HT", "260": "ZM", "264": "NA", "223": "ML", "502": "GT", "53": "CU", "20": "EG",
    "998": "UZ", "55": "BR", "268": "SZ", "972": "IL", "256": "UG", "213": "DZ", "44": "GB",
    "505": "NI", "258": "MZ", "60": "MY", "66": "TH", "218": "LY", "94": "LK", "967": "YE",
    "84": "VN", "52": "MX", "51": "PE", "235": "TD", "266": "LS", "596": "MQ", "992": "TJ",
    "54": "AR", "48": "PL", "595": "PY", "216": "TN", "211": "SS", "355": "AL", "90": "TR",
    "963": "SY", "503": "SV", "598": "UY", "852": "HK", "670": "TL", "39": "IT", "225": "CI",
    "507": "PA", "594": "GF", "961": "LB", "43": "AT", "993": "TM", "855": "KH", "374": "AM",
    "358": "FI", "299": "GL", "241": "GA", "501": "BZ", "593": "EC", "687": "NC", "960": "MV",
    "975": "BT", "590": "GP", "421": "SK", "962": "JO", "856": "LA", "995": "GE", "34": "ES",
    "387": "BA", "970": "PS", "49": "DE", "40": "RO", "968": "OM", "597": "SR", "31": "NL",
    "46": "SE", "976": "MN", "420": "CZ", "36": "HU", "32": "BE", "359": "BG", "33": "FR",
    "994": "AZ", "965": "KW", "673": "BN", "371": "LV", "61": "AU", "974": "QA", "370": "LT",
    "373": "MD", "674": "NR", "675": "PG", "386": "SI", "47": "NO", "971": "AE", "65": "SG", "375": "BY",
    "853": "MO", "886": "TW", "356": "MT", "383": "XK", "591": "BO", "58": "VE", "380": "UA",
    "41": "CH", "973": "BH", "82": "KR", "350": "GI", "682": "CK", "7": "RU", "966": "SA",
    "964": "IQ", "45": "DK", "381": "RS", "372": "EE", "351": "PT", "98": "IR", "880": "BD",
    "1": "US", "57": "CO", "56": "CL", "996": "KG", "81": "JP", "64": "NZ", "27": "ZA"
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
    conn = sqlite3.connect(DB_FILE, timeout=20)
    c = conn.cursor()
    c.execute("PRAGMA journal_mode=WAL;")
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
    conn = sqlite3.connect(DB_FILE, timeout=20)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO ledger (item_id, status, cost_usd, profit_usd, best_bot, country, timestamp)
        VALUES (?, 'bought', ?, ?, ?, ?, ?)
    ''', (str(item_id), cost_usd, expected_profit_usd, best_bot, country, time.time()))
    conn.commit()
    conn.close()

def mark_item_sold(item_id):
    conn = sqlite3.connect(DB_FILE, timeout=20)
    c = conn.cursor()
    c.execute("UPDATE ledger SET status = 'sold' WHERE item_id = ?", (str(item_id),))
    conn.commit()
    conn.close()

def mark_item_banned(item_id):
    conn = sqlite3.connect(DB_FILE, timeout=20)
    c = conn.cursor()
    c.execute("UPDATE ledger SET status = 'banned' WHERE item_id = ?", (str(item_id),))
    conn.commit()
    conn.close()

def log_manual_profit(amount_usd, note="Manual Profit"):
    conn = sqlite3.connect(DB_FILE, timeout=20)
    c = conn.cursor()
    manual_id = f"profit_{int(time.time()*1000)}"
    c.execute('''
        INSERT INTO ledger (item_id, status, cost_usd, profit_usd, best_bot, country, timestamp)
        VALUES (?, 'sold', 0.0, ?, ?, 'MANUAL', ?)
    ''', (manual_id, float(amount_usd), note, time.time()))
    conn.commit()
    conn.close()

def log_manual_loss(amount_usd, note="Manual Loss"):
    conn = sqlite3.connect(DB_FILE, timeout=20)
    c = conn.cursor()
    manual_id = f"loss_{int(time.time()*1000)}"
    c.execute('''
        INSERT INTO ledger (item_id, status, cost_usd, profit_usd, best_bot, country, timestamp)
        VALUES (?, 'banned', ?, 0.0, ?, 'MANUAL', ?)
    ''', (manual_id, float(amount_usd), note, time.time()))
    conn.commit()
    conn.close()

def get_stats_summary(min_profit_usd=0.30):
    conn = sqlite3.connect(DB_FILE, timeout=20)
    c = conn.cursor()
    c.execute("SELECT status, cost_usd, profit_usd, timestamp FROM ledger")
    rows = c.fetchall()
    conn.close()
    
    now = time.time()
    one_day_ago = now - 86400
    one_week_ago = now - (7 * 86400)
    one_month_ago = now - (30 * 86400)

    def calc_period(data_rows):
        total = len(data_rows)
        sold = sum(1 for r in data_rows if r[0] == 'sold')
        banned = sum(1 for r in data_rows if r[0] == 'banned')
        pending = sum(1 for r in data_rows if r[0] == 'bought')
        profit = sum(r[2] or 0.0 for r in data_rows if r[0] == 'sold')
        loss = sum(r[1] or 0.0 for r in data_rows if r[0] == 'banned')
        net = profit - loss
        return {
            "total": total, "sold": sold, "banned": banned, "pending": pending,
            "profit": profit, "loss": loss, "net": net
        }

    all_time = calc_period(rows)
    today = calc_period([r for r in rows if (r[3] or 0) >= one_day_ago])
    week = calc_period([r for r in rows if (r[3] or 0) >= one_week_ago])
    month = calc_period([r for r in rows if (r[3] or 0) >= one_month_ago])

    recovery_needed = 0
    if all_time["loss"] > 0 and min_profit_usd > 0:
        import math
        recovery_needed = math.ceil(all_time["loss"] / min_profit_usd)

    return {
        "all_time": all_time,
        "today": today,
        "week": week,
        "month": month,
        "recovery_needed": recovery_needed,
        # backward compatibility keys
        "total_bought": all_time["total"],
        "sold_count": all_time["sold"],
        "banned_count": all_time["banned"],
        "pending_count": all_time["pending"],
        "total_profit_usd": all_time["profit"],
        "total_loss_usd": all_time["loss"],
        "net_balance_usd": all_time["net"]
    }

def reset_db_stats():
    conn = sqlite3.connect(DB_FILE, timeout=20)
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

def parse_spamblock(spam_block_val, max_wait_hours=0):
    if spam_block_val is None or spam_block_val == "":
        return False, "غير مفحوص (مرفوض للأمان)"
    if spam_block_val is False:
        return True, "خالٍ تماماً من السبام (0% Spam Clean)"
    low = str(spam_block_val).strip().lower()
    if low in ('no', 'false', '0', '-1'):
        return True, "خالٍ تماماً من السبام (0% Spam Clean)"
    try:
        val_int = int(low)
        if val_int == -1 or val_int == 0:
            return True, "خالٍ تماماً من السبام (0% Spam Clean)"
        elif val_int > 0:
            expire_dt = datetime.fromtimestamp(val_int).strftime('%Y-%m-%d %H:%M')
            return False, f"محظور سبام حتى {expire_dt}"
        else:
            # Any negative value other than -1 (such as -3, -4) is strictly SPAM!
            return False, f"محظور سبام (كود {val_int})"
    except (ValueError, TypeError):
        pass
    return False, f"محظور سبام ({spam_block_val})"

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
def extract_item_prices(item, rub_per_usd=90.0):
    """
    Accurately extracts buy_rub and buy_usd from LZT API item object.
    LZT API returns 'rub_price' (e.g. 50, 60, 80) and 'price' (e.g. 0.59 if USD or 50 if RUB).
    """
    rub_price_raw = item.get("rub_price")
    price_raw = item.get("price")
    curr_raw = str(item.get("price_currency") or "rub").lower()

    if rub_price_raw is not None and float(rub_price_raw) > 0:
        buy_rub = float(rub_price_raw)
        if curr_raw in ("usd", "$") and price_raw is not None:
            buy_usd = float(price_raw)
        else:
            buy_usd = round(buy_rub / rub_per_usd, 2)
    else:
        raw_val = float(price_raw or 0.0)
        if curr_raw in ("usd", "$"):
            buy_usd = raw_val
            buy_rub = round(buy_usd * rub_per_usd, 2)
        else:
            buy_rub = raw_val
            buy_usd = round(buy_rub / rub_per_usd, 2)

    return buy_rub, buy_usd

# -------------------------------------------------------------------
# Send Alert Function (With Fast-Buy & Manual-Buy Buttons)
# -------------------------------------------------------------------
def extract_item_prices(item, rub_per_usd=90.0):
    """
    Accurately extracts buy_rub and buy_usd from LZT API item object.
    LZT API returns 'rub_price' (e.g. 50, 60, 80) and 'price' (e.g. 0.59 if USD or 50 if RUB).
    """
    rub_price_raw = item.get("rub_price")
    price_raw = item.get("price")
    curr_raw = str(item.get("price_currency") or "rub").lower()

    if rub_price_raw is not None and float(rub_price_raw) > 0:
        buy_rub = float(rub_price_raw)
        if curr_raw in ("usd", "$") and price_raw is not None:
            buy_usd = float(price_raw)
        else:
            buy_usd = round(buy_rub / rub_per_usd, 2)
    else:
        raw_val = float(price_raw or 0.0)
        if curr_raw in ("usd", "$"):
            buy_usd = raw_val
            buy_rub = round(buy_usd * rub_per_usd, 2)
        else:
            buy_rub = raw_val
            buy_usd = round(buy_rub / rub_per_usd, 2)

    return buy_rub, buy_usd

# -------------------------------------------------------------------
# Send Alert Function (With Fast-Buy & Manual-Buy Buttons)
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Estimate Telegram Channel / Supergroup Creation Year from ID
# -------------------------------------------------------------------

def is_telegram_group(group_obj, item):
    """
    Strictly verifies that the entity is a REAL GROUP / CHAT and NOT a Channel.
    Uses official Telegram MTProto specifications:
    - Channels have post_messages/edit_messages permissions (CHANNELS ONLY).
    - Groups have ban_users permissions and NO post_messages permission.
    """
    perms = group_obj.get("permissions") or {}
    
    # 1. MTProto Rights Check (post_messages/edit_messages exist ONLY for Channels!)
    if perms.get("post_messages") is True or perms.get("edit_messages") is True:
        return False, "قناة بث (Channel) وليست مجموعة"

    # 2. In groups, admins have ban_users / restrict_members
    if not perms.get("ban_users"):
        return False, "ليست مجموعة حقيقية (لا توجد صلاحية حظر الأعضاء)"

    # 3. Total chats check on the account
    chats_count = item.get("telegram_chats_count", 0)
    group_counters = item.get("telegram_group_counters") or {}
    chats_in_counter = group_counters.get("chats", 0)
    if chats_count == 0 and chats_in_counter == 0:
        return False, "الحساب لا يحتوي على مجموعات إطلاقاً (فقط قنوات)"

    # 4. Check title for channel keywords
    title = (group_obj.get("title") or "").lower()
    channel_keywords = ["channel", "канал", "news", "новости", "قناة"]
    if any(k in title for k in channel_keywords):
        return False, f"العنوان يشير لقناة ({title})"

    # 5. Check username if public via Telegram preview
    username = group_obj.get("username")
    if username:
        try:
            r = requests.get(f"https://t.me/{username}", timeout=3)
            if r.status_code == 200:
                text = r.text.lower()
                if "subscribers" in text or "подписчик" in text or "مشترك" in text:
                    return False, f"المعرف {username} يتبع لقناة (مشتركين) وليس مجموعة"
                if "members" in text or "участник" in text or "عضو" in text:
                    return True, "مجموعة عامة مؤكدة"
        except Exception:
            pass

    return True, "مجموعة مؤكدة"

def estimate_group_year(gid):
    """
    Calibrated estimation of Telegram supergroup/chat creation year.
    IDs created in 2019 and earlier were under 1,180,000,000.
    IDs above 1,200,000,000 were created in late 2020 and 2021+.
    """
    try:
        gid = int(gid)
    except (ValueError, TypeError):
        return None
    # Basic legacy chats (created prior to 2018)
    if gid < 500_000_000:
        return 2017
    elif gid <= 1_050_000_000:
        return 2016
    elif gid <= 1_100_000_000:
        return 2017
    elif gid <= 1_150_000_000:
        return 2018
    elif gid <= 1_180_000_000:
        return 2019
    elif gid <= 1_250_000_000:
        return 2020
    elif gid <= 1_400_000_000:
        return 2021
    elif gid <= 1_700_000_000:
        return 2022
    elif gid <= 2_100_000_000:
        return 2023
    elif gid <= 2_800_000_000:
        return 2024
    elif gid <= 3_500_000_000:
        return 2025
    else:
        return 2026

def send_telegram_group_alert(bot_token, chat_id, item, aged_groups, buy_rub, buy_usd, session_age_hours, spam_status):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    item_id = item.get("item_id")
    title = item.get("title", "بدون عنوان")
    country = item.get("telegram_country", "غير معروف")
    ccode = resolve_country_code(country, title)
    country_display = f"{country} ({ccode})" if ccode and ccode != country else country
    
    group_lines = []
    for g, est_year in aged_groups:
        g_title = g.get("title", "بدون اسم")
        g_members = g.get("participants_count", 0)
        g_id = g.get("id", "??")
        g_user = g.get("username")
        is_owner = g.get("owner", False)
        
        user_str = f"<a href='https://t.me/{g_user}'>@{g_user}</a>" if g_user else "خاصة (Private)"
        owner_str = "👑 المالك الأساسي (Owner)" if is_owner else "👮‍♂️ مشرف كامل الصلاحيات"
        
        group_lines.append(
            f"🔹 <b>اسم المجموعة:</b> {g_title}\n"
            f"   • <b>الرابط:</b> {user_str}\n"
            f"   • <b>الأعضاء:</b> {g_members} عضو\n"
            f"   • <b>الرتبة:</b> {owner_str}\n"
            f"   • <b>معرف تيليجرام:</b> <code>{g_id}</code>\n"
            f"   • <b>سنة الإنشاء المقدرة:</b> 📅 <b>{est_year} أو أقدم</b>"
        )
        
    groups_text = "\n\n".join(group_lines)
    
    text = (
        f"<b>👑 [صيد استثنائي: حساب يملك مجموعة قديمة (2019 وأقدم)!] 👑</b>\n\n"
        f"<b>📝 العنوان:</b> {title}\n"
        f"<b>💵 سعر الشراء:</b> {buy_rub:.0f} ₽ (≈ ${buy_usd:.2f} USD)\n"
        f"<b>🌍 الدولة:</b> {country_display}\n"
        f"<b>⏳ عمر الجلسة:</b> ✅ {session_age_hours:.1f} ساعة (فوق 24H)\n"
        f"<b>🔐 كلمة السر (2FA):</b> ❌ لا توجد (جاهز للدخول)\n"
        f"<b>🚫 حالة السبام:</b> {spam_status} <i>(مستثنى لحسابات المجموعات القديمة)</i>\n\n"
        f"<b>👥 تفاصيل المجموعة القديمة المكتشفة:</b>\n"
        f"{groups_text}\n\n"
        f"🔗 <a href='https://lzt.market/{item_id}/'>اضغط هنا للشراء يدوياً من الموقع</a>"
    )
    
    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "⚡ شراء فوري من رصيدي ⚡", "callback_data": f"fastbuy:{item_id}:{buy_usd:.2f}:0:AgedGroup:{ccode}"}
            ],
            [
                {"text": "🛒 تم الشراء يدوياً", "callback_data": f"buy:{item_id}:{buy_usd:.2f}:0:AgedGroup:{ccode}"},
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
            print(f"[Telegram Group Alert] Alert sent for item {item_id} with aged group!")
            return True
        else:
            print(f"[Telegram Group Alert] Failed: {r.status_code} - {r.text}")
            return False
    except Exception as e:
        print(f"[Telegram Group Alert] Error: {e}")
        return False

def send_telegram_alert(bot_token, chat_id, item, spam_status, sell_usd, best_bot, buy_rub, buy_usd, profit_usd, session_age_hours, scan_tag='Listing'):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    item_id = item.get("item_id")
    title = item.get("title", "بدون عنوان")
    country = item.get("telegram_country", "غير معروف")
    is_premium = item.get("telegram_premium", 0)
    
    ccode = resolve_country_code(country, title)
    country_display = f"{country} ({ccode})" if ccode and ccode != country else country
    
    rub_per_usd = 90.0
    sell_rub = round(sell_usd * rub_per_usd, 0)
    profit_rub = round(profit_usd * rub_per_usd, 0)
    
    # Calculate exact session age
    if session_age_hours >= 24.0:
        session_age_str = f"✅ {session_age_hours:.1f} ساعة (جلسة معتقة 24H+ جاهزة لطرد الجلسات)"
    else:
        remaining_hours = max(0.0, 24.0 - session_age_hours)
        session_age_str = f"⏳ {session_age_hours:.1f} ساعة (متبقي {remaining_hours:.1f} س لتصبح 24H)"

    # Additional features / assets
    extras = []
    if is_premium:
        prem_exp = item.get("telegram_premium_expires") or 0
        rem_days = max(0, int((prem_exp - time.time()) / 86400)) if prem_exp > time.time() else 0
        extras.append(f"💎 بريميوم نشط ({rem_days} يوم متبقٍ)")
    stars_count = item.get("telegram_stars_count", 0)
    if stars_count and int(stars_count) > 0:
        extras.append(f"🌟 {stars_count} نجوم")
    gifts_count = item.get("telegram_gifts_count", 0)
    if gifts_count and int(gifts_count) > 0:
        extras.append(f"🎁 {gifts_count} هدايا")
    
    extras_str = " | ".join(extras) if extras else "لا يوجد"
    tier_badge = " [🏆 صيد ذهبي]" if sell_usd >= 1.50 else ""

    if "IranianTurbo" in scan_tag or "Global-BargainAged" in scan_tag:
        header = f"<b>⚡ [صيد البوت الإيراني - كل الدول 🇮🇷{tier_badge}] ربح متوقع +${profit_usd:.2f} USD (+{profit_rub:.0f} ₽)</b>"
    elif "Target-Bargains" in scan_tag:
        header = f"<b>🔥 [صيدة لقطة بسعر رخيص{tier_badge}] ربح متوقع +${profit_usd:.2f} USD (+{profit_rub:.0f} ₽)</b>"
    else:
        header = f"<b>🔔 [حساب مطابق للفلاتر{tier_badge}] ربح متوقع +${profit_usd:.2f} USD (+{profit_rub:.0f} ₽)</b>"

    text = (
        f"{header}\n\n"
        f"<b>📝 العنوان:</b> {title}\n"
        f"<b>💵 سعر الشراء:</b> {buy_rub:.0f} ₽ (≈ ${buy_usd:.2f} USD)\n"
        f"<b>🌍 الدولة:</b> {country_display}\n"
        f"<b>💰 أعلى سعر بيع لبوتاتك:</b> ${sell_usd:.2f} USD (≈ {sell_rub:.0f} ₽) <i>[{best_bot}]</i>\n"
        f"<b>💚 الربح الصافي المتوقع:</b> <b>+${profit_usd:.2f} USD</b> (≈ +{profit_rub:.0f} ₽)\n"
        f"<b>⏳ عمر الجلسة (Session Age):</b> {session_age_str}\n"
        f"<b>🚫 حالة السبام:</b> {spam_status}\n"
        f"<b>✨ مميزات إضافية:</b> {extras_str}\n\n"
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
            print(f"[Telegram] Alert sent for item {item_id}.")
            return True
        else:
            print(f"[Telegram] Failed to send alert: {r.status_code} - {r.text}")
            return False
    except Exception as e:
        print(f"[Telegram] Error sending alert: {e}")
        return False

def parse_and_update_prices_from_text(text):
    sell_prices = load_sell_prices()
    updated_count = 0
    updated_sample = []
    
    lines = text.split('\n')
    for line in lines:
        line_clean = line.strip()
        if not line_clean or len(line_clean) < 3:
            continue
            
        # Extract any price float from line (e.g. 1.65, $1.65, 1.65$, 1,65$)
        m_price = re.search(r'[\$]?\s*([0-9]+[.,][0-9]{1,3})\s*(?:[\$]|USD|usd|р|руб)?', line_clean)
        if not m_price:
            continue
            
        try:
            price = float(m_price.group(1).replace(',', '.'))
        except ValueError:
            continue
            
        # Ignore unreasonable price values (e.g. 0, or year 2024, or huge numbers)
        if price <= 0.01 or price > 20.0:
            continue

        # Try to extract country code from line
        ccode = resolve_country_code(line_clean, line_clean)
        if not ccode:
            # Try searching for any 2-letter uppercase word
            words = re.findall(r'\b([A-Za-z]{2})\b', line_clean)
            for w in words:
                w_up = w.upper()
                if w_up in DEFAULT_SELL_PRICES:
                    ccode = w_up
                    break
                    
        if ccode:
            if ccode not in sell_prices:
                sell_prices[ccode] = {"best_usd": price, "best_bot": "Forwarded Bot"}
            else:
                if price > sell_prices[ccode].get("best_usd", 0):
                    sell_prices[ccode]["best_usd"] = price
                    sell_prices[ccode]["best_bot"] = "Forwarded Bot"
            updated_count += 1
            if len(updated_sample) < 5:
                updated_sample.append(f"{ccode}: ${price:.2f}")
            
    if updated_count > 0:
        try:
            with open(SELL_PRICES_FILE, "w", encoding="utf-8") as f:
                json.dump(sell_prices, f, indent=2)
        except Exception as e:
            print(f"Error saving updated prices: {e}")
            
    return updated_count, len(sell_prices), updated_sample

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

                    elif action == "quick_profit":
                        val = float(parts[1])
                        log_manual_profit(val, note="Quick Button")
                        requests.post(f"{base_url}answerCallbackQuery", json={
                            "callback_query_id": cb_id,
                            "text": f"✅ تم تسجيل ربح +${val:.2f} USD بنجاح!"
                        })
                        # Refresh stats message
                        stats = get_stats_summary(min_profit_usd)
                        w = stats["week"]
                        t = stats["today"]
                        a = stats["all_time"]
                        net_icon_w = "💚" if w["net"] >= 0 else "💔"
                        net_icon_a = "💚" if a["net"] >= 0 else "💔"
                        report = (
                            f"📊 <b>لوحة التحكم والحاسبة المالية التفاعلية (محدثة):</b>\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"🗓️ <b>أرباح وخسائر هذا الأسبوع (7 أيام):</b>\n"
                            f"  • تم الشراء: <b>{w['total']}</b> حساب\n"
                            f"  • تم البيع: <b>{w['sold']}</b> | تم الحظر: <b>{w['banned']}</b>\n"
                            f"  • الأرباح: <b>+${w['profit']:.2f} USD</b>\n"
                            f"  • الخسائر: <b>-${w['loss']:.2f} USD</b>\n"
                            f"  • {net_icon_w} <b>صافي ربح الأسبوع:</b> <b>{'+' if w['net']>=0 else ''}${w['net']:.2f} USD</b>\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"📅 <b>أرباح وخسائر اليوم (24 ساعة):</b>\n"
                            f"  • بيع: {t['sold']} | خسارة: {t['banned']} | صافي: <b>{'+' if t['net']>=0 else ''}${t['net']:.2f} USD</b>\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"👑 <b>الإجمالي الشامل منذ بداية العمل:</b>\n"
                            f"  • إجمالي الحسابات: <b>{a['total']}</b>\n"
                            f"  • إجمالي الأرباح: <b>+${a['profit']:.2f} USD</b>\n"
                            f"  • إجمالي الخسائر: <b>-${a['loss']:.2f} USD</b>\n"
                            f"  • {net_icon_a} <b>صافي الربح النهائي:</b> <b>{'+' if a['net']>=0 else ''}${a['net']:.2f} USD</b>\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                        )
                        if stats['recovery_needed'] > 0:
                            report += f"🎯 <b>حاسبة التعويض:</b> تحتاج لبيع <b>{stats['recovery_needed']} حسابات</b> جديدة بربح ${min_profit_usd:.2f} لتغطية أي خسارة سابقة تماماً! 🚀\n\n"
                        else:
                            report += f"✨ <b>أداء مالي أسطوري: لا توجد أي خسائر تحتاج لتعويض! 🎉</b>\n\n"
                        report += (
                            f"👇 <i>اضغط على الأزرار أدناه لتسجيل ربح أو خسارة فوراً:</i>\n"
                            f"💡 <i>أو اكتب مباشرة للشات: <code>ربح 0.8</code> أو <code>خسارة 0.7</code></i>"
                        )
                        requests.post(f"{base_url}editMessageText", json={
                            "chat_id": chat_id, "message_id": msg_id,
                            "text": report, "parse_mode": "HTML", "reply_markup": msg.get("reply_markup")
                        })

                    elif action == "quick_loss":
                        val = float(parts[1])
                        log_manual_loss(val, note="Quick Button")
                        requests.post(f"{base_url}answerCallbackQuery", json={
                            "callback_query_id": cb_id,
                            "text": f"💔 تم تسجيل خسارة -${val:.2f} USD وتحديث الحسابات."
                        })
                        # Refresh stats message
                        stats = get_stats_summary(min_profit_usd)
                        w = stats["week"]
                        t = stats["today"]
                        a = stats["all_time"]
                        net_icon_w = "💚" if w["net"] >= 0 else "💔"
                        net_icon_a = "💚" if a["net"] >= 0 else "💔"
                        report = (
                            f"📊 <b>لوحة التحكم والحاسبة المالية التفاعلية (محدثة):</b>\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"🗓️ <b>أرباح وخسائر هذا الأسبوع (7 أيام):</b>\n"
                            f"  • تم الشراء: <b>{w['total']}</b> حساب\n"
                            f"  • تم البيع: <b>{w['sold']}</b> | تم الحظر: <b>{w['banned']}</b>\n"
                            f"  • الأرباح: <b>+${w['profit']:.2f} USD</b>\n"
                            f"  • الخسائر: <b>-${w['loss']:.2f} USD</b>\n"
                            f"  • {net_icon_w} <b>صافي ربح الأسبوع:</b> <b>{'+' if w['net']>=0 else ''}${w['net']:.2f} USD</b>\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"📅 <b>أرباح وخسائر اليوم (24 ساعة):</b>\n"
                            f"  • بيع: {t['sold']} | خسارة: {t['banned']} | صافي: <b>{'+' if t['net']>=0 else ''}${t['net']:.2f} USD</b>\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"👑 <b>الإجمالي الشامل منذ بداية العمل:</b>\n"
                            f"  • إجمالي الحسابات: <b>{a['total']}</b>\n"
                            f"  • إجمالي الأرباح: <b>+${a['profit']:.2f} USD</b>\n"
                            f"  • إجمالي الخسائر: <b>-${a['loss']:.2f} USD</b>\n"
                            f"  • {net_icon_a} <b>صافي الربح النهائي:</b> <b>{'+' if a['net']>=0 else ''}${a['net']:.2f} USD</b>\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                        )
                        if stats['recovery_needed'] > 0:
                            report += f"🎯 <b>حاسبة التعويض:</b> تحتاج لبيع <b>{stats['recovery_needed']} حسابات</b> جديدة بربح ${min_profit_usd:.2f} لتغطية أي خسارة سابقة تماماً! 🚀\n\n"
                        else:
                            report += f"✨ <b>أداء مالي أسطوري: لا توجد أي خسائر تحتاج لتعويض! 🎉</b>\n\n"
                        report += (
                            f"👇 <i>اضغط على الأزرار أدناه لتسجيل ربح أو خسارة فوراً:</i>\n"
                            f"💡 <i>أو اكتب مباشرة للشات: <code>ربح 0.8</code> أو <code>خسارة 0.7</code></i>"
                        )
                        requests.post(f"{base_url}editMessageText", json={
                            "chat_id": chat_id, "message_id": msg_id,
                            "text": report, "parse_mode": "HTML", "reply_markup": msg.get("reply_markup")
                        })

                    elif action == "refresh_stats":
                        stats = get_stats_summary(min_profit_usd)
                        w = stats["week"]
                        t = stats["today"]
                        a = stats["all_time"]
                        net_icon_w = "💚" if w["net"] >= 0 else "💔"
                        net_icon_a = "💚" if a["net"] >= 0 else "💔"
                        report = (
                            f"📊 <b>لوحة التحكم والحاسبة المالية التفاعلية (محدثة):</b>\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"🗓️ <b>أرباح وخسائر هذا الأسبوع (7 أيام):</b>\n"
                            f"  • تم الشراء: <b>{w['total']}</b> حساب\n"
                            f"  • تم البيع: <b>{w['sold']}</b> | تم الحظر: <b>{w['banned']}</b>\n"
                            f"  • الأرباح: <b>+${w['profit']:.2f} USD</b>\n"
                            f"  • الخسائر: <b>-${w['loss']:.2f} USD</b>\n"
                            f"  • {net_icon_w} <b>صافي ربح الأسبوع:</b> <b>{'+' if w['net']>=0 else ''}${w['net']:.2f} USD</b>\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"📅 <b>أرباح وخسائر اليوم (24 ساعة):</b>\n"
                            f"  • بيع: {t['sold']} | خسارة: {t['banned']} | صافي: <b>{'+' if t['net']>=0 else ''}${t['net']:.2f} USD</b>\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"👑 <b>الإجمالي الشامل منذ بداية العمل:</b>\n"
                            f"  • إجمالي الحسابات: <b>{a['total']}</b>\n"
                            f"  • إجمالي الأرباح: <b>+${a['profit']:.2f} USD</b>\n"
                            f"  • إجمالي الخسائر: <b>-${a['loss']:.2f} USD</b>\n"
                            f"  • {net_icon_a} <b>صافي الربح النهائي:</b> <b>{'+' if a['net']>=0 else ''}${a['net']:.2f} USD</b>\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                        )
                        if stats['recovery_needed'] > 0:
                            report += f"🎯 <b>حاسبة التعويض:</b> تحتاج لبيع <b>{stats['recovery_needed']} حسابات</b> جديدة بربح ${min_profit_usd:.2f} لتغطية أي خسارة سابقة تماماً! 🚀\n\n"
                        else:
                            report += f"✨ <b>أداء مالي أسطوري: لا توجد أي خسائر تحتاج لتعويض! 🎉</b>\n\n"
                        report += (
                            f"👇 <i>اضغط على الأزرار أدناه لتسجيل ربح أو خسارة فوراً:</i>\n"
                            f"💡 <i>أو اكتب مباشرة للشات: <code>ربح 0.8</code> أو <code>خسارة 0.7</code></i>"
                        )
                        requests.post(f"{base_url}editMessageText", json={
                            "chat_id": chat_id, "message_id": msg_id,
                            "text": report, "parse_mode": "HTML", "reply_markup": msg.get("reply_markup")
                        })
                        requests.post(f"{base_url}answerCallbackQuery", json={"callback_query_id": cb_id, "text": "تم تحديث الإحصائيات!"})

                # Handle Text Messages & Forwarded Price Lists
                if "message" in update:
                    m = update["message"]
                    chat_id = m.get("chat", {}).get("id")
                    text = m.get("text", "").strip()
                    
                    if text in ("/stats", "/start", "احصائيات", "ارباحي"):
                        stats = get_stats_summary(min_profit_usd)
                        w = stats["week"]
                        t = stats["today"]
                        a = stats["all_time"]
                        
                        net_icon_w = "💚" if w["net"] >= 0 else "💔"
                        net_icon_a = "💚" if a["net"] >= 0 else "💔"

                        report = (
                            f"📊 <b>لوحة التحكم والحاسبة المالية التفاعلية:</b>\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"🗓️ <b>أرباح وخسائر هذا الأسبوع (7 أيام):</b>\n"
                            f"  • تم الشراء: <b>{w['total']}</b> حساب\n"
                            f"  • تم البيع: <b>{w['sold']}</b> | تم الحظر: <b>{w['banned']}</b>\n"
                            f"  • الأرباح: <b>+${w['profit']:.2f} USD</b>\n"
                            f"  • الخسائر: <b>-${w['loss']:.2f} USD</b>\n"
                            f"  • {net_icon_w} <b>صافي ربح الأسبوع:</b> <b>{'+' if w['net']>=0 else ''}${w['net']:.2f} USD</b>\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"📅 <b>أرباح وخسائر اليوم (24 ساعة):</b>\n"
                            f"  • بيع: {t['sold']} | خسارة: {t['banned']} | صافي: <b>{'+' if t['net']>=0 else ''}${t['net']:.2f} USD</b>\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"👑 <b>الإجمالي الشامل منذ بداية العمل:</b>\n"
                            f"  • إجمالي الحسابات: <b>{a['total']}</b>\n"
                            f"  • إجمالي الأرباح: <b>+${a['profit']:.2f} USD</b>\n"
                            f"  • إجمالي الخسائر: <b>-${a['loss']:.2f} USD</b>\n"
                            f"  • {net_icon_a} <b>صافي الربح النهائي:</b> <b>{'+' if a['net']>=0 else ''}${a['net']:.2f} USD</b>\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                        )
                        if stats['recovery_needed'] > 0:
                            report += f"🎯 <b>حاسبة التعويض:</b> تحتاج لبيع <b>{stats['recovery_needed']} حسابات</b> جديدة بربح ${min_profit_usd:.2f} لتغطية أي خسارة سابقة تماماً! 🚀\n\n"
                        else:
                            report += f"✨ <b>أداء مالي أسطوري: لا توجد أي خسائر تحتاج لتعويض! 🎉</b>\n\n"

                        report += (
                            f"👇 <i>اضغط على الأزرار أدناه لتسجيل ربح أو خسارة فوراً:</i>\n"
                            f"💡 <i>أو اكتب مباشرة للشات: <code>ربح 0.8</code> أو <code>خسارة 0.7</code></i>"
                        )
                            
                        calc_markup = {
                            "inline_keyboard": [
                                [
                                    {"text": "➕ ربح +$0.50", "callback_data": "quick_profit:0.50"},
                                    {"text": "➕ ربح +$0.80", "callback_data": "quick_profit:0.80"},
                                    {"text": "➕ ربح +$1.00", "callback_data": "quick_profit:1.00"}
                                ],
                                [
                                    {"text": "➕ ربح +$1.50", "callback_data": "quick_profit:1.50"},
                                    {"text": "➕ ربح +$2.00", "callback_data": "quick_profit:2.00"},
                                    {"text": "➕ ربح +$2.50", "callback_data": "quick_profit:2.50"}
                                ],
                                [
                                    {"text": "💔 خسارة -$0.70", "callback_data": "quick_loss:0.70"},
                                    {"text": "💔 خسارة -$0.80", "callback_data": "quick_loss:0.80"},
                                    {"text": "💔 خسارة -$1.00", "callback_data": "quick_loss:1.00"}
                                ],
                                [
                                    {"text": "🔄 تحديث الإحصائيات", "callback_data": "refresh_stats"}
                                ]
                            ]
                        }
                        requests.post(f"{base_url}sendMessage", json={
                            "chat_id": chat_id, "text": report, "parse_mode": "HTML", "reply_markup": calc_markup
                        })

                    # Handle direct text additions like: ربح 0.5 or خسارة 0.8 or +0.5 or -0.8
                    elif text.startswith(("ربح", "+", "ربحت", "profit", "Profit")):
                        m_val = re.search(r'[\d]+[.,]?[\d]*', text)
                        if m_val:
                            val = float(m_val.group(0).replace(',', '.'))
                            if 0 < val <= 500:
                                log_manual_profit(val, note="Direct Chat")
                                requests.post(f"{base_url}sendMessage", json={
                                    "chat_id": chat_id,
                                    "text": f"✅ <b>تمت إضافة ربح +${val:.2f} USD بنجاح! 💚</b>\nأرسل /stats لرؤية الحسابات المحدثة.",
                                    "parse_mode": "HTML"
                                })

                    elif text.startswith(("خسارة", "-", "خسرت", "loss", "Loss")):
                        m_val = re.search(r'[\d]+[.,]?[\d]*', text)
                        if m_val:
                            val = float(m_val.group(0).replace(',', '.'))
                            if 0 < val <= 500:
                                log_manual_loss(val, note="Direct Chat")
                                requests.post(f"{base_url}sendMessage", json={
                                    "chat_id": chat_id,
                                    "text": f"💔 <b>تم تسجيل خسارة -${val:.2f} USD وتحديث حاسبة التعويض.</b>\nأرسل /stats لرؤية الحسابات المحدثة.",
                                    "parse_mode": "HTML"
                                })
                        
                    elif text == "/reset_stats":
                        reset_db_stats()
                        requests.post(f"{base_url}sendMessage", json={"chat_id": chat_id, "text": "♻️ تم تصفير جميع الإحصائيات والسجل المالي بنجاح."})
                        
                    # Check if user sent/forwarded a price list
                    elif any(ch in text for ch in ("$", "Free:", "–", ":", "USD", "usd")) and len(text) > 20:
                        updated_cnt, total_cnt, sample = parse_and_update_prices_from_text(text)
                        if updated_cnt > 0:
                            sample_text = ", ".join(sample)
                            reply_msg = (
                                f"✅ <b>تم تحديث أسعار البيع بنجاح!</b>\n\n"
                                f"🔄 تم تحديث ومقارنة أسعار <b>{updated_cnt} دولة</b> (أمثلة: <code>{sample_text}</code>).\n"
                                f"🌍 إجمالي الدول المسجلة في قاعدة البوت الآن: <b>{total_cnt} دولة</b>.\n\n"
                                f"🚀 يتم الآن حساب أرباح كافة الصفقات والقنص الآلي بناءً على هذه الأسعار الجديدة فوراً!"
                            )
                            requests.post(f"{base_url}sendMessage", json={"chat_id": chat_id, "text": reply_msg, "parse_mode": "HTML"})

        except Exception as e:
            time.sleep(2)

# -------------------------------------------------------------------
# Helper to Process Listings for All Streams
# -------------------------------------------------------------------
# -------------------------------------------------------------------
# Process Listings (Strict Country Filtering & Real Pricing)
# -------------------------------------------------------------------
# -------------------------------------------------------------------
# Process Listings (Strict Country Filtering & Real Pricing)
# -------------------------------------------------------------------
def process_stream_items(
    items, min_profit_usd, max_price_rub, rub_per_usd,
    target_countries_set, require_session_age_24h,
    sell_prices, sent_alerts, tg_token, tg_chat_id, lzt_token,
    scan_tag="Listing", group_sniper_cfg=None
):
    if group_sniper_cfg is None:
        group_sniper_cfg = {}

    for item in items:
        item_id = str(item.get("item_id"))
        if not item_id:
            continue

        # -------------------------------------------------------------
        # 0. AGED GROUP SNIPER FILTER (2019 or older):
        # -------------------------------------------------------------
        if group_sniper_cfg.get("enabled", True):
            session_created_at = item.get("telegram_session_created_at") or 0
            now_ts = time.time()
            session_age_hours = (now_ts - session_created_at) / 3600 if session_created_at > 0 else 0
            min_grp_age = group_sniper_cfg.get("min_session_age_hours", 24.0)

            # Condition 1: Session Age >= 24 Hours
            if session_age_hours >= min_grp_age:
                # Condition 2: No 2FA password
                has_2fa = item.get("telegram_password")
                is_no_2fa = (not has_2fa) or (str(has_2fa).strip().lower() in ("", "no", "false", "none", "0"))
                if is_no_2fa:
                    admin_groups = item.get("telegram_admin_groups") or []
                    aged_groups = []
                    max_year = group_sniper_cfg.get("max_year", 2019)
                    require_owner = group_sniper_cfg.get("require_owner", True)
                    
                    for g in admin_groups:
                        # Strictly verify it is a GROUP and NOT a Channel
                        is_grp, reason = is_telegram_group(g, item)
                        if not is_grp:
                            continue
                            
                        gid = g.get("id")
                        est_year = estimate_group_year(gid)
                        if est_year and est_year <= max_year:
                            if (not require_owner) or g.get("owner", False):
                                aged_groups.append((g, est_year))
                                
                    if aged_groups:
                        buy_rub, buy_usd = extract_item_prices(item, rub_per_usd)
                        max_grp_price = group_sniper_cfg.get("max_price_rub", 200)
                        if (not max_grp_price) or buy_rub <= max_grp_price:
                            alert_key = f"group:{item_id}"
                            if alert_key not in sent_alerts and str(item_id) not in sent_alerts:
                                spam_val = item.get("telegram_spam_block")
                                spam_status = f"سبام ({spam_val})" if spam_val not in (-1, 0, None) else "✅ سليم"
                                print(f"[AGED GROUP MATCH] Item {item_id} has {len(aged_groups)} group(s) <= {max_year}!")
                                success = send_telegram_group_alert(
                                    tg_token, tg_chat_id, item, aged_groups,
                                    buy_rub, buy_usd, session_age_hours, spam_status
                                )
                                if success:
                                    sent_alerts.add(alert_key)
                                    sent_alerts.add(str(item_id))
                                    save_sent_alerts(sent_alerts)
                                    continue

        # 1. STRICT COUNTRY FILTER:
        country_raw = item.get("telegram_country", "")
        title_raw = item.get("title", "")
        ccode = resolve_country_code(country_raw, title_raw)
        
        if target_countries_set:
            is_target = False
            if ccode and ccode.upper() in target_countries_set:
                is_target = True
            elif country_raw and country_raw.upper() in target_countries_set:
                is_target = True
            elif country_raw:
                res_c = resolve_country_code(country_raw)
                if res_c and res_c.upper() in target_countries_set:
                    is_target = True
            if not is_target:
                continue  # STRICTLY SKIP non-target countries!

        # 2. ACCURATE PRICE EXTRACTION:
        buy_rub, buy_usd = extract_item_prices(item, rub_per_usd)

        # 3. Price Ceiling Filter:
        if max_price_rub and buy_rub > max_price_rub:
            continue

        # 4. Check Spam Block (Strict 0% Spam Clean, accepts -1, -3, 0):
        spam_block_val = item.get("telegram_spam_block")
        is_accepted, spam_status = parse_spamblock(spam_block_val)
        if not is_accepted:
            continue

        # 5. Session Age Calculation:
        session_created_at = item.get("telegram_session_created_at") or item.get("session_created_at") or 0
        now_ts = time.time()
        if session_created_at > 0:
            session_age_hours = (now_ts - session_created_at) / 3600
        elif item.get("daybreak") or (scan_tag and ("daybreak" in scan_tag.lower() or "aged" in scan_tag.lower() or "iranianturbo" in scan_tag.lower())):
            # Guaranteed 24H+ by LZT daybreak filter
            session_age_hours = 24.5
        else:
            session_age_hours = 0.0

        if require_session_age_24h and session_age_hours < 24.0:
            # User requires session age >= 24h.
            # Skip alerting now without marking as alerted,
            # so as soon as it crosses 24h it will be alerted!
            continue

        # 6. Check if already alerted:
        alert_key = f"{item_id}:aged" if session_age_hours >= 24.0 else f"{item_id}:fresh"
        if alert_key in sent_alerts or str(item_id) in sent_alerts:
            continue

        # 7. Real Bot Sell Price for this Country (No Fake Premium Markup!):
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

        # Skip if no selling price defined for this country
        if not sell_usd or sell_usd <= 0:
            continue

        # 8. Profit Calculation:
        expected_profit_usd = round(sell_usd - buy_usd, 2)
        if expected_profit_usd < min_profit_usd:
            continue

        # 9. Send Standard Telegram Alert:
        print(f"[{scan_tag} Match] Item {item_id} | Country: {ccode} | Buy: {buy_rub:.0f} RUB (${buy_usd:.2f}) | Sell: ${sell_usd:.2f} | Profit: +${expected_profit_usd:.2f} USD")
        success = send_telegram_alert(
            tg_token, tg_chat_id, item, spam_status, 
            sell_usd, best_bot, buy_rub, buy_usd, expected_profit_usd, session_age_hours,
            scan_tag=scan_tag
        )
        if success:
            sent_alerts.add(alert_key)
            sent_alerts.add(str(item_id))
            save_sent_alerts(sent_alerts)

# -------------------------------------------------------------------
# Lightweight Background Health Check Server (For Koyeb, Render, etc.)
# -------------------------------------------------------------------
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b"LZT Telegram Monitor is Running & Healthy!")

    def log_message(self, format, *args):
        pass

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    print(f"[System] Health check server listening on port {port}...")
    server.serve_forever()

# -------------------------------------------------------------------
# Main Monitor Loop (Dual Scanning: Newest First & Cheapest First)
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Automatic Live Price Sync from Iranian Channel (@OzvAcc1)
# -------------------------------------------------------------------
def sync_channel_prices_loop():
    """
    Periodically scrapes the Iranian Bot update channel (https://t.me/s/OzvAcc1)
    to keep sell prices and new country capacities fresh and updated in real time.
    """
    channel_url = "https://t.me/s/OzvAcc1"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    time.sleep(5)  # Start shortly after boot
    while True:
        try:
            r = requests.get(channel_url, headers=headers, timeout=15)
            if r.status_code == 200:
                blocks = re.findall(r'<div class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>', r.text, re.DOTALL)
                channel_prices = {}
                for b in blocks:
                    clean = html.unescape(re.sub(r'<[^>]+>', ' ', b))
                    # Individual capacity alerts
                    matches = re.findall(r'پیش شماره \+(\d+).*?\(([\d\.]+)\$\)', clean)
                    for prefix, p_str in matches:
                        iso = PHONE_PREFIX_TO_CODE.get(prefix)
                        if iso:
                            channel_prices[iso] = float(p_str)
                    # Full price list if present
                    if "نام کشور" in clean:
                        entries = clean.split("✅")
                        for e in entries:
                            m_code = re.search(r'\(\+(\d+)\)', e)
                            m_price = re.search(r'\(([\d\.]+)\$\)', e)
                            if m_code and m_price:
                                iso = PHONE_PREFIX_TO_CODE.get(m_code.group(1))
                                if iso:
                                    channel_prices[iso] = float(m_price.group(1))
                                    
                if channel_prices:
                    sell_prices = load_sell_prices()
                    updated = False
                    for iso, p1 in channel_prices.items():
                        if iso not in sell_prices:
                            sell_prices[iso] = {
                                "best_usd": p1,
                                "best_bot": "البوت الأول 🥇 (الإيراني)",
                                "bot1_usd": p1,
                                "bot2_usd": 0.0
                            }
                            updated = True
                        else:
                            entry = sell_prices[iso]
                            if entry.get("bot1_usd") != p1:
                                entry["bot1_usd"] = p1
                                p2 = entry.get("bot2_usd", 0.0)
                                if p1 > p2:
                                    entry["best_usd"] = p1
                                    entry["best_bot"] = "البوت الأول 🥇 (الإيراني)"
                                elif p2 > p1:
                                    entry["best_usd"] = p2
                                    entry["best_bot"] = "البوت الثاني 🥈"
                                else:
                                    entry["best_usd"] = p1
                                    entry["best_bot"] = "البوت الأول أو الثاني (متطابق)"
                                updated = True
                    if updated:
                        with open(SELL_PRICES_FILE, "w", encoding="utf-8") as f:
                            json.dump(sell_prices, f, indent=2, ensure_ascii=False)
                        print(f"[Price Sync] Automatically updated {len(channel_prices)} live prices from @OzvAcc1!")
        except Exception as e:
            print(f"[Price Sync] Background sync error: {e}")
            
        time.sleep(600)  # Check every 10 minutes

def monitor_lzt():
    init_db()
    config = load_config()
    
    lzt_token = config.get("lzt_api_token")
    tg_token = config.get("telegram_bot_token")
    tg_chat_id = config.get("telegram_chat_id")
    interval = config.get("check_interval_seconds", 3)
    filters = config.get("filters", {})
    group_sniper_cfg = config.get("group_sniper", {
        "enabled": True, "max_year": 2019, "max_price_rub": 200,
        "min_session_age_hours": 24.0, "require_no_2fa": True, "require_owner": True
    })
    
    # 16-Country Comprehensive Target List
    target_countries = filters.get("countries", [
        "UA", "IQ", "AE", "BY", "LT", "AU", "TW", "KR", "CH", "NO", "SG", "QA", "BN", "BH", "MO", "GI"
    ])
    target_countries_set = set()
    for c in target_countries:
        c_str = str(c).strip().upper()
        target_countries_set.add(c_str)
        res_code = resolve_country_code(c_str)
        if res_code:
            target_countries_set.add(res_code.upper())
            
    pmin = filters.get("pmin", 2)
    pmax = filters.get("pmax", 70)
    min_profit_usd = filters.get("min_profit_usd", 0.20)
    require_session_age_24h = filters.get("require_session_age_24h", True)
    rub_per_usd = 90.0
    
    if not lzt_token or not tg_token or not tg_chat_id:
        print("Error: Missing credentials in config.json or environment variables.")
        sys.exit(1)

    threading.Thread(target=run_health_server, daemon=True).start()
    threading.Thread(target=telegram_bot_listener, args=(tg_token, lzt_token, min_profit_usd), daemon=True).start()
    threading.Thread(target=sync_channel_prices_loop, daemon=True).start()

    sent_alerts = load_sent_alerts()
    
    print("--------------------------------------------------")
    print(f"Starting Target-Focused Dual-Scan Telegram Monitor (3s loop)...")
    print(f"Target Countries ({len(target_countries_set)}): {', '.join(sorted(target_countries_set))}")
    print(f"Price Range: {pmin} - {pmax} RUB | Min Profit: +${min_profit_usd:.2f} USD")
    print(f"Session Age: {'Require >= 24H' if require_session_age_24h else 'All Ages'}")
    print(f"Dual Scan Mode: Alternating Newest First (pdate_to_down) & Cheapest First (price_to_up)")
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
    cycle_count = 0

    api_countries = [c for c in target_countries if len(c) == 2 and c.isalpha()]

    while True:
        try:
            current_url = fallback_url if consecutive_errors >= 3 else url
            sell_prices = load_sell_prices()
            
            # 6-Stage Advanced Multi-Vector Search Engine:
            # Mode 0: Targeted Aged Stream (Target countries, daybreak=1, newest first)
            # Mode 1: Targeted Fresh Stream (Target countries, pdate_to_down, Page 1)
            # Mode 2: Targeted Bargain Hunter (Target countries, price_to_up, Page 1)
            # Mode 3: Global Group Sniper (ALL countries, <= 2019 groups, max 200 RUB)
            # Mode 4: 🌟 Global Iranian Turbo Sniper (ALL countries, daybreak=1, profit > $0.50, newest first)
            # Mode 5: 🌟 Global Bargain Aged Hunter (ALL countries, daybreak=1, profit > $0.50, cheapest first)
            global_sniper_cfg = config.get("global_profit_sniper", {
                "enabled": True, "min_profit_usd": 0.50, "require_session_age_24h": True, "pmax": 150
            })
            
            scan_mode = cycle_count % 6
            cycle_count += 1

            current_target_set = target_countries_set
            current_min_profit = min_profit_usd
            current_req_age = require_session_age_24h
            current_pmax = pmax

            if scan_mode == 0:
                sort_order = "pdate_to_down"
                scan_tag = "Target-AgedStream"
                current_req_age = True
                query_params = {
                    "pmin": pmin,
                    "pmax": pmax,
                    "currency": "rub",
                    "2fa": "no",
                    "spam": "no",
                    "allow_geo_spamblock": 0,
                    "nsb": 1,
                    "nsb_by_me": 1,
                    "daybreak": 1,
                    "session_age": 1,
                    "session_age_period": "day",
                    "page": 1,
                    "order_by": sort_order
                }
                if api_countries:
                    query_params["country[]"] = api_countries

            elif scan_mode == 1:
                sort_order = "pdate_to_down"
                scan_tag = "Target-Newest"
                query_params = {
                    "pmin": pmin,
                    "pmax": pmax,
                    "currency": "rub",
                    "2fa": "no",
                    "spam": "no",
                    "allow_geo_spamblock": 0,
                    "nsb": 1,
                    "nsb_by_me": 1,
                    "page": 1,
                    "order_by": sort_order
                }
                if api_countries:
                    query_params["country[]"] = api_countries

            elif scan_mode == 2:
                sort_order = "price_to_up"
                scan_tag = "Target-Bargains"
                query_params = {
                    "pmin": pmin,
                    "pmax": pmax,
                    "currency": "rub",
                    "2fa": "no",
                    "spam": "no",
                    "allow_geo_spamblock": 0,
                    "nsb": 1,
                    "nsb_by_me": 1,
                    "page": 1,
                    "order_by": sort_order
                }
                if api_countries:
                    query_params["country[]"] = api_countries

            elif scan_mode == 3 and group_sniper_cfg.get("enabled", True):
                sort_order = "pdate_to_down"
                scan_tag = "Global-GroupScan"
                current_target_set = None
                current_pmax = group_sniper_cfg.get("max_price_rub", 200)
                query_params = {
                    "pmin": pmin,
                    "pmax": current_pmax,
                    "currency": "rub",
                    "2fa": "no",
                    "nsb": 1,
                    "nsb_by_me": 1,
                    "page": 1,
                    "order_by": sort_order
                }

            elif scan_mode == 4:
                # 🌟 Global Iranian Bot Turbo Hunter (ANY Country, Session > 24H, Profit >= $0.50)
                sort_order = "pdate_to_down"
                scan_tag = "Global-IranianTurbo-50c"
                current_target_set = None  # SCAN ALL COUNTRIES!
                current_min_profit = global_sniper_cfg.get("min_profit_usd", 0.50)
                current_req_age = True     # SESSION AGE > 1 DAY
                current_pmax = global_sniper_cfg.get("pmax", 150)
                query_params = {
                    "pmin": pmin,
                    "pmax": current_pmax,
                    "currency": "rub",
                    "2fa": "no",
                    "spam": "no",
                    "allow_geo_spamblock": 0,
                    "daybreak": 1,
                    "session_age": 1,
                    "session_age_period": "day",
                    "nsb": 1,
                    "nsb_by_me": 1,
                    "page": 1,
                    "order_by": sort_order
                }

            else:
                # 🌟 Global Bargain Aged Hunter (Cheapest 24H+ accounts across ALL countries)
                sort_order = "price_to_up"
                scan_tag = "Global-BargainAged-50c"
                current_target_set = None  # SCAN ALL COUNTRIES!
                current_min_profit = global_sniper_cfg.get("min_profit_usd", 0.50)
                current_req_age = True     # SESSION AGE > 1 DAY
                current_pmax = global_sniper_cfg.get("pmax", 150)
                query_params = {
                    "pmin": pmin,
                    "pmax": current_pmax,
                    "currency": "rub",
                    "2fa": "no",
                    "spam": "no",
                    "allow_geo_spamblock": 0,
                    "daybreak": 1,
                    "session_age": 1,
                    "session_age_period": "day",
                    "nsb": 1,
                    "nsb_by_me": 1,
                    "page": 1,
                    "order_by": sort_order
                }

            resp = session.get(current_url, headers=headers, params=query_params, timeout=10)
            if resp.status_code == 200:
                consecutive_errors = 0
                items = resp.json().get("items") or resp.json().get("accounts") or []
                process_stream_items(
                    items, current_min_profit, current_pmax, rub_per_usd,
                    current_target_set, current_req_age,
                    sell_prices, sent_alerts, tg_token, tg_chat_id, lzt_token,
                    scan_tag=scan_tag, group_sniper_cfg=group_sniper_cfg
                )
            elif resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", 10))
                print(f"[Warning] Rate limited (429). Sleeping {retry_after}s...")
                time.sleep(retry_after)
            else:
                consecutive_errors += 1
                time.sleep(min(30, interval * 2))

        except requests.exceptions.RequestException as req_err:
            print(f"[Connection Error] {req_err}")
            consecutive_errors += 1
            time.sleep(4)
        except Exception as e:
            print(f"[Unexpected Error] {e}")
            time.sleep(interval)
            
        time.sleep(interval)

if __name__ == "__main__":
    monitor_lzt()
