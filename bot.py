import time
import json
import re
import os
import requests
from datetime import datetime

# ==========================================
#               CONFIGURATION
# ==========================================
# 1) Get your API Token from your Power SMS Panel: menu -> "CR API"
API_TOKEN   = "gLpF8WHy0Nf7bdMK3qPoQvt7qZF663KVsx0tzAlYRef"

# 2) Your panel's own address (no trailing slash)
PANEL_URL   = "http://173.208.151.95"
API_ENDPOINT = f"http://173.208.151.95/api/sms/cdr"

# 3) Your Telegram bot (create via @BotFather) and the group to post OTPs in
BOT_TOKEN   = "8513071962:AAGK_Fr3rWwXoLGRGphhoAun2c_mMfrg5FY"
GROUP_CHAT  = "-1003247504066"

# 4) Buttons shown under every OTP message (edit or remove as you like)
MAIN_CHANNEL_LINK = "https://t.me/earning_hub_official_channel"
BOT_LINK          = "https://t.me/EARNING_HUB_NUMBER_BOT"

# 5) How often to check for new OTPs (seconds)
CHECK_INTERVAL = 2

# 6) Where to remember which OTPs were already sent (so restarting the
#    script doesn't re-send old messages)
SENT_IDS_FILE = "sent_ids.json"

COUNTRY_FLAGS = {
    "AFGHANISTAN": "🇦🇫", "ALBANIA": "🇦🇱", "ALGERIA": "🇩🇿", "ANDORRA": "🇦🇩",
    "ANGOLA": "🇦🇴", "ANTIGUA AND BARBUDA": "🇦🇬", "ARGENTINA": "🇦🇷", "ARMENIA": "🇦🇲",
    "AUSTRALIA": "🇦🇺", "AUSTRIA": "🇦🇹", "AZERBAIJAN": "🇦🇿",
    "BAHAMAS": "🇧🇸", "BAHRAIN": "🇧🇭", "BANGLADESH": "🇧🇩", "BARBADOS": "🇧🇧",
    "BELARUS": "🇧🇾", "BELGIUM": "🇧🇪", "BELIZE": "🇧🇿", "BENIN": "🇧🇯",
    "BHUTAN": "🇧🇹", "BOLIVIA": "🇧🇴", "BOSNIA": "🇧🇦", "BOSNIA AND HERZEGOVINA": "🇧🇦",
    "BOTSWANA": "🇧🇼", "BRAZIL": "🇧🇷", "BRUNEI": "🇧🇳", "BULGARIA": "🇧🇬",
    "BURKINA FASO": "🇧🇫", "BURUNDI": "🇧🇮",
    "CAMBODIA": "🇰🇭", "CAMEROON": "🇨🇲", "CANADA": "🇨🇦", "CAPE VERDE": "🇨🇻",
    "CENTRAL AFRICAN REPUBLIC": "🇨🇫", "CHAD": "🇹🇩", "CHILE": "🇨🇱", "CHINA": "🇨🇳",
    "COLOMBIA": "🇨🇴", "COMOROS": "🇰🇲", "CONGO": "🇨🇬", "DR CONGO": "🇨🇩",
    "DEMOCRATIC REPUBLIC OF CONGO": "🇨🇩", "COSTA RICA": "🇨🇷", "CROATIA": "🇭🇷",
    "CUBA": "🇨🇺", "CYPRUS": "🇨🇾", "CZECH REPUBLIC": "🇨🇿", "CZECHIA": "🇨🇿",
    "IVORY COAST": "🇨🇮", "COTE D'IVOIRE": "🇨🇮",
    "DENMARK": "🇩🇰", "DJIBOUTI": "🇩🇯", "DOMINICA": "🇩🇲", "DOMINICAN REPUBLIC": "🇩🇴",
    "EAST TIMOR": "🇹🇱", "TIMOR-LESTE": "🇹🇱", "ECUADOR": "🇪🇨", "EGYPT": "🇪🇬",
    "EL SALVADOR": "🇸🇻", "EQUATORIAL GUINEA": "🇬🇶", "ERITREA": "🇪🇷", "ESTONIA": "🇪🇪",
    "ESWATINI": "🇸🇿", "SWAZILAND": "🇸🇿", "ETHIOPIA": "🇪🇹",
    "FIJI": "🇫🇯", "FINLAND": "🇫🇮", "FRANCE": "🇫🇷",
    "GABON": "🇬🇦", "GAMBIA": "🇬🇲", "GEORGIA": "🇬🇪", "GERMANY": "🇩🇪",
    "GHANA": "🇬🇭", "GREECE": "🇬🇷", "GRENADA": "🇬🇩", "GUATEMALA": "🇬🇹",
    "GUINEA": "🇬🇳", "GUINEA-BISSAU": "🇬🇼", "GUYANA": "🇬🇾",
    "HAITI": "🇭🇹", "HONDURAS": "🇭🇳", "HUNGARY": "🇭🇺",
    "ICELAND": "🇮🇸", "INDIA": "🇮🇳", "INDONESIA": "🇮🇩", "IRAN": "🇮🇷",
    "IRAQ": "🇮🇶", "IRELAND": "🇮🇪", "ISRAEL": "🇮🇱", "ITALY": "🇮🇹",
    "JAMAICA": "🇯🇲", "JAPAN": "🇯🇵", "JORDAN": "🇯🇴",
    "KAZAKHSTAN": "🇰🇿", "KENYA": "🇰🇪", "KIRIBATI": "🇰🇮", "KUWAIT": "🇰🇼",
    "KYRGYZSTAN": "🇰🇬", "NORTH KOREA": "🇰🇵", "SOUTH KOREA": "🇰🇷",
    "LAOS": "🇱🇦", "LATVIA": "🇱🇻", "LEBANON": "🇱🇧", "LESOTHO": "🇱🇸",
    "LIBERIA": "🇱🇷", "LIBYA": "🇱🇾", "LIECHTENSTEIN": "🇱🇮", "LITHUANIA": "🇱🇹",
    "LUXEMBOURG": "🇱🇺",
    "MADAGASCAR": "🇲🇬", "MALAWI": "🇲🇼", "MALAYSIA": "🇲🇾", "MALDIVES": "🇲🇻",
    "MALI": "🇲🇱", "MALTA": "🇲🇹", "MARSHALL ISLANDS": "🇲🇭", "MAURITANIA": "🇲🇷",
    "MAURITIUS": "🇲🇺", "MEXICO": "🇲🇽", "MICRONESIA": "🇫🇲", "MOLDOVA": "🇲🇩",
    "MONACO": "🇲🇨", "MONGOLIA": "🇲🇳", "MONTENEGRO": "🇲🇪", "MOROCCO": "🇲🇦",
    "MOZAMBIQUE": "🇲🇿", "MYANMAR": "🇲🇲",
    "NAMIBIA": "🇳🇦", "NAURU": "🇳🇷", "NEPAL": "🇳🇵", "NETHERLANDS": "🇳🇱",
    "NEW ZEALAND": "🇳🇿", "NICARAGUA": "🇳🇮", "NIGER": "🇳🇪", "NIGERIA": "🇳🇬",
    "NORTH MACEDONIA": "🇲🇰", "NORWAY": "🇳🇴",
    "OMAN": "🇴🇲",
    "PAKISTAN": "🇵🇰", "PALAU": "🇵🇼", "PALESTINE": "🇵🇸", "PANAMA": "🇵🇦",
    "PAPUA NEW GUINEA": "🇵🇬", "PARAGUAY": "🇵🇾", "PERU": "🇵🇪",
    "PHILIPPINES": "🇵🇭", "POLAND": "🇵🇱", "PORTUGAL": "🇵🇹",
    "QATAR": "🇶🇦",
    "ROMANIA": "🇷🇴", "RUSSIA": "🇷🇺", "RWANDA": "🇷🇼",
    "SAINT KITTS AND NEVIS": "🇰🇳", "SAINT LUCIA": "🇱🇨",
    "SAINT VINCENT AND THE GRENADINES": "🇻🇨", "SAMOA": "🇼🇸", "SAN MARINO": "🇸🇲",
    "SAO TOME AND PRINCIPE": "🇸🇹", "SAUDI ARABIA": "🇸🇦", "SENEGAL": "🇸🇳",
    "SERBIA": "🇷🇸", "SEYCHELLES": "🇸🇨", "SIERRA LEONE": "🇸🇱", "SINGAPORE": "🇸🇬",
    "SLOVAKIA": "🇸🇰", "SLOVENIA": "🇸🇮", "SOLOMON ISLANDS": "🇸🇧", "SOMALIA": "🇸🇴",
    "SOUTH AFRICA": "🇿🇦", "SOUTH SUDAN": "🇸🇸", "SPAIN": "🇪🇸", "SRI LANKA": "🇱🇰",
    "SUDAN": "🇸🇩", "SURINAME": "🇸🇷", "SWEDEN": "🇸🇪", "SWITZERLAND": "🇨🇭",
    "SYRIA": "🇸🇾",
    "TAIWAN": "🇹🇼", "TAJIKISTAN": "🇹🇯", "TANZANIA": "🇹🇿", "THAILAND": "🇹🇭",
    "TOGO": "🇹🇬", "TONGA": "🇹🇴", "TRINIDAD AND TOBAGO": "🇹🇹", "TUNISIA": "🇹🇳",
    "TURKEY": "🇹🇷", "TURKMENISTAN": "🇹🇲", "TUVALU": "🇹🇻",
    "UGANDA": "🇺🇬", "UKRAINE": "🇺🇦", "UAE": "🇦🇪", "UNITED ARAB EMIRATES": "🇦🇪",
    "UK": "🇬🇧", "UNITED KINGDOM": "🇬🇧", "USA": "🇺🇸", "UNITED STATES": "🇺🇸",
    "URUGUAY": "🇺🇾", "UZBEKISTAN": "🇺🇿",
    "VANUATU": "🇻🇺", "VATICAN": "🇻🇦", "VENEZUELA": "🇻🇪", "VIETNAM": "🇻🇳",
    "YEMEN": "🇾🇪",
    "ZAMBIA": "🇿🇲", "ZIMBABWE": "🇿🇼",
}


# ==========================================
#             HELPER FUNCTIONS
# ==========================================

def get_flag(country):
    if not country or not isinstance(country, str):
        return "🌐"
    return COUNTRY_FLAGS.get(country.upper(), "🌐")


def extract_otp(message):
    """Best-effort OTP extraction, only used to power the 'Copy OTP' button."""
    if not message:
        return None
    msg_str = str(message)
    wa_match = re.search(r'(?<!\d)(\d{3})\s*[-–—.]\s*(\d{3})(?!\d)', msg_str)
    if wa_match:
        return wa_match.group(1) + wa_match.group(2)
    matches = re.findall(r'(?<!\d)(\d{4,8})(?!\d)', msg_str)
    return matches[-1] if matches else None


def load_sent():
    if os.path.exists(SENT_IDS_FILE):
        try:
            with open(SENT_IDS_FILE) as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()


def save_sent(sent_ids):
    with open(SENT_IDS_FILE, "w") as f:
        json.dump(list(sent_ids), f)


def tg_send(chat_id, text, otp_val=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    kb = []
    if otp_val:
        kb.append([{"text": f"Copy OTP: {otp_val}", "copy_text": {"text": str(otp_val)}}])
    kb.append([
        {"text": "Main Channel ➦", "url": MAIN_CHANNEL_LINK},
        {"text": "Number Bot ➦", "url": BOT_LINK}
    ])
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": {"inline_keyboard": kb},
        "disable_web_page_preview": True
    }
    try:
        r = requests.post(url, json=payload, timeout=15)
        if r.status_code != 200:
            print(f"[TG ERROR] {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"[TG ERROR] {e}")


# ==========================================
#             FETCH FROM PANEL
# ==========================================

def fetch_new_cdr(per_page=50):
    """
    Calls the panel's own /api/sms/cdr endpoint with our API token.
    Returns a list of CDR dicts (newest first), or None on error.
    """
    params = {
        "api_token": API_TOKEN,
        "per_page": per_page,
    }
    try:
        r = requests.get(API_ENDPOINT, params=params, timeout=25)
        if r.status_code == 401:
            print("[!] Invalid API token. Check API_TOKEN in the config.")
            return None
        if r.status_code != 200:
            print(f"[HTTP] Unexpected status: {r.status_code}")
            return None
        data = r.json()
        return data.get("results", [])
    except requests.exceptions.JSONDecodeError:
        print(f"[!] Panel returned non-JSON response: {r.text[:200]}")
        return None
    except Exception as e:
        print(f"[FETCH ERROR] {e}")
        return None


# ==========================================
#                 MAIN
# ==========================================

def main():
    print("=" * 45)
    print("   POWER SMS PANEL — TELEGRAM OTP BOT")
    print("=" * 45)

    if "your_channel_here" in MAIN_CHANNEL_LINK or "your_bot_username_here" in BOT_LINK:
        print("[i] Tip: edit MAIN_CHANNEL_LINK and BOT_LINK in the config to your own links.")

    sent_ids = load_sent()
    first_run = not os.path.exists(SENT_IDS_FILE)

    if first_run:
        print("[i] First run detected — existing OTPs will be marked as")
        print("    already-seen (not sent). Only NEW OTPs from now on will")
        print("    be forwarded to Telegram.")
        rows = fetch_new_cdr()
        if rows:
            for item in rows:
                cdr_id = item.get("id")
                if cdr_id is not None:
                    sent_ids.add(cdr_id)
            save_sent(sent_ids)
        print(f"[i] Marked {len(sent_ids)} existing record(s) as seen.\n")

    while True:
        try:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Checking for new OTPs...")
            rows = fetch_new_cdr()

            if rows is None:
                print("[!] Could not reach the panel. Retrying shortly...")
                time.sleep(20)
                continue

            print(f"[*] {len(rows)} record(s) fetched.")

            count = 0
            for item in reversed(rows):
                cdr_id = item.get("id")
                if cdr_id is None or cdr_id in sent_ids:
                    continue

                number  = item.get("number") or "Unknown"
                cli     = item.get("cli") or item.get("caller_id") or "Unknown"
                message = item.get("message") or ""
                country = item.get("country")
                flag    = get_flag(country)
                country_label = (country or item.get("range_name") or "Unknown").title()

                otp = extract_otp(message)

                text = f"#{country_label} #{cli}  <code>{number}</code> {flag}\n\n{message}"
                tg_send(GROUP_CHAT, text, otp)

                sent_ids.add(cdr_id)
                count += 1
                print(f"  → Sent: {number} | OTP: {otp}")

            if count > 0:
                save_sent(sent_ids)
                print(f"[✓] {count} new OTP(s) forwarded.")
            else:
                print("[*] No new OTPs.")

            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            print("\n[*] Bot stopping...")
            save_sent(sent_ids)
            break
        except Exception as e:
            print(f"[ERROR] {e}")
            time.sleep(20)


if __name__ == "__main__":
    main()
