import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import pytz
import time
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
THAI_TZ = pytz.timezone("Asia/Bangkok")
NOTIFIED = set()

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"})

def get_events():
    url = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"
    res = requests.get(url, timeout=10)
    root = ET.fromstring(res.content)
    events = []
    for e in root.findall("event"):
        impact = e.findtext("impact", "")
        currency = e.findtext("currency", "")
        if impact != "High" or currency != "USD":
            continue
        title = e.findtext("title", "")
        date_str = e.findtext("date", "")
        forecast = e.findtext("forecast", "-")
        previous = e.findtext("previous", "-")
        try:
            dt = datetime.strptime(date_str, "%m-%d-%Y %I:%M%p")
            dt = pytz.utc.localize(dt).astimezone(THAI_TZ)
            events.append((title, dt, forecast, previous))
        except:
            continue
    return events

def check_and_notify():
    now = datetime.now(THAI_TZ)
    try:
        events = get_events()
    except Exception as ex:
        print(f"Error: {ex}")
        return
    for title, dt, forecast, previous in events:
        diff = (dt - now).total_seconds()
        key = f"{title}_{dt}"
        if 0 < diff <= 1800 and key not in NOTIFIED:
            mins = int(diff // 60)
            msg = (
                f"⚠️ <b>ข่
