"""Ekranchi Telegram bot (Vercel serverless, Flask).

Vercel > Settings > Environment Variables ga quyidagilarni qo'shing:
  BOT_TOKEN        - @BotFather dan olingan YANGI token (eskisini revoke qiling!)
  ADMIN_ID         - admin Telegram ID raqami
  WEBHOOK_SECRET   - istalgan uzun tasodifiy satr (faqat A-Z a-z 0-9 _ -)
  WEB_APP_URL      - (ixtiyoriy) market.html manzili
  ADMIN_USERNAME   - (ixtiyoriy) admin @username, mijozlar to'lov haqida shunga yozadi
  UPSTASH_REDIS_REST_URL, UPSTASH_REDIS_REST_TOKEN - doimiy baza (Vercel Marketplace > Upstash)

Webhookni ulash: https://<sayt>/api/index?ulash=1&key=<WEBHOOK_SECRET>
"""
from flask import Flask, request, jsonify
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from html import escape
import json, os, io, csv, hmac, hashlib, time, logging, requests

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("ekranchi")

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0") or 0)
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")
WEB_APP_URL = os.environ.get("WEB_APP_URL", "https://bekzodmatkarimov7770-cyber.github.io/Ekranchi-shop/market.html?v=wow_v6")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "").lstrip("@").strip()
PAYMENT_TEXT = "💬 <b>To'lov masalasida admin siz bilan o'zi bog'lanadi.</b> Savollar bo'lsa, pastdagi tugma orqali adminga yozing."

PUBLIC_URL = os.environ.get("PUBLIC_URL", "https://ekranchi-shop.vercel.app").rstrip("/")

WHOLESALE_MIN = 50          # shuncha va undan ko'p dona bo'lsa optom narx
MAX_QTY_PER_ITEM = 9999
ALLOWED_DELIVERY = {"BTS", "Taksi"}

# Vercel Marketplace Upstash integratsiyasi KV_REST_API_* nomlarini qo'shadi
REDIS_URL = (os.environ.get("UPSTASH_REDIS_REST_URL") or os.environ.get("KV_REST_API_URL") or "").rstrip("/")
REDIS_TOKEN = os.environ.get("UPSTASH_REDIS_REST_TOKEN") or os.environ.get("KV_REST_API_TOKEN") or ""

# Boshlang'ich katalog: faqat baza bo'sh bo'lsa ishlatiladi. Keyin narx va qoldiq admin paneldan boshqariladi.
SEED_CATALOG = [
    {"id": "1", "brand": "Samsung", "type": "IPS LCD", "name": "A02S / A03S / A03 / A035 / A025 / A04E / A042", "retail": 77000, "wholesale": 57000, "stock": 3818},
    {"id": "2", "brand": "Samsung", "type": "IPS LCD", "name": "A10 2019 / A105 / M10 / M105", "retail": 77000, "wholesale": 57000, "stock": 1519},
    {"id": "3", "brand": "Redmi", "type": "Incell HD+", "name": "POCO M3 / 9T", "retail": 84000, "wholesale": 62000, "stock": 1461},
    {"id": "4", "brand": "Redmi", "type": "Incell HD+", "name": "13C 4G / 13C 5G / POCO C65 / 13R / POCO M6 5G", "retail": 86000, "wholesale": 63000, "stock": 1350},
    {"id": "5", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE8 PRO", "retail": 87000, "wholesale": 64000, "stock": 1341},
    {"id": "6", "brand": "Samsung", "type": "IPS LCD", "name": "A135F / A13 4G / A13 LITE / A135 / A137 / F13 / M13", "retail": 80000, "wholesale": 59000, "stock": 1332},
    {"id": "7", "brand": "Samsung", "type": "IPS LCD", "name": "A10S 2020 / A107", "retail": 77000, "wholesale": 57000, "stock": 1205},
    {"id": "8", "brand": "Vivo", "type": "Incell HD+", "name": "Y21T / Y16 / y21 / Y15A / Y15S / Y21A / Y21e / Y21G / Y21S / Y33E / Y31S / Y32 / Y01 / Y02S", "retail": 77000, "wholesale": 57000, "stock": 1194},
    {"id": "9", "brand": "Redmi", "type": "Incell HD+", "name": "11A / POCO C55 / A11 / 12C", "retail": 84000, "wholesale": 62000, "stock": 1102},
    {"id": "10", "brand": "Redmi", "type": "Incell HD+", "name": "9 PRIME / POCO M2", "retail": 84000, "wholesale": 62000, "stock": 1075},
    {"id": "11", "brand": "Samsung", "type": "IPS LCD", "name": "A20S 2020 / A207", "retail": 80000, "wholesale": 59000, "stock": 933},
    {"id": "12", "brand": "Redmi", "type": "Incell HD+", "name": "10X / NOTE 9", "retail": 90000, "wholesale": 66000, "stock": 911},
    {"id": "13", "brand": "Samsung", "type": "IPS LCD", "name": "J4+ / J6+ / J415 / J610 / J410", "retail": 77000, "wholesale": 57000, "stock": 765},
    {"id": "14", "brand": "Redmi", "type": "Incell HD+", "name": "A1 / A1+ / A2 / A2+", "retail": 77000, "wholesale": 57000, "stock": 747},
    {"id": "15", "brand": "Samsung", "type": "IPS LCD", "name": "A13 5G / A04S / A136U / A047 / A04CORE", "retail": 79000, "wholesale": 58000, "stock": 701},
    {"id": "16", "brand": "Samsung", "type": "IPS LCD", "name": "A01CORE / A013 / A3CORE", "retail": 81000, "wholesale": 60000, "stock": 697},
    {"id": "17", "brand": "Redmi", "type": "Incell HD+", "name": "10 4G / 10-2022 / 10 prime / 10prime 2022", "retail": 92000, "wholesale": 68000, "stock": 683},
    {"id": "18", "brand": "Redmi", "type": "Incell HD+", "name": "A5 4G / A5 5G / A5 New / Poco C71", "retail": 90000, "wholesale": 66000, "stock": 628},
    {"id": "19", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "BE8 / HOT12 / Hot20i / POP6 Pro / TECNO SPARK8C / SPARK 8C / SPARK9 / SPARK 9T / SMART 6HD / Hot 12i / HOT12 PRO", "retail": 80000, "wholesale": 59000, "stock": 627},
    {"id": "20", "brand": "Redmi", "type": "Incell HD+", "name": "15C 4G", "retail": 91000, "wholesale": 67000, "stock": 627},
    {"id": "21", "brand": "Samsung", "type": "IPS LCD", "name": "A15 / M15 / M156", "retail": 90000, "wholesale": 66000, "stock": 608},
    {"id": "22", "brand": "Redmi", "type": "Incell HD+", "name": "A3 / A3X / POCO C61(yin du)", "retail": 84000, "wholesale": 62000, "stock": 574},
    {"id": "23", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "Hot11 / Spark8P / Spark8t / S18pro / S662L / vision5plus / S662LC / SPARK9PRO", "retail": 86000, "wholesale": 63000, "stock": 551},
    {"id": "24", "brand": "Samsung", "type": "IPS LCD", "name": "A04 / A045", "retail": 81000, "wholesale": 60000, "stock": 535},
    {"id": "25", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE10 5G / Note11SE / Note10T 5G / POCO M3 PRO", "retail": 92000, "wholesale": 68000, "stock": 519},
    {"id": "26", "brand": "Samsung", "type": "IPS LCD", "name": "A06 4G / A065", "retail": 86000, "wholesale": 63000, "stock": 513},
    {"id": "27", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "BD4 / SMART6 / BD4A / BD4I / BD4J / BD4H / SPARK GO2022 / POP5LTE / POP5PRO / BD4T", "retail": 79000, "wholesale": 58000, "stock": 487},
    {"id": "28", "brand": "Samsung", "type": "IPS LCD", "name": "A07 4G", "retail": 90000, "wholesale": 66000, "stock": 482},
    {"id": "29", "brand": "Redmi", "type": "Incell HD+", "name": "POCO C40 / 10 POWER / 10INDIA / 10C", "retail": 84000, "wholesale": 62000, "stock": 481},
    {"id": "30", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "HOT12 / HOT12PLAY / HOT12PLAYNFC / NOTE12I / LG7N / POVA4 / HOT20PLAY / HOT20 / LG6 / LG6N / POVANEO2 / LH6N / POVANEO3 / HOT30PLAY / 6835", "retail": 90000, "wholesale": 66000, "stock": 478},
    {"id": "31", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "S16 / Smart5 / SparkGo 2020 / Hot10lite / Vision1pro / Vision1plus", "retail": 77000, "wholesale": 57000, "stock": 469},
    {"id": "32", "brand": "Xiaomi", "type": "Incell HD+", "name": "MI 11T / MI11T PRO", "retail": 125000, "wholesale": 92000, "stock": 429},
    {"id": "33", "brand": "Realme", "type": "Incell HD+", "name": "A11X / A5 2020 / narzo 20A / A9 2020 / A31 2020 / realmeC3 / Realme5 / Realme5S / narzo10A / A8 2020 / Realme6 / Realme6i / Realme7", "retail": 77000, "wholesale": 57000, "stock": 426},
    {"id": "34", "brand": "Redmi", "type": "Incell HD+", "name": "12R / Note 13R / 12 / 13 5G / 13 / POCO M6 PRO 5G / 12 5G", "retail": 90000, "wholesale": 66000, "stock": 423},
    {"id": "35", "brand": "Samsung", "type": "IPS LCD", "name": "A01F 2020 / A015", "retail": 80000, "wholesale": 59000, "stock": 413},
    {"id": "36", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE 8", "retail": 88000, "wholesale": 65000, "stock": 409},
    {"id": "37", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "HOT50 / SPARK30 / SPARK30 4G / HOT50 4G", "retail": 102000, "wholesale": 75000, "stock": 384},
    {"id": "38", "brand": "Xiaomi", "type": "Incell HD+", "name": "MI 9T / MI9T PRO", "retail": 100000, "wholesale": 74000, "stock": 373},
    {"id": "39", "brand": "Redmi", "type": "Incell HD+", "name": "14C 4G / 14C 5G / Poco C75", "retail": 86000, "wholesale": 63000, "stock": 366},
    {"id": "40", "brand": "Samsung", "type": "IPS LCD", "name": "A2Core / A260", "retail": 72000, "wholesale": 53000, "stock": 358},
    {"id": "41", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "S17 / A58 / A58PRO 4G / A49 / A661 / A661L / S661W / SMART6+ / SPARK8", "retail": 80000, "wholesale": 59000, "stock": 353},
    {"id": "42", "brand": "Samsung", "type": "IPS LCD", "name": "A05 / A055F / M05", "retail": 83000, "wholesale": 61000, "stock": 346},
    {"id": "43", "brand": "Samsung", "type": "IPS LCD", "name": "A05S / A057", "retail": 96000, "wholesale": 71000, "stock": 345},
    {"id": "44", "brand": "Samsung", "type": "IPS LCD", "name": "M23", "retail": 88000, "wholesale": 65000, "stock": 331},
    {"id": "45", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE14 PRO 4GWF", "retail": 169000, "wholesale": 125000, "stock": 322},
    {"id": "46", "brand": "Redmi", "type": "Incell HD+", "name": "8A", "retail": 80000, "wholesale": 59000, "stock": 321},
    {"id": "47", "brand": "Xiaomi", "type": "Incell HD+", "name": "POCO X3 / X3 PRO / NOTE9 PRO 5G / MI10T LITE 5G", "retail": 96000, "wholesale": 71000, "stock": 320},
    {"id": "48", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE11 5G / NOTE 11T 5G / NOTE 11S 5G / POCO M4 PRO 5G", "retail": 114000, "wholesale": 84000, "stock": 284},
    {"id": "49", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "SMART5", "retail": 99000, "wholesale": 73000, "stock": 272},
    {"id": "50", "brand": "Redmi", "type": "Incell HD+", "name": "15 4G / 5G", "retail": 110000, "wholesale": 81000, "stock": 263},
    {"id": "51", "brand": "Oppo", "type": "Incell HD+", "name": "NARZO 50I", "retail": 96000, "wholesale": 71000, "stock": 257},
    {"id": "52", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE13PRO 4GWF", "retail": 194000, "wholesale": 143000, "stock": 256},
    {"id": "53", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "HOT40PRO / HOT40", "retail": 108000, "wholesale": 80000, "stock": 253},
    {"id": "54", "brand": "Samsung", "type": "IPS LCD", "name": "A11 2020 / A115", "retail": 103000, "wholesale": 76000, "stock": 246},
    {"id": "55", "brand": "Samsung", "type": "TFT", "name": "S10+WF", "retail": 230000, "wholesale": 170000, "stock": 246},
    {"id": "56", "brand": "Redmi", "type": "Incell HD+", "name": "6A", "retail": 94000, "wholesale": 69000, "stock": 243},
    {"id": "57", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "NOTE30I / SPARK20SPRO", "retail": 111000, "wholesale": 82000, "stock": 230},
    {"id": "58", "brand": "Vivo", "type": "Incell HD+", "name": "Y3 / Y13 / Y3S / Y11 / Y12 / Y15 / Y17 / U3X / U10 / 8A", "retail": 96000, "wholesale": 71000, "stock": 222},
    {"id": "59", "brand": "Oppo", "type": "Incell HD+", "name": "A16 / A16S / A16K / A15 / A15S / A35 / A54S / A56 4G / 5G / A55 5G", "retail": 96000, "wholesale": 71000, "stock": 221},
    {"id": "60", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "HOT11S / CH6 / CG7 / Camon17PRO / CH7 / Camon18PRO / CI8 / KI7 / LI6 / SPARK8PRO / KJ6 / KJ8", "retail": 104000, "wholesale": 77000, "stock": 219},
    {"id": "61", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "BD3 / KF6 / KF6H / KF6i / KF6J / Spark7 / PR651 / PR651H / POP5P / Smart5Pro / PR652B / Vision2S / HOT10i", "retail": 94000, "wholesale": 69000, "stock": 211},
    {"id": "62", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "KI7 / SPARK10PRO / HOT30 / POVA5 / LH7 / NOTE30 / LH7N", "retail": 106000, "wholesale": 78000, "stock": 203},
    {"id": "63", "brand": "Vivo", "type": "Incell HD+", "name": "IQ00 Z7x(m) / VIVO Y100i / VIVO Y78m / IQ00 Z7 / VIVO Y78 / IQ00 Z7X / IQ00 Z8 / IQ00 Z8x / VIVO Y77T-5G / VIVO Y78T / VIVO Y78（t1） / VIVO Y100T / VIVO Y36-4G / VIVO Y36 5G", "retail": 92000, "wholesale": 68000, "stock": 202},
    {"id": "64", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE11PRO 4GWF", "retail": 146000, "wholesale": 108000, "stock": 200},
    {"id": "65", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE13 PRO 4G", "retail": 118000, "wholesale": 87000, "stock": 198},
    {"id": "66", "brand": "Redmi", "type": "Incell HD+", "name": "Y3", "retail": 99000, "wholesale": 73000, "stock": 195},
    {"id": "67", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE 9S / NOTE9 PRO 4G / NOTE9 PROMAX / NOTE10 LITE / XM POCO M2 PRO", "retail": 95000, "wholesale": 70000, "stock": 193},
    {"id": "68", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "CD7 / CD7H / CD6 / CD6J.S / HOT9 / HOT9PRO / SPARK5 / SPARK5PRO / Camon5 / Camon 5air / Note 7lite", "retail": 96000, "wholesale": 71000, "stock": 193},
    {"id": "69", "brand": "Vivo", "type": "Incell HD+", "name": "Y20 / Y20I / Y20S / Y15A / Y15S / Y11S / Y12S / Y12A / (NEIDAN)Y30 / Y30G / Y31S / IQOOU1X / Y10-(T1 / T2) / Y02", "retail": 90000, "wholesale": 66000, "stock": 188},
    {"id": "70", "brand": "Xiaomi", "type": "Incell HD+", "name": "F3 / F4 / Mi 11i / Mi11x / Mi11x Pro / Shark 4 / 4Pro", "retail": 115000, "wholesale": 85000, "stock": 188},
    {"id": "71", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "HOT10 / CE7 / CE7J / LD7 / LD7J / SPARK6 / Pova / Note8i / Camon16 / Camon16SE", "retail": 106000, "wholesale": 78000, "stock": 186},
    {"id": "72", "brand": "Redmi", "type": "Incell HD+", "name": "7A", "retail": 92000, "wholesale": 68000, "stock": 181},
    {"id": "73", "brand": "Samsung", "type": "IPS LCD", "name": "A6 2018 / A600", "retail": 102000, "wholesale": 75000, "stock": 174},
    {"id": "74", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "NOTE11 / NOTE12", "retail": 107000, "wholesale": 79000, "stock": 174},
    {"id": "75", "brand": "Samsung", "type": "IPS LCD", "name": "A325N / A325M / A325F / M325FV / M325F", "retail": 107000, "wholesale": 79000, "stock": 174},
    {"id": "76", "brand": "Samsung", "type": "IPS LCD", "name": "A31 2020 / A315-WF", "retail": 127000, "wholesale": 94000, "stock": 168},
    {"id": "77", "brand": "Oppo", "type": "Incell HD+", "name": "A15 / A15S / A35 / V3 / A16K / Q2i / Narzo20 / Narzo30a / Rearlme 7i", "retail": 96000, "wholesale": 71000, "stock": 156},
    {"id": "78", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "SPARK6GO", "retail": 94000, "wholesale": 69000, "stock": 152},
    {"id": "79", "brand": "Xiaomi", "type": "Incell HD+", "name": "MI 8 LITE", "retail": 99000, "wholesale": 73000, "stock": 150},
    {"id": "80", "brand": "Honor", "type": "Servis", "name": "X9C WF", "retail": 503000, "wholesale": 372000, "stock": 148},
    {"id": "81", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "KF7J / SPARK7P / HOT10T / HOT10S / SMART6PLUS / VISION3+ / KF7", "retail": 102000, "wholesale": 75000, "stock": 144},
    {"id": "82", "brand": "Samsung", "type": "IPS LCD", "name": "A14 5G / A146B / A146F / A145F / A145M(BIG）", "retail": 100000, "wholesale": 74000, "stock": 144},
    {"id": "83", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "LE6 / HOT10PLAY / HOT11PLAY / POVANEO / LE6H / VOSON2+", "retail": 99000, "wholesale": 73000, "stock": 143},
    {"id": "84", "brand": "Samsung", "type": "IPS LCD", "name": "A36 / A56", "retail": 126000, "wholesale": 93000, "stock": 143},
    {"id": "85", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE14 4G WF", "retail": 138000, "wholesale": 102000, "stock": 137},
    {"id": "86", "brand": "Redmi", "type": "Incell HD+", "name": "POCO X3 GT / NOTE10PRO 5G", "retail": 110000, "wholesale": 81000, "stock": 134},
    {"id": "87", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE 6 / NOTE6 PRO", "retail": 108000, "wholesale": 80000, "stock": 131},
    {"id": "88", "brand": "Xiaomi", "type": "Incell HD+", "name": "MI 8", "retail": 141000, "wholesale": 104000, "stock": 131},
    {"id": "89", "brand": "Redmi", "type": "Incell HD+", "name": "POCO X4 GT", "retail": 126000, "wholesale": 93000, "stock": 125},
    {"id": "90", "brand": "Honor", "type": "Servis", "name": "RY X8C", "retail": 244000, "wholesale": 180000, "stock": 122},
    {"id": "91", "brand": "Samsung", "type": "OLED", "name": "A325 / A32 4G / M32 / M325 / F325 / A32LITE", "retail": 330000, "wholesale": 244000, "stock": 120},
    {"id": "92", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "KJ6 / SPARK20PRO", "retail": 111000, "wholesale": 82000, "stock": 118},
    {"id": "93", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "Note11 / Note12 5G(X671) / Note12pro 4G / 5G(X676B) / Note20 / Note12i", "retail": 110000, "wholesale": 81000, "stock": 116},
    {"id": "94", "brand": "Samsung", "type": "IPS LCD", "name": "A16-WF", "retail": 133000, "wholesale": 98000, "stock": 116},
    {"id": "95", "brand": "Vivo", "type": "Incell HD+", "name": "Y93 / Y93A / Y93T / Y91 / Y95 / U1 / Y1S", "retail": 96000, "wholesale": 71000, "stock": 114},
    {"id": "96", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE12 4G-WF", "retail": 148000, "wholesale": 109000, "stock": 114},
    {"id": "97", "brand": "Xiaomi", "type": "Incell HD+", "name": "MI 9", "retail": 169000, "wholesale": 125000, "stock": 112},
    {"id": "98", "brand": "Samsung", "type": "IPS LCD", "name": "A34 4G-WF", "retail": 157000, "wholesale": 116000, "stock": 109},
    {"id": "99", "brand": "Honor", "type": "Incell HD+", "name": "RY  X9", "retail": 119000, "wholesale": 88000, "stock": 107},
    {"id": "100", "brand": "Honor", "type": "Incell HD+", "name": "X6C WF", "retail": 169000, "wholesale": 125000, "stock": 107},
    {"id": "101", "brand": "Samsung", "type": "IPS LCD", "name": "A7 2018 / A750", "retail": 107000, "wholesale": 79000, "stock": 106},
    {"id": "102", "brand": "Huawei", "type": "Incell HD+", "name": "Y7 2019 / Y7PRO 2019", "retail": 96000, "wholesale": 71000, "stock": 105},
    {"id": "103", "brand": "Vivo", "type": "Incell HD+", "name": "Y29 4G / Y300I", "retail": 106000, "wholesale": 78000, "stock": 103},
    {"id": "104", "brand": "Samsung", "type": "IPS LCD", "name": "A12 / A02 / A125 / A127 2021 / A022 / M12", "retail": 94000, "wholesale": 69000, "stock": 102},
    {"id": "105", "brand": "Xiaomi", "type": "Incell HD+", "name": "MI 14TPRO / MI14T", "retail": 185000, "wholesale": 137000, "stock": 102},
    {"id": "106", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "KC8 / KC8S / CC7 / CC7S / KC2 / KC2J / HOT8 / HOT8LITE / CAMON12 / SPARK4", "retail": 92000, "wholesale": 68000, "stock": 101},
    {"id": "107", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "BG6 / BG7 / POP8 / KJ5 / KJ5N / SPARKGO2024 / SPARK20C / SPARK20 / SMART8 / SMARTHD / HOTE40I / SMART8PLUS / SMART8PRO / 6525B / BG6H / S24 / BG6I / NOTE40PRO5G / NOTE30VIP / NOTE20PRO", "retail": 96000, "wholesale": 71000, "stock": 99},
    {"id": "108", "brand": "Samsung", "type": "IPS LCD", "name": "A17WF", "retail": 137000, "wholesale": 101000, "stock": 99},
    {"id": "109", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "SPARK GO 2021", "retail": 99000, "wholesale": 73000, "stock": 97},
    {"id": "110", "brand": "Oppo", "type": "Incell HD+", "name": "RENO5LITE WF", "retail": 146000, "wholesale": 108000, "stock": 97},
    {"id": "111", "brand": "Vivo", "type": "Incell HD+", "name": "Y19 / Y5S / Z5I / U3 / U20", "retail": 99000, "wholesale": 73000, "stock": 96},
    {"id": "112", "brand": "Vivo", "type": "Incell HD+", "name": "s6-V1962A / y73s-V2031A / G1-V1962BA / S7 E-V2031A / S10E-V2130A / T1 4G-V2153 / y55 4G-V2154 / Y70外-V2023 / T1 4G-V2168", "retail": 102000, "wholesale": 75000, "stock": 96},
    {"id": "113", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "POVA4PRO / LG8 / LG8N", "retail": 126000, "wholesale": 93000, "stock": 95},
    {"id": "114", "brand": "Honor", "type": "Servis", "name": "X8CWF", "retail": 381000, "wholesale": 282000, "stock": 95},
    {"id": "115", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "SPARK8C / S18 / Smart6 / SPARK9T / VISON3 / S661L / S663L / Vision5", "retail": 91000, "wholesale": 67000, "stock": 93},
    {"id": "116", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE14PRO 4G", "retail": 157000, "wholesale": 116000, "stock": 93},
    {"id": "117", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "NOTE30PRO", "retail": 111000, "wholesale": 82000, "stock": 91},
    {"id": "118", "brand": "Xiaomi", "type": "Incell HD+", "name": "MI 12T PRO / MI12T", "retail": 145000, "wholesale": 107000, "stock": 91},
    {"id": "119", "brand": "Vivo", "type": "Incell HD+", "name": "Y28 4G / Y38 5G / Y37PRO / Y19S / Y29 5G / Y200+", "retail": 104000, "wholesale": 77000, "stock": 90},
    {"id": "120", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "KF8 / Spark7Pro / CG6 / CG6J / Camon17 / Camon18i", "retail": 99000, "wholesale": 73000, "stock": 89},
    {"id": "121", "brand": "Honor", "type": "Incell HD+", "name": "X6AWF", "retail": 134000, "wholesale": 99000, "stock": 89},
    {"id": "122", "brand": "Samsung", "type": "IPS LCD", "name": "A30 / A50 / A50S-WF", "retail": 125000, "wholesale": 92000, "stock": 88},
    {"id": "123", "brand": "Samsung", "type": "IPS LCD", "name": "A8 2018 / A530", "retail": 107000, "wholesale": 79000, "stock": 87},
    {"id": "124", "brand": "Samsung", "type": "IPS LCD", "name": "J3 2016 / J320 / J300", "retail": 91000, "wholesale": 67000, "stock": 86},
    {"id": "125", "brand": "Honor", "type": "Incell HD+", "name": "RY X8 WF", "retail": 180000, "wholesale": 133000, "stock": 84},
    {"id": "126", "brand": "Samsung", "type": "IPS LCD", "name": "A15WF", "retail": 127000, "wholesale": 94000, "stock": 82},
    {"id": "127", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "GT20PRO", "retail": 121000, "wholesale": 89000, "stock": 82},
    {"id": "128", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE13PRO PLUS WF", "retail": 194000, "wholesale": 143000, "stock": 81},
    {"id": "129", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "POP5LITE", "retail": 102000, "wholesale": 75000, "stock": 80},
    {"id": "130", "brand": "Vivo", "type": "Incell HD+", "name": "Y35+ / Y35M+ / Y27 4G / Y36 / Y27 5G", "retail": 106000, "wholesale": 78000, "stock": 79},
    {"id": "131", "brand": "Samsung", "type": "IPS LCD", "name": "A6+ 2018 / A605", "retail": 111000, "wholesale": 82000, "stock": 79},
    {"id": "132", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "NOTE40S", "retail": 121000, "wholesale": 89000, "stock": 77},
    {"id": "133", "brand": "Huawei", "type": "Incell HD+", "name": "Y6P / RY 9A", "retail": 102000, "wholesale": 75000, "stock": 76},
    {"id": "134", "brand": "Honor", "type": "Incell HD+", "name": "X9C SMART", "retail": 131000, "wholesale": 97000, "stock": 74},
    {"id": "135", "brand": "Realme", "type": "Incell HD+", "name": "Realme8i / Realme9i / A96 4G / Narzo50", "retail": 103000, "wholesale": 76000, "stock": 74},
    {"id": "136", "brand": "Honor", "type": "Incell HD+", "name": "RY X8B", "retail": 253000, "wholesale": 187000, "stock": 74},
    {"id": "137", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "CK7 / CK7N / CAMON20PRO", "retail": 108000, "wholesale": 80000, "stock": 73},
    {"id": "138", "brand": "Honor", "type": "Incell HD+", "name": "RY X8B WF", "retail": 299000, "wholesale": 221000, "stock": 73},
    {"id": "139", "brand": "Samsung", "type": "OLED", "name": "A315 / A31-WF", "retail": 306000, "wholesale": 226000, "stock": 73},
    {"id": "140", "brand": "Honor", "type": "Servis", "name": "X8BWF", "retail": 368000, "wholesale": 272000, "stock": 73},
    {"id": "141", "brand": "Samsung", "type": "OLED", "name": "A16 4GWF", "retail": 442000, "wholesale": 327000, "stock": 72},
    {"id": "142", "brand": "Vivo", "type": "Incell HD+", "name": "Y27S", "retail": 107000, "wholesale": 79000, "stock": 70},
    {"id": "143", "brand": "Oppo", "type": "Incell HD+", "name": "V40LITE", "retail": 134000, "wholesale": 99000, "stock": 70},
    {"id": "144", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE12 PRO-WF", "retail": 141000, "wholesale": 104000, "stock": 69},
    {"id": "145", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "POP8PRO", "retail": 104000, "wholesale": 77000, "stock": 68},
    {"id": "146", "brand": "Samsung", "type": "IPS LCD", "name": "A336 / A33-WF", "retail": 157000, "wholesale": 116000, "stock": 68},
    {"id": "147", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE11 4G / NOTE11S / M4PRO 4G / NOTE12S", "retail": 113000, "wholesale": 83000, "stock": 67},
    {"id": "148", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE8T", "retail": 96000, "wholesale": 71000, "stock": 65},
    {"id": "149", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE7 / NOTE7PRO / NOTE7PLUS / NOTE 7S", "retail": 91000, "wholesale": 67000, "stock": 64},
    {"id": "150", "brand": "Honor", "type": "Incell HD+", "name": "RY X8", "retail": 106000, "wholesale": 78000, "stock": 64},
    {"id": "151", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE8 Overseas version", "retail": 90000, "wholesale": 66000, "stock": 63},
    {"id": "152", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "Camon30 / CL7 / CL6K / CL6", "retail": 119000, "wholesale": 88000, "stock": 63},
    {"id": "153", "brand": "Oppo", "type": "Incell HD+", "name": "V40", "retail": 194000, "wholesale": 143000, "stock": 62},
    {"id": "154", "brand": "Oppo", "type": "Incell HD+", "name": "A36 / A76 / A76New", "retail": 106000, "wholesale": 78000, "stock": 61},
    {"id": "155", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE12PRO-WF", "retail": 137000, "wholesale": 101000, "stock": 61},
    {"id": "156", "brand": "Samsung", "type": "IPS LCD", "name": "A53 / A536", "retail": 114000, "wholesale": 84000, "stock": 61},
    {"id": "157", "brand": "Honor", "type": "Incell HD+", "name": "X7C WF", "retail": 158000, "wholesale": 117000, "stock": 61},
    {"id": "158", "brand": "Xiaomi", "type": "Incell HD+", "name": "MI10T / MI10T PRO", "retail": 123000, "wholesale": 91000, "stock": 61},
    {"id": "159", "brand": "Honor", "type": "Incell HD+", "name": "X9AWF", "retail": 432000, "wholesale": 320000, "stock": 61},
    {"id": "160", "brand": "Samsung", "type": "TFT", "name": "J1 2016 / J120", "retail": 91000, "wholesale": 67000, "stock": 60},
    {"id": "161", "brand": "Huawei", "type": "Incell HD+", "name": "PLAY6TPRO / PLAY7TPRO", "retail": 150000, "wholesale": 111000, "stock": 60},
    {"id": "162", "brand": "Samsung", "type": "OLED", "name": "A15 / A155 / A156-WF", "retail": 403000, "wholesale": 298000, "stock": 60},
    {"id": "163", "brand": "Honor", "type": "Servis", "name": "X9D WF", "retail": 451000, "wholesale": 334000, "stock": 60},
    {"id": "164", "brand": "Honor", "type": "Servis", "name": "X9B WF", "retail": 499000, "wholesale": 369000, "stock": 60},
    {"id": "165", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "CAMON15 / 15AIR", "retail": 102000, "wholesale": 75000, "stock": 59},
    {"id": "166", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "ZERO40", "retail": 141000, "wholesale": 104000, "stock": 59},
    {"id": "167", "brand": "Vivo", "type": "Incell HD+", "name": "Y02 / Y02T / Y02A / Y11-2023", "retail": 94000, "wholesale": 69000, "stock": 58},
    {"id": "168", "brand": "Samsung", "type": "IPS LCD", "name": "A20 / A205", "retail": 99000, "wholesale": 73000, "stock": 58},
    {"id": "169", "brand": "Realme", "type": "Incell HD+", "name": "realme C31", "retail": 99000, "wholesale": 73000, "stock": 58},
    {"id": "170", "brand": "Samsung", "type": "OLED", "name": "A515 / A51-WF", "retail": 353000, "wholesale": 261000, "stock": 58},
    {"id": "171", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "CC6 / KC3 / CAMON12AIR / S5 / S5LITE", "retail": 98000, "wholesale": 72000, "stock": 57},
    {"id": "172", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE11 4G-WF", "retail": 137000, "wholesale": 101000, "stock": 57},
    {"id": "173", "brand": "Samsung", "type": "IPS LCD", "name": "J3Prime / J327", "retail": 108000, "wholesale": 80000, "stock": 56},
    {"id": "174", "brand": "Realme", "type": "Incell HD+", "name": "REALME5PRO / REALME Q", "retail": 108000, "wholesale": 80000, "stock": 56},
    {"id": "175", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "NOTE40PRO 4G", "retail": 141000, "wholesale": 104000, "stock": 56},
    {"id": "176", "brand": "Samsung", "type": "TFT", "name": "S20 4GWF", "retail": 246000, "wholesale": 182000, "stock": 56},
    {"id": "177", "brand": "Honor", "type": "Incell HD+", "name": "RY 10LITE(2018)", "retail": 104000, "wholesale": 77000, "stock": 55},
    {"id": "178", "brand": "Samsung", "type": "IPS LCD", "name": "A26WF", "retail": 176000, "wholesale": 130000, "stock": 55},
    {"id": "179", "brand": "Samsung", "type": "IPS LCD", "name": "A36WF", "retail": 184000, "wholesale": 136000, "stock": 55},
    {"id": "180", "brand": "Samsung", "type": "IPS LCD", "name": "A20 2019 / A205-WF", "retail": 114000, "wholesale": 84000, "stock": 55},
    {"id": "181", "brand": "Oppo", "type": "Incell HD+", "name": "NARZO50IPRIME", "retail": 96000, "wholesale": 71000, "stock": 52},
    {"id": "182", "brand": "Oppo", "type": "Incell HD+", "name": "V20E", "retail": 106000, "wholesale": 78000, "stock": 52},
    {"id": "183", "brand": "Redmi", "type": "Incell HD+", "name": "HM5", "retail": 100000, "wholesale": 74000, "stock": 50},
    {"id": "184", "brand": "Samsung", "type": "IPS LCD", "name": "A30S 2020 / A307", "retail": 99000, "wholesale": 73000, "stock": 50},
    {"id": "185", "brand": "Honor", "type": "Servis", "name": "RY X7A", "retail": 104000, "wholesale": 77000, "stock": 50},
    {"id": "186", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "POVA NEO6", "retail": 110000, "wholesale": 81000, "stock": 50},
    {"id": "187", "brand": "Realme", "type": "Incell HD+", "name": "A60 4G / Realme C65 4G / Realme C65 5G / Realme Narzo N65 / Realme 12X 5G / Realme 14X 5G / Realme C75x / OPPO A3 Pro / Realme V60 / Realme V60s / OPPO K12x 5G / OPPO A3X 4G / OPPO A3X 5G / OPPO A35G", "retail": 114000, "wholesale": 84000, "stock": 50},
    {"id": "188", "brand": "Huawei", "type": "Incell HD+", "name": "NOVA10 SE / NOVA11SE / NOVA12SE", "retail": 200000, "wholesale": 148000, "stock": 50},
    {"id": "189", "brand": "Honor", "type": "Servis", "name": "X9A WF", "retail": 442000, "wholesale": 327000, "stock": 50},
    {"id": "190", "brand": "Realme", "type": "Incell HD+", "name": "N61 / N63 / Realme note60", "retail": 103000, "wholesale": 76000, "stock": 49},
    {"id": "191", "brand": "Realme", "type": "Incell HD+", "name": "REALME12X 5G / REALME12 5G / NARZO70X 5G", "retail": 108000, "wholesale": 80000, "stock": 49},
    {"id": "192", "brand": "Samsung", "type": "IPS LCD", "name": "M53", "retail": 135000, "wholesale": 100000, "stock": 49},
    {"id": "193", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "SPARK GO 2", "retail": 107000, "wholesale": 79000, "stock": 47},
    {"id": "194", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "ZEROX NEO", "retail": 114000, "wholesale": 84000, "stock": 47},
    {"id": "195", "brand": "Oppo", "type": "Incell HD+", "name": "A57 WF", "retail": 131000, "wholesale": 97000, "stock": 47},
    {"id": "196", "brand": "Oppo", "type": "Incell HD+", "name": "F19PROWF", "retail": 134000, "wholesale": 99000, "stock": 47},
    {"id": "197", "brand": "iPhone", "type": "Incell HD+", "name": "XR-FHD", "retail": 202000, "wholesale": 149000, "stock": 47},
    {"id": "198", "brand": "Samsung", "type": "IPS LCD", "name": "A52WF", "retail": 158000, "wholesale": 117000, "stock": 47},
    {"id": "199", "brand": "iPhone", "type": "Servis", "name": "XS-F(Q-X)", "retail": 503000, "wholesale": 372000, "stock": 47},
    {"id": "200", "brand": "Samsung", "type": "IPS LCD", "name": "J2Core / J260", "retail": 91000, "wholesale": 67000, "stock": 45},
    {"id": "201", "brand": "iPhone", "type": "Incell HD+", "name": "XR", "retail": 118000, "wholesale": 87000, "stock": 45},
    {"id": "202", "brand": "iPhone", "type": "Incell HD+", "name": "XS", "retail": 125000, "wholesale": 92000, "stock": 45},
    {"id": "203", "brand": "iPhone", "type": "Incell HD+", "name": "X", "retail": 125000, "wholesale": 92000, "stock": 45},
    {"id": "204", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE14 4G", "retail": 115000, "wholesale": 85000, "stock": 45},
    {"id": "205", "brand": "Samsung", "type": "IPS LCD", "name": "A35WF", "retail": 172000, "wholesale": 127000, "stock": 45},
    {"id": "206", "brand": "Samsung", "type": "IPS LCD", "name": "A24-4G / Galaxy A25 5G / Galaxy M34 5G / A26-Galaxy F34 5G", "retail": 110000, "wholesale": 81000, "stock": 45},
    {"id": "207", "brand": "Honor", "type": "Incell HD+", "name": "X8A / X8 2023", "retail": 113000, "wholesale": 83000, "stock": 45},
    {"id": "208", "brand": "Samsung", "type": "TFT", "name": "NOTE8WF", "retail": 285000, "wholesale": 211000, "stock": 45},
    {"id": "209", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "KM5 / SPARK GO1 / A80(A671L)", "retail": 102000, "wholesale": 75000, "stock": 44},
    {"id": "210", "brand": "Realme", "type": "Incell HD+", "name": "A7 / A5S / A7n / AX5S / A12 / Realme3 / Realme3i", "retail": 94000, "wholesale": 69000, "stock": 44},
    {"id": "211", "brand": "Realme", "type": "Incell HD+", "name": "REALME12X 5G / REALME12 5G / NARZO70X 5G", "retail": 118000, "wholesale": 87000, "stock": 44},
    {"id": "212", "brand": "Realme", "type": "Incell HD+", "name": "A5 / A3S / Realme2 / A5低 / A12e / AX5 / RealmeC1", "retail": 100000, "wholesale": 74000, "stock": 43},
    {"id": "213", "brand": "iPhone", "type": "Incell HD+", "name": "15PRO", "retail": 189000, "wholesale": 140000, "stock": 43},
    {"id": "214", "brand": "Oppo", "type": "Incell HD+", "name": "A77 / A78WF", "retail": 138000, "wholesale": 102000, "stock": 42},
    {"id": "215", "brand": "Samsung", "type": "IPS LCD", "name": "A14 4G / A145P / A145B", "retail": 91000, "wholesale": 67000, "stock": 41},
    {"id": "216", "brand": "iPhone", "type": "Incell HD+", "name": "13PROMAX", "retail": 200000, "wholesale": 148000, "stock": 41},
    {"id": "217", "brand": "Samsung", "type": "TFT", "name": "NOTE9WF", "retail": 285000, "wholesale": 211000, "stock": 41},
    {"id": "218", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "SPARK30PRO / HOT50PRO / S25 / S685LN", "retail": 117000, "wholesale": 86000, "stock": 40},
    {"id": "219", "brand": "Realme", "type": "Incell HD+", "name": "realme9 pro plus / realme9 4g / reno7 / oneplus nord ce 2 5G / reno 8t / REALME10 4G", "retail": 113000, "wholesale": 83000, "stock": 40},
    {"id": "220", "brand": "iPhone", "type": "Incell HD+", "name": "11PROMAX", "retail": 146000, "wholesale": 108000, "stock": 40},
    {"id": "221", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "SPARK5AIR / LC7 / LC7S / LC8 / SPARK6AIR / POUVOIR4 / POUVOIR4PRO / SPARKPOWER2", "retail": 104000, "wholesale": 77000, "stock": 40},
    {"id": "222", "brand": "Samsung", "type": "TFT", "name": "S10WF", "retail": 230000, "wholesale": 170000, "stock": 40},
    {"id": "223", "brand": "iPhone", "type": "Servis", "name": "X-F(Q)", "retail": 489000, "wholesale": 362000, "stock": 40},
    {"id": "224", "brand": "Samsung", "type": "TFT", "name": "NOTE10+WF", "retail": 314000, "wholesale": 232000, "stock": 40},
    {"id": "225", "brand": "Samsung", "type": "TFT", "name": "S23U(USA version)WF", "retail": 319000, "wholesale": 236000, "stock": 40},
    {"id": "226", "brand": "Samsung", "type": "TFT", "name": "NOTE10-WF", "retail": 327000, "wholesale": 242000, "stock": 40},
    {"id": "227", "brand": "Realme", "type": "Incell HD+", "name": "A60 4G / Realme C65 4G / Realme C65 5G / Realme Narzo N65 / Realme 12X 5G / Realme 14X 5G / Realme C75x / OPPO A3 Pro / Realme V60 / Realme V60s / OPPO K12x 5G / OPPO A3X 4G / OPPO A3X 5G / OPPO A3 5G", "retail": 107000, "wholesale": 79000, "stock": 39},
    {"id": "228", "brand": "Samsung", "type": "IPS LCD", "name": "A35 / A55 4G WF", "retail": 195000, "wholesale": 144000, "stock": 39},
    {"id": "229", "brand": "Samsung", "type": "TFT", "name": "S21UWF", "retail": 264000, "wholesale": 195000, "stock": 39},
    {"id": "230", "brand": "Samsung", "type": "IPS LCD", "name": "A52 / A525 A52 4G-WF", "retail": 158000, "wholesale": 117000, "stock": 39},
    {"id": "231", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "Smart 6 HD / Hot 12i / Smart 6HD 2022 / hot20i", "retail": 99000, "wholesale": 73000, "stock": 38},
    {"id": "232", "brand": "Vivo", "type": "Incell HD+", "name": "Y04 / Y19E / Y29E / Y29S", "retail": 104000, "wholesale": 77000, "stock": 38},
    {"id": "233", "brand": "Huawei", "type": "Incell HD+", "name": "RY X10 LITE / Y7A / PSMART 2021", "retail": 110000, "wholesale": 81000, "stock": 38},
    {"id": "234", "brand": "Realme", "type": "Incell HD+", "name": "Realme8i-5G／A96／K10／narzo50／Realme9i / OPPO A36 / A76 / Realme9pro／K9S / reaimeQ3S／realmeQ3T／Realme v25／realmeQ5／1＋CE2lite / 1+ACE", "retail": 119000, "wholesale": 88000, "stock": 38},
    {"id": "235", "brand": "Samsung", "type": "IPS LCD", "name": "M52 / M53 / M54", "retail": 121000, "wholesale": 89000, "stock": 38},
    {"id": "236", "brand": "Samsung", "type": "IPS LCD", "name": "A22 5G(2021) / A226", "retail": 96000, "wholesale": 71000, "stock": 37},
    {"id": "237", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "POVA6NEO", "retail": 107000, "wholesale": 79000, "stock": 37},
    {"id": "238", "brand": "Huawei", "type": "Incell HD+", "name": "PSMART 2021 / Y7A / RY X10 LITE", "retail": 103000, "wholesale": 76000, "stock": 37},
    {"id": "239", "brand": "iPhone", "type": "Incell HD+", "name": "11", "retail": 121000, "wholesale": 89000, "stock": 37},
    {"id": "240", "brand": "Samsung", "type": "IPS LCD", "name": "A73-WF", "retail": 171000, "wholesale": 126000, "stock": 37},
    {"id": "241", "brand": "Samsung", "type": "TFT", "name": "S8+WF", "retail": 223000, "wholesale": 165000, "stock": 37},
    {"id": "242", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "CI6 / CI7N / CI8N / CAMON19 / CI8 / CI7 / CAMON19PRO", "retail": 108000, "wholesale": 80000, "stock": 36},
    {"id": "243", "brand": "Samsung", "type": "IPS LCD", "name": "A54 5G / A546 WF", "retail": 172000, "wholesale": 127000, "stock": 36},
    {"id": "244", "brand": "Samsung", "type": "IPS LCD", "name": "A315G / A315N / A315F", "retail": 104000, "wholesale": 77000, "stock": 35},
    {"id": "245", "brand": "Samsung", "type": "IPS LCD", "name": "A40 2020 / A405-WF", "retail": 157000, "wholesale": 116000, "stock": 35},
    {"id": "246", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE10 4G-WF", "retail": 133000, "wholesale": 98000, "stock": 35},
    {"id": "247", "brand": "Samsung", "type": "OLED", "name": "A30 / A50 / A50S-WF", "retail": 308000, "wholesale": 228000, "stock": 35},
    {"id": "248", "brand": "Oppo", "type": "Incell HD+", "name": "A3 / F7", "retail": 102000, "wholesale": 75000, "stock": 34},
    {"id": "249", "brand": "iPhone", "type": "Incell HD+", "name": "13PRO", "retail": 173000, "wholesale": 128000, "stock": 34},
    {"id": "250", "brand": "Honor", "type": "Incell HD+", "name": "RY Y72 / Y72S", "retail": 100000, "wholesale": 74000, "stock": 33},
    {"id": "251", "brand": "Huawei", "type": "Incell HD+", "name": "NOVA Y90", "retail": 113000, "wholesale": 83000, "stock": 33},
    {"id": "252", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "ZERO304G / 5G", "retail": 141000, "wholesale": 104000, "stock": 33},
    {"id": "253", "brand": "iPhone", "type": "Servis", "name": "11-F(Q)", "retail": 225000, "wholesale": 166000, "stock": 33},
    {"id": "254", "brand": "Realme", "type": "Incell HD+", "name": "Reno8 5G / Reno7 Se 5G / Find X5 Lite / realme 10 / F21 PRO / F21s PRO / Realme Narzo 60 5G / realme 9 4G / Reno8 T / Realme Narzo 50 Pro 5G / Reno8 / 11 / OPPO A78 / Reno7 A / Reno7 4", "retail": 98000, "wholesale": 72000, "stock": 32},
    {"id": "255", "brand": "Redmi", "type": "Incell HD+", "name": "HM 5", "retail": 102000, "wholesale": 75000, "stock": 32},
    {"id": "256", "brand": "Xiaomi", "type": "Incell HD+", "name": "MI 11 LITE 4G / 5G", "retail": 114000, "wholesale": 84000, "stock": 32},
    {"id": "257", "brand": "Redmi", "type": "Incell HD+", "name": "A2 LITE / 6PRO", "retail": 110000, "wholesale": 81000, "stock": 31},
    {"id": "258", "brand": "Samsung", "type": "TFT", "name": "S22U（EU version）WF", "retail": 345000, "wholesale": 255000, "stock": 31},
    {"id": "259", "brand": "Realme", "type": "Incell HD+", "name": "A1K / RealmeC2", "retail": 99000, "wholesale": 73000, "stock": 30},
    {"id": "260", "brand": "Honor", "type": "Incell HD+", "name": "RY X5B", "retail": 107000, "wholesale": 79000, "stock": 30},
    {"id": "261", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "HOT40 / SPARK20PRO / KJ6 / KJ7", "retail": 115000, "wholesale": 85000, "stock": 30},
    {"id": "262", "brand": "Samsung", "type": "IPS LCD", "name": "A11 2020 / A115", "retail": 100000, "wholesale": 74000, "stock": 30},
    {"id": "263", "brand": "Honor", "type": "Incell HD+", "name": "X5+", "retail": 103000, "wholesale": 76000, "stock": 29},
    {"id": "264", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "SPARK20PRO5G / NOTE40X5G", "retail": 113000, "wholesale": 83000, "stock": 29},
    {"id": "265", "brand": "Samsung", "type": "TFT", "name": "S9WF", "retail": 229000, "wholesale": 169000, "stock": 29},
    {"id": "266", "brand": "Samsung", "type": "IPS LCD", "name": "A53WF", "retail": 153000, "wholesale": 113000, "stock": 29},
    {"id": "267", "brand": "Huawei", "type": "Incell HD+", "name": "PSMART Z", "retail": 110000, "wholesale": 81000, "stock": 28},
    {"id": "268", "brand": "Vivo", "type": "Incell HD+", "name": "Y03 / Y18 / Y37 / Y18E / Y18I / Y18S / Y28E 5G / Y03T / Y28S 5G / T3 LITE 5G", "retail": 96000, "wholesale": 71000, "stock": 28},
    {"id": "269", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "SPARK8PRO", "retail": 117000, "wholesale": 86000, "stock": 28},
    {"id": "270", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE10PRO 4G-WF", "retail": 142000, "wholesale": 105000, "stock": 28},
    {"id": "271", "brand": "Vivo", "type": "Incell HD+", "name": "Y58", "retail": 110000, "wholesale": 81000, "stock": 28},
    {"id": "272", "brand": "Honor", "type": "Incell HD+", "name": "RY X9A / MAGIC 5LITE", "retail": 206000, "wholesale": 152000, "stock": 28},
    {"id": "273", "brand": "Samsung", "type": "TFT", "name": "S8WF", "retail": 219000, "wholesale": 162000, "stock": 28},
    {"id": "274", "brand": "Honor", "type": "OLED", "name": "RY 90WF", "retail": 470000, "wholesale": 348000, "stock": 28},
    {"id": "275", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE5 PLUS", "retail": 99000, "wholesale": 73000, "stock": 27},
    {"id": "276", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "Spark7T", "retail": 99000, "wholesale": 73000, "stock": 27},
    {"id": "277", "brand": "Vivo", "type": "Incell HD+", "name": "Y35 5G", "retail": 106000, "wholesale": 78000, "stock": 27},
    {"id": "278", "brand": "iPhone", "type": "Incell HD+", "name": "16PRO", "retail": 262000, "wholesale": 194000, "stock": 27},
    {"id": "279", "brand": "Redmi", "type": "OLED", "name": "NOTE12Pro 4G-WF", "retail": 373000, "wholesale": 276000, "stock": 27},
    {"id": "280", "brand": "iPhone", "type": "Servis", "name": "14PROMAX-F(Q)", "retail": 1118000, "wholesale": 828000, "stock": 27},
    {"id": "281", "brand": "Huawei", "type": "Servis", "name": "NOVA10PRO", "retail": 632000, "wholesale": 468000, "stock": 27},
    {"id": "282", "brand": "Samsung", "type": "IPS LCD", "name": "A04S / A047 / A136B", "retail": 98000, "wholesale": 72000, "stock": 26},
    {"id": "283", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE5 PLUS", "retail": 99000, "wholesale": 73000, "stock": 26},
    {"id": "284", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "POVA NEO 6", "retail": 106000, "wholesale": 78000, "stock": 26},
    {"id": "285", "brand": "Honor", "type": "Incell HD+", "name": "X7D 5G", "retail": 111000, "wholesale": 82000, "stock": 26},
    {"id": "286", "brand": "Samsung", "type": "IPS LCD", "name": "A35 / A55", "retail": 123000, "wholesale": 91000, "stock": 26},
    {"id": "287", "brand": "Redmi", "type": "OLED", "name": "NOTE13PRO 4G WF", "retail": 428000, "wholesale": 317000, "stock": 26},
    {"id": "288", "brand": "Xiaomi", "type": "Servis", "name": "Mi Note10Pro / Note10Lite", "retail": 553000, "wholesale": 409000, "stock": 26},
    {"id": "289", "brand": "Redmi", "type": "Incell HD+", "name": "9A / 9AT / 9C / 9i / 10A / POCO-C3", "retail": 90000, "wholesale": 66000, "stock": 25},
    {"id": "290", "brand": "Redmi", "type": "Incell HD+", "name": "Note 10 / Note 10s / POCO M5S", "retail": 111000, "wholesale": 82000, "stock": 25},
    {"id": "291", "brand": "Oppo", "type": "Incell HD+", "name": "RENO 5LITE WF", "retail": 135000, "wholesale": 100000, "stock": 25},
    {"id": "292", "brand": "Samsung", "type": "IPS LCD", "name": "A53 / A535-WF", "retail": 156000, "wholesale": 115000, "stock": 25},
    {"id": "293", "brand": "Honor", "type": "Incell HD+", "name": "RY X6 / X6X / X8 5G / RY 70LITE / X8A 5G", "retail": 106000, "wholesale": 78000, "stock": 25},
    {"id": "294", "brand": "Oppo", "type": "Incell HD+", "name": "V27 5G", "retail": 221000, "wholesale": 163000, "stock": 25},
    {"id": "295", "brand": "Samsung", "type": "TFT", "name": "S9+WF", "retail": 229000, "wholesale": 169000, "stock": 25},
    {"id": "296", "brand": "iPhone", "type": "Servis", "name": "12PROMAX-F-(Q)", "retail": 681000, "wholesale": 504000, "stock": 25},
    {"id": "297", "brand": "Samsung", "type": "IPS LCD", "name": "A01M 2020 / A015", "retail": 92000, "wholesale": 68000, "stock": 24},
    {"id": "298", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE5 / NOTE 5 PRO", "retail": 99000, "wholesale": 73000, "stock": 24},
    {"id": "299", "brand": "iPhone", "type": "Incell HD+", "name": "XSMAX", "retail": 137000, "wholesale": 101000, "stock": 24},
    {"id": "300", "brand": "Samsung", "type": "IPS LCD", "name": "S24UWF", "retail": 327000, "wholesale": 242000, "stock": 24},
    {"id": "301", "brand": "iPhone", "type": "Servis", "name": "XSMAX-F(Q)", "retail": 585000, "wholesale": 433000, "stock": 24},
    {"id": "302", "brand": "Redmi", "type": "OLED", "name": "NOTE11 4G WF", "retail": 392000, "wholesale": 290000, "stock": 23},
    {"id": "303", "brand": "Vivo", "type": "Incell HD+", "name": "S6 / G1 / S7E / Y70 / Y73S", "retail": 107000, "wholesale": 79000, "stock": 22},
    {"id": "304", "brand": "Xiaomi", "type": "Incell HD+", "name": "MI NOTE10 LITE / CC9PRO", "retail": 162000, "wholesale": 120000, "stock": 22},
    {"id": "305", "brand": "Redmi", "type": "Incell HD+", "name": "Note14pro 5G / Note13proplus / PocoX7 / Note14pro plus", "retail": 207000, "wholesale": 153000, "stock": 22},
    {"id": "306", "brand": "Realme", "type": "Incell HD+", "name": "realme C31", "retail": 106000, "wholesale": 78000, "stock": 21},
    {"id": "307", "brand": "iPhone", "type": "Incell HD+", "name": "12 / 12PRO", "retail": 144000, "wholesale": 106000, "stock": 21},
    {"id": "308", "brand": "Samsung", "type": "IPS LCD", "name": "A24-4G / Galaxy A25 5G / Galaxy M34 5G / A26-Galaxy F34 5G", "retail": 111000, "wholesale": 82000, "stock": 21},
    {"id": "309", "brand": "Huawei", "type": "Servis", "name": "NOVA10SE", "retail": 437000, "wholesale": 323000, "stock": 21},
    {"id": "310", "brand": "iPhone", "type": "Servis", "name": "13PROMAX-F(Q)", "retail": 863000, "wholesale": 639000, "stock": 21},
    {"id": "311", "brand": "Honor", "type": "Incell HD+", "name": "RY 9XLITE(2020) / RY 8X", "retail": 106000, "wholesale": 78000, "stock": 20},
    {"id": "312", "brand": "Samsung", "type": "TFT", "name": "S20+WF", "retail": 250000, "wholesale": 185000, "stock": 20},
    {"id": "313", "brand": "Samsung", "type": "OLED", "name": "A20-WF", "retail": 308000, "wholesale": 228000, "stock": 20},
    {"id": "314", "brand": "Oppo", "type": "Incell HD+", "name": "A5PRO", "retail": 106000, "wholesale": 78000, "stock": 19},
    {"id": "315", "brand": "Samsung", "type": "TFT", "name": "S20UWF", "retail": 273000, "wholesale": 202000, "stock": 19},
    {"id": "316", "brand": "Samsung", "type": "OLED", "name": "A30S-WF", "retail": 308000, "wholesale": 228000, "stock": 19},
    {"id": "317", "brand": "Samsung", "type": "OLED", "name": "NOTE11 PRO 4G / NOTE12 PRO 4G WF", "retail": 373000, "wholesale": 276000, "stock": 18},
    {"id": "318", "brand": "iPhone", "type": "Incell HD+", "name": "16PROMAX", "retail": 303000, "wholesale": 224000, "stock": 17},
    {"id": "319", "brand": "Redmi", "type": "OLED", "name": "NOTE12 4G-WF", "retail": 357000, "wholesale": 264000, "stock": 17},
    {"id": "320", "brand": "Samsung", "type": "IPS LCD", "name": "A12 / A02 / A125 / A127 2021 / A022 / A32 5G / M12 / M127 / M02", "retail": 91000, "wholesale": 67000, "stock": 16},
    {"id": "321", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE11R / 10 5G / 11Prime 5G / POCO M4 5G / M5(INDIA) / NOTE11E", "retail": 102000, "wholesale": 75000, "stock": 16},
    {"id": "322", "brand": "Honor", "type": "Servis", "name": "X8A / X8 2023", "retail": 130000, "wholesale": 96000, "stock": 16},
    {"id": "323", "brand": "Honor", "type": "Incell HD+", "name": "RY90", "retail": 114000, "wholesale": 84000, "stock": 16},
    {"id": "324", "brand": "Samsung", "type": "IPS LCD", "name": "A23 4G / A235 / M336", "retail": 98000, "wholesale": 72000, "stock": 15},
    {"id": "325", "brand": "iPhone", "type": "Incell HD+", "name": "11PRO", "retail": 142000, "wholesale": 105000, "stock": 15},
    {"id": "326", "brand": "iPhone", "type": "Servis", "name": "7GW-F(Q)", "retail": 169000, "wholesale": 125000, "stock": 15},
    {"id": "327", "brand": "iPhone", "type": "Servis", "name": "7PW-F(Q)", "retail": 219000, "wholesale": 162000, "stock": 15},
    {"id": "328", "brand": "Redmi", "type": "OLED", "name": "NOTE13 4G-WF", "retail": 368000, "wholesale": 272000, "stock": 15},
    {"id": "329", "brand": "Oppo", "type": "Incell HD+", "name": "NARZO 50A", "retail": 95000, "wholesale": 70000, "stock": 14},
    {"id": "330", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "SPARK30PRO / HOT50PRO / S25 / S685LN", "retail": 121000, "wholesale": 89000, "stock": 14},
    {"id": "331", "brand": "Samsung", "type": "OLED", "name": "A325 / A32 4G / A32LITE-WF", "retail": 335000, "wholesale": 248000, "stock": 14},
    {"id": "332", "brand": "Samsung", "type": "TFT", "name": "S23U(EU version)WF", "retail": 350000, "wholesale": 259000, "stock": 14},
    {"id": "333", "brand": "iPhone", "type": "Servis", "name": "12PRO-F(Q）", "retail": 639000, "wholesale": 473000, "stock": 14},
    {"id": "334", "brand": "Samsung", "type": "OLED", "name": "S10+-WF", "retail": 1523000, "wholesale": 1128000, "stock": 14},
    {"id": "335", "brand": "Samsung", "type": "IPS LCD", "name": "J5 2017 / J5Pro / J530", "retail": 98000, "wholesale": 72000, "stock": 13},
    {"id": "336", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "HOT40(X6836) / SPARK20PRO(KJ6) / Spark10pro(KI7)", "retail": 110000, "wholesale": 81000, "stock": 13},
    {"id": "337", "brand": "iPhone", "type": "Incell HD+", "name": "13MINI-FHD", "retail": 253000, "wholesale": 187000, "stock": 13},
    {"id": "338", "brand": "Realme", "type": "Incell HD+", "name": "realme9Pro plus / Realme9 4g / Reno7 / Reno 8t / REALME10 4G", "retail": 114000, "wholesale": 84000, "stock": 13},
    {"id": "339", "brand": "iPhone", "type": "Servis", "name": "11PROMAX-F(Q)", "retail": 694000, "wholesale": 514000, "stock": 13},
    {"id": "340", "brand": "Realme", "type": "Incell HD+", "name": "REALME C35 / Narzo 50A prime", "retail": 95000, "wholesale": 70000, "stock": 12},
    {"id": "341", "brand": "Vivo", "type": "Incell HD+", "name": "A57 5G / A58 5G / A77 5G / A78 5G / NORD N20 SE / NORD N300 5G / A17 / A38 / A18 / A56S 5G / A58X / A57 4G / A17K / A77 4G / A17s / ONE PlusN20se / A1 5G(Vitality Edition Phone) / A17K(A01) / A17K(A40) / A1X 5G / A2M / A2X", "retail": 100000, "wholesale": 74000, "stock": 12},
    {"id": "342", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "BG6 / BG7 / BG7N / SMART8HD / SMART8 PRO / SMART8 PLUS / HOT40I / SPARK GO 2024 / POP8 / BG6H / BG6I / SPARK20 / KJ5 / KJ5N / SPARK20C / A666L / A666LN / A70S / RS4 / S24", "retail": 96000, "wholesale": 71000, "stock": 12},
    {"id": "343", "brand": "Oppo", "type": "Incell HD+", "name": "S6 5G", "retail": 114000, "wholesale": 84000, "stock": 12},
    {"id": "344", "brand": "iPhone", "type": "Servis", "name": "15PROMAX-F(Q-X)", "retail": 1226000, "wholesale": 908000, "stock": 12},
    {"id": "345", "brand": "Vivo", "type": "Incell HD+", "name": "Y58", "retail": 104000, "wholesale": 77000, "stock": 11},
    {"id": "346", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE11S-WF", "retail": 134000, "wholesale": 99000, "stock": 11},
    {"id": "347", "brand": "iPhone", "type": "Servis", "name": "7PB-F(Q)", "retail": 219000, "wholesale": 162000, "stock": 11},
    {"id": "348", "brand": "Vivo", "type": "Incell HD+", "name": "s18e / 30lite 5G / 30lite 4G / T3 5G / Y100 4G / Y100 5 G / Y200E 5G / iqooz9 5G / Y300 5G / Y400 5G / iqoo Z10 lite 4G / Y200 5G", "retail": 303000, "wholesale": 224000, "stock": 11},
    {"id": "349", "brand": "Samsung", "type": "OLED", "name": "A15 / A155 / A156 / M15 / M156 5G", "retail": 412000, "wholesale": 305000, "stock": 11},
    {"id": "350", "brand": "Honor", "type": "Incell HD+", "name": "RY Y72 / Y72S", "retail": 107000, "wholesale": 79000, "stock": 10},
    {"id": "351", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE11 4G-WF", "retail": 129000, "wholesale": 95000, "stock": 10},
    {"id": "352", "brand": "Honor", "type": "Incell HD+", "name": "X7D 5G WF", "retail": 185000, "wholesale": 137000, "stock": 10},
    {"id": "353", "brand": "Samsung", "type": "TFT", "name": "S21WF", "retail": 249000, "wholesale": 184000, "stock": 10},
    {"id": "354", "brand": "Samsung", "type": "OLED", "name": "A165 4G / A166 5G / M16 5G / F16 5G / A266 / A26 5G / A175 4G / A176 5G / M176 / F176", "retail": 418000, "wholesale": 309000, "stock": 10},
    {"id": "355", "brand": "Samsung", "type": "OLED", "name": "A175 4G / A176 5G / M176 / F176 WF", "retail": 451000, "wholesale": 334000, "stock": 10},
    {"id": "356", "brand": "iPhone", "type": "Servis", "name": "16PRO-F(Q)", "retail": 1005000, "wholesale": 744000, "stock": 10},
    {"id": "357", "brand": "iPhone", "type": "Servis", "name": "15PRO-F(Q)", "retail": 1541000, "wholesale": 1141000, "stock": 10},
    {"id": "358", "brand": "Huawei", "type": "Incell HD+", "name": "Y7P / Y7P 2020", "retail": 103000, "wholesale": 76000, "stock": 9},
    {"id": "359", "brand": "Vivo", "type": "Incell HD+", "name": "Y35 5G", "retail": 103000, "wholesale": 76000, "stock": 9},
    {"id": "360", "brand": "Oppo", "type": "Incell HD+", "name": "A40 / A60 / A80 / A3PRO", "retail": 106000, "wholesale": 78000, "stock": 9},
    {"id": "361", "brand": "Oppo", "type": "Incell HD+", "name": "A3PRO", "retail": 106000, "wholesale": 78000, "stock": 9},
    {"id": "362", "brand": "Honor", "type": "Servis", "name": "RY X5B", "retail": 104000, "wholesale": 77000, "stock": 9},
    {"id": "363", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE10PRO 4G / NOTE10MAX / NOTE11PRO 4G / 5G / NOTE13 4G / POCO X4PRO / NOTE10PRO+ / NOTE11PRO+ / NOTE11E PRO / NOTE14 4G / M7PRO / NOTE12PRO 4G", "retail": 108000, "wholesale": 80000, "stock": 9},
    {"id": "364", "brand": "iPhone", "type": "Incell HD+", "name": "XSMAX-FHD", "retail": 234000, "wholesale": 173000, "stock": 9},
    {"id": "365", "brand": "Samsung", "type": "IPS LCD", "name": "A356 / A556 / A55 5G / M35 WF", "retail": 195000, "wholesale": 144000, "stock": 9},
    {"id": "366", "brand": "Xiaomi", "type": "Incell HD+", "name": "MI 12PRO / MI12S PRO", "retail": 219000, "wholesale": 162000, "stock": 9},
    {"id": "367", "brand": "Honor", "type": "Incell HD+", "name": "X9CWF", "retail": 299000, "wholesale": 221000, "stock": 9},
    {"id": "368", "brand": "Samsung", "type": "IPS LCD", "name": "J2Core / J260", "retail": 87000, "wholesale": 64000, "stock": 8},
    {"id": "369", "brand": "Samsung", "type": "IPS LCD", "name": "A32 4G / A325 / A32 LITE WF", "retail": 127000, "wholesale": 94000, "stock": 8},
    {"id": "370", "brand": "Xiaomi", "type": "OLED", "name": "F3 / F4 / MI11I", "retail": 377000, "wholesale": 279000, "stock": 8},
    {"id": "371", "brand": "Oppo", "type": "OLED", "name": "RENO 8T 5G", "retail": 392000, "wholesale": 290000, "stock": 8},
    {"id": "372", "brand": "Samsung", "type": "OLED", "name": "S23ultra / S918-WF", "retail": 883000, "wholesale": 654000, "stock": 8},
    {"id": "373", "brand": "Samsung", "type": "IPS LCD", "name": "A21S 2020 / A217", "retail": 91000, "wholesale": 67000, "stock": 7},
    {"id": "374", "brand": "Samsung", "type": "IPS LCD", "name": "A03CORE / A032", "retail": 91000, "wholesale": 67000, "stock": 7},
    {"id": "375", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "HOT60I", "retail": 106000, "wholesale": 78000, "stock": 7},
    {"id": "376", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "SPARK20PRO5G / NOTE40X5G", "retail": 114000, "wholesale": 84000, "stock": 7},
    {"id": "377", "brand": "Vivo", "type": "Incell HD+", "name": "S9e-V2048A / S15e-V2190A / VIVO T1 5G -V2150 / VIVO T1 Pro 5G-V2151", "retail": 115000, "wholesale": 85000, "stock": 7},
    {"id": "378", "brand": "iPhone", "type": "Servis", "name": "8PB-F(Q)", "retail": 225000, "wholesale": 166000, "stock": 7},
    {"id": "379", "brand": "Honor", "type": "Incell HD+", "name": "X8 WF", "retail": 180000, "wholesale": 133000, "stock": 7},
    {"id": "380", "brand": "iPhone", "type": "Incell HD+", "name": "12 / 12PRO-FHD", "retail": 234000, "wholesale": 173000, "stock": 7},
    {"id": "381", "brand": "Vivo", "type": "Incell HD+", "name": "Y300", "retail": 276000, "wholesale": 204000, "stock": 7},
    {"id": "382", "brand": "Samsung", "type": "TFT", "name": "S22+WF", "retail": 285000, "wholesale": 211000, "stock": 7},
    {"id": "383", "brand": "iPhone", "type": "Servis", "name": "11PRO-F(Q)", "retail": 639000, "wholesale": 473000, "stock": 7},
    {"id": "384", "brand": "Redmi", "type": "OLED", "name": "POCO F3 WF", "retail": 437000, "wholesale": 323000, "stock": 7},
    {"id": "385", "brand": "Vivo", "type": "Incell HD+", "name": "C21Y/C25Y", "retail": 96000, "wholesale": 71000, "stock": 6},
    {"id": "386", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE 5 / NOTE 5 PRO", "retail": 96000, "wholesale": 71000, "stock": 6},
    {"id": "387", "brand": "Vivo", "type": "Incell HD+", "name": "Y100 / Y100-5G / Y200 / S18E / Y300 5G / Y200 5G / 5G", "retail": 118000, "wholesale": 87000, "stock": 6},
    {"id": "388", "brand": "iPhone", "type": "Servis", "name": "8GW-F(Q)", "retail": 176000, "wholesale": 130000, "stock": 6},
    {"id": "389", "brand": "Realme", "type": "Incell HD+", "name": "N61 / N63 / Realme note60", "retail": 102000, "wholesale": 75000, "stock": 6},
    {"id": "390", "brand": "Honor", "type": "Incell HD+", "name": "X8A / X8 2023", "retail": 104000, "wholesale": 77000, "stock": 6},
    {"id": "391", "brand": "Samsung", "type": "IPS LCD", "name": "A56WF", "retail": 208000, "wholesale": 154000, "stock": 6},
    {"id": "392", "brand": "Honor", "type": "Incell HD+", "name": "RY 50", "retail": 219000, "wholesale": 162000, "stock": 6},
    {"id": "393", "brand": "Samsung", "type": "TFT", "name": "S23WF", "retail": 291000, "wholesale": 215000, "stock": 6},
    {"id": "394", "brand": "iPhone", "type": "Incell HD+", "name": "13PROMAX-FHD", "retail": 308000, "wholesale": 228000, "stock": 6},
    {"id": "395", "brand": "Samsung", "type": "TFT", "name": "S23+WF", "retail": 391000, "wholesale": 289000, "stock": 6},
    {"id": "396", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE10PRO 4G WF", "retail": 141000, "wholesale": 104000, "stock": 6},
    {"id": "397", "brand": "Oppo", "type": "Incell HD+", "name": "A59 / F1S", "retail": 91000, "wholesale": 67000, "stock": 5},
    {"id": "398", "brand": "Samsung", "type": "IPS LCD", "name": "A16 4G / A17 / A17 5G / A16 5G / M16 / F16", "retail": 106000, "wholesale": 78000, "stock": 5},
    {"id": "399", "brand": "Samsung", "type": "IPS LCD", "name": "A515 / A516 / M31S-WF", "retail": 126000, "wholesale": 93000, "stock": 5},
    {"id": "400", "brand": "iPhone", "type": "Servis", "name": "8GB-F(Q)", "retail": 176000, "wholesale": 130000, "stock": 5},
    {"id": "401", "brand": "Realme", "type": "Incell HD+", "name": "REALMEC53 / NOTE50", "retail": 102000, "wholesale": 75000, "stock": 5},
    {"id": "402", "brand": "iPhone", "type": "Servis", "name": "8PW-F-(Q)", "retail": 225000, "wholesale": 166000, "stock": 5},
    {"id": "403", "brand": "Honor", "type": "Incell HD+", "name": "X7D 4G WF", "retail": 185000, "wholesale": 137000, "stock": 5},
    {"id": "404", "brand": "Samsung", "type": "IPS LCD", "name": "A245 / A246 / A255 / A256 / M346", "retail": 114000, "wholesale": 84000, "stock": 4},
    {"id": "405", "brand": "Honor", "type": "Servis", "name": "X6B", "retail": 102000, "wholesale": 75000, "stock": 4},
    {"id": "406", "brand": "Honor", "type": "Incell HD+", "name": "Magic7 Lite / X9C", "retail": 253000, "wholesale": 187000, "stock": 4},
    {"id": "407", "brand": "Vivo", "type": "OLED", "name": "Y100 4G", "retail": 327000, "wholesale": 242000, "stock": 4},
    {"id": "408", "brand": "Samsung", "type": "IPS LCD", "name": "S24WF", "retail": 488000, "wholesale": 361000, "stock": 4},
    {"id": "409", "brand": "Honor", "type": "Incell HD+", "name": "X9BWF", "retail": 508000, "wholesale": 376000, "stock": 4},
    {"id": "410", "brand": "Honor", "type": "Incell HD+", "name": "RY X6 / X6S / X8 5G / 70LITE / X8A 5G", "retail": 95000, "wholesale": 70000, "stock": 3},
    {"id": "411", "brand": "Vivo", "type": "Incell HD+", "name": "Y56 5G / Y35 4G / Y33S 4GOverseas version", "retail": 95000, "wholesale": 70000, "stock": 3},
    {"id": "412", "brand": "Huawei", "type": "Incell HD+", "name": "PSMART Z", "retail": 96000, "wholesale": 71000, "stock": 3},
    {"id": "413", "brand": "Huawei", "type": "Incell HD+", "name": "CW40 / RY X6A / CW40C / X5 Plus / X5B / X5B Plus", "retail": 98000, "wholesale": 72000, "stock": 3},
    {"id": "414", "brand": "Samsung", "type": "IPS LCD", "name": "A24 4G-WF", "retail": 130000, "wholesale": 96000, "stock": 3},
    {"id": "415", "brand": "Xiaomi", "type": "Incell HD+", "name": "MI 13T / MI13TPRO", "retail": 169000, "wholesale": 125000, "stock": 3},
    {"id": "416", "brand": "Redmi", "type": "Incell HD+", "name": "Note 14 5G / Note 14 / Note 13 / POCO M7 PRO 5G", "retail": 108000, "wholesale": 80000, "stock": 3},
    {"id": "417", "brand": "Samsung", "type": "IPS LCD", "name": "A725-WF", "retail": 171000, "wholesale": 126000, "stock": 3},
    {"id": "418", "brand": "iPhone", "type": "Incell HD+", "name": "12MINI-FHD", "retail": 253000, "wholesale": 187000, "stock": 3},
    {"id": "419", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "BF7 / BF6 / A60 / A60S / POP7 / KI5K / SPARKGO2023 / SMART10HD / KI5Q / SPARK10(KI5) / SPARK10C / KI8 / KI5N / VISION3 / SMART7 / S23 / POP7PRO / SMARK7HD / A662L / NOTE20 / NOTE12VIP / HOT30I", "retail": 95000, "wholesale": 70000, "stock": 2},
    {"id": "420", "brand": "Vivo", "type": "Incell HD+", "name": "S6 / G1 / S7E / Y70 / Y73S", "retail": 102000, "wholesale": 75000, "stock": 2},
    {"id": "421", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "SPARK5AIR / LC7 / LC7S / LC8 / SPARK6AIR / POUVOIR4 / POUVOIR4PRO / SPARKPOWER2", "retail": 103000, "wholesale": 76000, "stock": 2},
    {"id": "422", "brand": "Honor", "type": "Servis", "name": "RY X5B", "retail": 106000, "wholesale": 78000, "stock": 2},
    {"id": "423", "brand": "Samsung", "type": "IPS LCD", "name": "A325N / A325M / A325F / M325FV / M325F", "retail": 107000, "wholesale": 79000, "stock": 2},
    {"id": "424", "brand": "Huawei", "type": "Incell HD+", "name": "NOVA12I", "retail": 114000, "wholesale": 84000, "stock": 2},
    {"id": "425", "brand": "iPhone", "type": "Incell HD+", "name": "13", "retail": 146000, "wholesale": 108000, "stock": 2},
    {"id": "426", "brand": "iPhone", "type": "Incell HD+", "name": "11-FHD", "retail": 202000, "wholesale": 149000, "stock": 2},
    {"id": "427", "brand": "Huawei", "type": "Servis", "name": "NOVA 5I / NOVA 7I", "retail": 156000, "wholesale": 115000, "stock": 2},
    {"id": "428", "brand": "Honor", "type": "Incell HD+", "name": "X7B WF", "retail": 158000, "wholesale": 117000, "stock": 2},
    {"id": "429", "brand": "Honor", "type": "Incell HD+", "name": "RY 70", "retail": 214000, "wholesale": 158000, "stock": 2},
    {"id": "430", "brand": "Huawei", "type": "Servis", "name": "NOVA12 SE", "retail": 216000, "wholesale": 160000, "stock": 2},
    {"id": "431", "brand": "Samsung", "type": "TFT", "name": "S21+WF", "retail": 249000, "wholesale": 184000, "stock": 2},
    {"id": "432", "brand": "Samsung", "type": "TFT", "name": "S22WF", "retail": 319000, "wholesale": 236000, "stock": 2},
    {"id": "433", "brand": "Vivo", "type": "OLED", "name": "V29E", "retail": 327000, "wholesale": 242000, "stock": 2},
    {"id": "434", "brand": "Huawei", "type": "OLED", "name": "NOVA12 SE", "retail": 453000, "wholesale": 335000, "stock": 2},
    {"id": "435", "brand": "Huawei", "type": "Servis", "name": "NOVA10PRO", "retail": 642000, "wholesale": 475000, "stock": 2},
    {"id": "436", "brand": "Samsung", "type": "OLED", "name": "S24U-WF", "retail": 994000, "wholesale": 736000, "stock": 2},
    {"id": "437", "brand": "Samsung", "type": "IPS LCD", "name": "J6 2018 / J600", "retail": 94000, "wholesale": 69000, "stock": 1},
    {"id": "438", "brand": "Oppo", "type": "Incell HD+", "name": "A77S", "retail": 95000, "wholesale": 70000, "stock": 1},
    {"id": "439", "brand": "Honor", "type": "Incell HD+", "name": "RY X5", "retail": 102000, "wholesale": 75000, "stock": 1},
    {"id": "440", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "NOTE10(X693) / NOTE 11I / NOTE 11S(X698) / NOTE 11Pro(X697) / POVA 2(LE7 / LE7n) / POVA3(LF7) / POVA 5G(LE8)", "retail": 123000, "wholesale": 91000, "stock": 1},
    {"id": "441", "brand": "iPhone", "type": "Incell HD+", "name": "15", "retail": 177000, "wholesale": 131000, "stock": 1},
    {"id": "442", "brand": "Samsung", "type": "IPS LCD", "name": "A33WF", "retail": 153000, "wholesale": 113000, "stock": 1},
    {"id": "443", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE12 4G / NOTE 12 5G / POCO X5 4G / POCO X5 5G", "retail": 108000, "wholesale": 80000, "stock": 1},
    {"id": "444", "brand": "Oppo", "type": "Incell HD+", "name": "RENO 8T 5G", "retail": 183000, "wholesale": 135000, "stock": 1},
    {"id": "445", "brand": "Samsung", "type": "IPS LCD", "name": "A30S-WF", "retail": 117000, "wholesale": 86000, "stock": 1},
    {"id": "446", "brand": "Honor", "type": "Incell HD+", "name": "Magic6 Lite 5G / X9B", "retail": 256000, "wholesale": 189000, "stock": 1},
    {"id": "447", "brand": "iPhone", "type": "Incell HD+", "name": "12PROMAX-FHD", "retail": 335000, "wholesale": 248000, "stock": 1},
    {"id": "448", "brand": "Samsung", "type": "OLED", "name": "A35 / M35WF", "retail": 369000, "wholesale": 273000, "stock": 1},
    {"id": "449", "brand": "Samsung", "type": "OLED", "name": "A525 / A526 / A528 / A52S-WF", "retail": 383000, "wholesale": 283000, "stock": 1},
    {"id": "450", "brand": "Oppo", "type": "OLED", "name": "GT MASTER", "retail": 484000, "wholesale": 358000, "stock": 1},
    {"id": "451", "brand": "Samsung", "type": "OLED", "name": "S22ultra / S908-WF", "retail": 883000, "wholesale": 654000, "stock": 1},
    {"id": "452", "brand": "Realme", "type": "Incell HD+", "name": "A32 4G / A33 / A53 4G / A53S / A54 4G / A55 4G / REALME7I / REALMEC17 / 1+N100", "retail": 96000, "wholesale": 71000, "stock": 0},
    {"id": "453", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE13 4G-WF", "retail": 175000, "wholesale": 129000, "stock": 0},
    {"id": "454", "brand": "Samsung", "type": "IPS LCD", "name": "A70 2019 / A705-WF", "retail": 127000, "wholesale": 94000, "stock": 0},
    {"id": "455", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE14 4G", "retail": 107000, "wholesale": 79000, "stock": 0},
    {"id": "456", "brand": "Honor", "type": "Incell HD+", "name": "RY X7C", "retail": 110000, "wholesale": 81000, "stock": 0},
]


WARRANTY_TEXT = (
    "🛡 <b>KAFOLAT VA QAYTARISH SHARTLARI (2 OY):</b>\n"
    "• Barcha displeylarga <b>2 oy kafolat</b> mavjud.\n"
    "• Zavod braki bo'lsa, xohishingizga ko'ra yangisiga almashtirib beriladi yoki pulingiz to'liq qaytariladi.\n"
    "• ⚠️ <b>Qat'iy talab:</b> Brakligini isbotlovchi aniq <b>video yoki rasm</b> bo'lishi shart! "
    "Rasmi yoki videosi bo'lmasa, mahsulot mutlaqo qaytarib olinmaydi!"
)


def h(value):
    """Foydalanuvchi matnini HTML xabarga xavfsiz qo'yish."""
    return escape(str(value if value is not None else ""), quote=False)


# ===================== SAQLASH (Upstash Redis, bo'lmasa /tmp) =====================
def _redis(*cmd):
    r = requests.post(REDIS_URL, headers={"Authorization": f"Bearer {REDIS_TOKEN}"}, json=list(cmd), timeout=5)
    r.raise_for_status()
    return r.json().get("result")

_TMP = {"users": "/tmp/users.json", "orders": "/tmp/orders.json", "orders2": "/tmp/orders2.json",
        "last_order": "/tmp/last_order.json", "meta": "/tmp/meta.json",
        "catalog": "/tmp/catalog.json", "stock": "/tmp/stock.json", "watch": "/tmp/watch.json"}

def _file_load(name):
    try:
        with open(_TMP[name]) as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return {}

def _file_save(name, data):
    with open(_TMP[name], "w") as f:
        json.dump(data, f)

def store_get(name, key):
    try:
        if REDIS_URL:
            raw = _redis("HGET", name, str(key))
            return json.loads(raw) if raw else None
        return _file_load(name).get(str(key))
    except Exception:
        log.exception("store_get %s %s", name, key)
        return None

def store_set(name, key, value):
    try:
        if REDIS_URL:
            _redis("HSET", name, str(key), json.dumps(value, ensure_ascii=False))
        else:
            data = _file_load(name)
            data[str(key)] = value
            _file_save(name, data)
    except Exception:
        log.exception("store_set %s %s", name, key)

def store_all(name):
    try:
        if REDIS_URL:
            flat = _redis("HGETALL", name) or []
            return {flat[i]: json.loads(flat[i + 1]) for i in range(0, len(flat), 2)}
        return _file_load(name)
    except Exception:
        log.exception("store_all %s", name)
        return {}

# ===================== KATALOG: narx va qoldiq bazada =====================
PRODUCT_FIELDS = ("brand", "type", "name", "retail", "wholesale", "active")

def _set_many(name, mapping):
    if not mapping:
        return
    if REDIS_URL:
        flat = []
        for k, v in mapping.items():
            flat += [str(k), v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)]
        for i in range(0, len(flat), 400):
            _redis("HSET", name, *flat[i:i + 400])
    else:
        data = _file_load(name)
        data.update({str(k): v for k, v in mapping.items()})
        _file_save(name, data)

def _ensure_catalog():
    """Baza bo'sh bo'lsa, boshlang'ich katalogni bir marta yozib qo'yadi."""
    cat = store_all("catalog")
    if cat:
        return cat
    log.info("Katalog bazaga yozilmoqda (%d ta)", len(SEED_CATALOG))
    _set_many("catalog", {p["id"]: {k: p[k] for k in ("brand", "type", "name", "retail", "wholesale")} | {"active": True}
                          for p in SEED_CATALOG})
    if not store_all("stock"):
        _set_many("stock", {p["id"]: int(p.get("stock") or 0) for p in SEED_CATALOG})
    return store_all("catalog")

def get_catalog(include_hidden=False):
    """{id: {...mahsulot, stock}} ko'rinishida to'liq katalog."""
    try:
        cat = _ensure_catalog()
        stock = store_all("stock")
    except Exception:
        log.exception("get_catalog")
        cat, stock = {}, {}
    if not cat:  # baza ishlamasa ham do'kon to'xtamasin
        cat = {p["id"]: {**p, "active": True} for p in SEED_CATALOG}
        stock = {p["id"]: p.get("stock", 0) for p in SEED_CATALOG}
    out = {}
    for pid, p in cat.items():
        if not isinstance(p, dict):
            continue
        if not include_hidden and p.get("active") is False:
            continue
        try:
            st = int(stock.get(pid, 0) or 0)
        except (TypeError, ValueError):
            st = 0
        out[str(pid)] = {"id": str(pid), **p, "stock": max(0, st)}
    return out

def stock_add(pid, delta):
    """Qoldiqni atomik o'zgartiradi, yangi qiymatni qaytaradi."""
    pid = str(pid)
    try:
        if REDIS_URL:
            return int(_redis("HINCRBY", "stock", pid, int(delta)))
        data = _file_load("stock")
        data[pid] = int(data.get(pid, 0) or 0) + int(delta)
        _file_save("stock", data)
        return data[pid]
    except Exception:
        log.exception("stock_add %s", pid)
        return None

def reserve_stock(pid, want):
    """Bor qoldiqdan `want` tagacha band qiladi, haqiqatda olingan sonni qaytaradi."""
    left = stock_add(pid, -want)
    if left is None:
        return want
    if left < 0:
        give_back = min(want, -left)
        stock_add(pid, give_back)
        return want - give_back
    return want

def release_order_stock(p, by="bot"):
    """Bekor qilingan buyurtma tovarlarini omborga qaytaradi (bir marta)."""
    if not p or p.get("stock_returned") or not p.get("stock_reserved"):
        return
    back = []
    for it in p.get("items", []):
        q = int(it.get("rq", it.get("aq", 0)) or 0)
        if q > 0:
            left = stock_add(it["id"], q)
            if left is not None and left - q <= 0 < left:
                back.append(str(it["id"]))
    p["stock_returned"] = True
    if back:
        notify_restock(back)


# ---- "Kelganda xabar bering": har bir mahsulotni kutayotgan mijozlar ----
WATCH_MAX_PER_ORDER = 50

def watch_add(pid, cid):
    pid, cid = str(pid), str(cid)
    try:
        if REDIS_URL:
            _redis("SADD", f"watch:{pid}", cid)
            return
        data = _file_load("watch")
        lst = data.get(pid) or []
        if cid not in lst:
            lst.append(cid)
        data[pid] = lst
        _file_save("watch", data)
    except Exception:
        log.exception("watch_add %s", pid)

def watch_pop(pid):
    """Mahsulotni kutayotganlar ro'yxatini qaytaradi va tozalaydi."""
    pid = str(pid)
    try:
        if REDIS_URL:
            key = f"watch:{pid}"
            members = _redis("SMEMBERS", key) or []
            if members:
                _redis("SREM", key, *members)
            return [str(x) for x in members]
        data = _file_load("watch")
        lst = data.pop(pid, None) or []
        if lst:
            _file_save("watch", data)
        return [str(x) for x in lst]
    except Exception:
        log.exception("watch_pop %s", pid)
        return []

def save_watch_request(cid, ids):
    """Mijoz yuborgan ID larni tekshirib, tugagan mahsulotlarga obuna qiladi. Obuna bo'lgan nomlarni qaytaradi."""
    catalog = get_catalog()
    names = []
    for raw in list(ids or [])[:WATCH_MAX_PER_ORDER]:
        try:
            pid = str(int(raw))
        except (TypeError, ValueError):
            continue
        p = catalog.get(pid)
        if not p or int(p.get("stock", 0) or 0) > 0 or any(pid == n[0] for n in names):
            continue
        watch_add(pid, cid)
        names.append((pid, f"{p.get('brand', '')} {p.get('name', '')}".strip()))
    return [n for _, n in names]

def notify_restock(pids):
    """Omborga qaytgan mahsulotlarni kutayotgan mijozlarga bitta xabar bilan yozadi."""
    if not pids:
        return
    catalog = get_catalog()
    per_user = {}
    for pid in dict.fromkeys(str(x) for x in pids):
        p = catalog.get(pid)
        if not p or int(p.get("stock", 0) or 0) <= 0:
            continue  # yashirilgan yoki hali ham yo'q: kutish davom etadi
        for cid in watch_pop(pid):
            per_user.setdefault(cid, []).append(p)
    for cid, items in per_user.items():
        lines = "".join(f"• <b>{h(p.get('brand', ''))} {h(str(p.get('name', ''))[:40].rstrip(' /'))}</b> — "
                        f"{int(p.get('retail') or 0):,} so'm (optom {int(p.get('wholesale') or 0):,})\n" for p in items[:15])
        safe_send(cid, f"🔔 <b>Siz kutgan ekran omborga keldi!</b>\n\n{lines}\n"
                       f"Tugab qolmasidan oldin <b>«🛍 Do'konni ochish»</b> tugmasini bosing 👇",
                  parse_mode="HTML", reply_markup=main_kb())
    if per_user:
        log.info("Restock xabari: %d mijoz", len(per_user))


def get_user(uid):
    u = store_get("users", uid)
    return u if isinstance(u, dict) else {}

# ---- Buyurtmalar: har biri alohida ID bilan saqlanadi (tarix yo'qolmaydi) ----
STATUSES = {
    "yangi": "Yangi",
    "chek": "Rasm keldi",
    "tasdiqlandi": "Tasdiqlandi",
    "yuborildi": "Yuborildi",
    "yetkazildi": "Yetkazildi",
    "bekor": "Bekor qilindi",
}
STATUS_CUSTOMER_MSG = {
    "tasdiqlandi": "✅ Buyurtmangiz <b>#{id}</b> tasdiqlandi, tayyorlanmoqda.",
    "yuborildi": "📦 Buyurtmangiz <b>#{id}</b> yuborildi! Tez orada yetib boradi.",
    "yetkazildi": "🎉 Buyurtmangiz <b>#{id}</b> yetkazildi. Xaridingiz uchun rahmat!",
    "bekor": "❌ Buyurtmangiz <b>#{id}</b> bekor qilindi. Savollar bo'lsa, adminga yozing.",
}

def now_ms():
    return int(time.time() * 1000)

def next_order_id():
    try:
        if REDIS_URL:
            n = int(_redis("INCR", "order_seq"))
        else:
            meta = _file_load("meta")
            n = int(meta.get("order_seq", 0)) + 1
            meta["order_seq"] = n
            _file_save("meta", meta)
    except Exception:
        log.exception("order_seq")
        n = int(time.time()) % 1000000
    return f"E{1000 + n}"

def get_order(oid):
    o = store_get("orders2", oid)
    return o if isinstance(o, dict) else None

def get_payload(key):
    """key: buyurtma ID (E1001) yoki mijoz chat ID (oxirgi buyurtmasi)."""
    key = str(key)
    if key.startswith("E"):
        return get_order(key)
    oid = store_get("last_order", key)
    if oid:
        o = get_order(oid)
        if o:
            return o
    return store_get("orders", key)  # eski formatdagi buyurtma

def save_order(key, p):
    if p.get("id"):
        p["updated"] = now_ms()
        store_set("orders2", p["id"], p)
        store_set("last_order", p.get("cid", key), p["id"])
    else:
        store_set("orders", key, p)

def order_cid(key, p):
    return str((p or {}).get("cid") or key)

def set_status(p, status, note=None, by="bot"):
    if not p or not p.get("id") or status not in STATUSES:
        return p
    if p.get("status") != status or note:
        if status == "bekor":
            release_order_stock(p, by)
        p["status"] = status
        p.setdefault("history", []).append({"t": now_ms(), "s": status, "by": by, **({"note": note} if note else {})})
        save_order(p["cid"], p)
    return p


# ===================== BOT =====================
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)

def user_link(uid, name):
    """Mijoz profiliga havola: username bo'lmasa ham ID orqali ochiladi."""
    return f'<a href="tg://user?id={int(uid)}">{h(name or "Mijoz")}</a>'

def contact_line(uid, name, username, phone):
    parts = [f"👤 <b>Mijoz:</b> {user_link(uid, name)}"]
    if username:
        parts.append(f"🔗 @{h(username)}")
    parts.append(f"🆔 <code>{int(uid)}</code>")
    line = " | ".join(parts)
    line += f"\n📞 <b>Raqam:</b> {h(phone)}" if phone else "\n📞 <b>Raqam:</b> ⏳ <i>mijozdan so'raldi</i>"
    return line

def is_admin(uid):
    return ADMIN_ID != 0 and int(uid) == ADMIN_ID

def admin_only(handler):
    """Admin tugmalarini boshqa odam bosa olmasligi uchun."""
    def wrapper(c):
        if not is_admin(c.from_user.id):
            try: bot.answer_callback_query(c.id, "Bu tugma faqat admin uchun.", show_alert=True)
            except Exception: pass
            return
        return handler(c)
    wrapper.__name__ = handler.__name__
    return wrapper

def safe_send(chat_id, text, **kw):
    try:
        return bot.send_message(int(chat_id), text, **kw)
    except Exception:
        log.exception("send_message -> %s", chat_id)

def notify_admin(text):
    if ADMIN_ID:
        safe_send(ADMIN_ID, text, parse_mode="HTML")

def admin_contact_kb():
    url = f"https://t.me/{ADMIN_USERNAME}" if ADMIN_USERNAME else (f"tg://user?id={ADMIN_ID}" if ADMIN_ID else None)
    return InlineKeyboardMarkup().add(InlineKeyboardButton("💬 Admin bilan bog'lanish", url=url)) if url else None

def send_with_admin_btn(chat_id, text):
    """Admin bilan bog'lanish tugmasi bilan yuboradi; admin profili yopiq bo'lsa, tugmasiz yuboradi."""
    kb = admin_contact_kb()
    if kb:
        try:
            return bot.send_message(int(chat_id), text, parse_mode="HTML", reply_markup=kb)
        except Exception:
            log.warning("admin tugmasi bilan yuborilmadi, tugmasiz yuboriladi")
    return safe_send(chat_id, text, parse_mode="HTML")


def do_ulash():
    key = request.args.get("key", "")
    if not WEBHOOK_SECRET or not hmac.compare_digest(key, WEBHOOK_SECRET):
        return "Forbidden: kalit noto'g'ri", 403
    try:
        # Vercel'da funksiya /api/index manzilida ishlaydi
        webhook_url = f"https://{request.host}/api/index"
        ok = bot.set_webhook(url=webhook_url, secret_token=WEBHOOK_SECRET,
                             allowed_updates=["message", "callback_query"], drop_pending_updates=False)
        me = bot.get_me()
        if ok:
            return f"✅ Bot @{h(me.username)} <b>{h(webhook_url)}</b> manziliga ulandi. Endi Telegramda /start yozing.", 200
        return "❌ Webhook ulanmadi", 500
    except Exception as e:
        log.exception("set_webhook")
        return f"XATOLIK: {h(e)}", 500


def main_kb():
    m = ReplyKeyboardMarkup(resize_keyboard=True)
    m.add(KeyboardButton("🛍 Do'konni ochish", web_app=WebAppInfo(url=WEB_APP_URL)))
    return m

def contact_kb():
    m = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    m.add(KeyboardButton("📱 Telefon raqamimni yuborish", request_contact=True))
    return m

def admin_order_kb(cid):
    m = InlineKeyboardMarkup(row_width=2)
    m.add(
        InlineKeyboardButton("🤝 To'lov kelishildi", callback_data=f"pay:{cid}:cash"),
        InlineKeyboardButton("⚡️ Bugun yetkazish", callback_data=f"pay:{cid}:today"),
        InlineKeyboardButton("📦 Ertaga yetkazish", callback_data=f"pay:{cid}:tomorrow"),
        InlineKeyboardButton("❌ Bekor qilish", callback_data=f"pay:{cid}:cancel"),
        InlineKeyboardButton("⚠️ Ayrim tovarlar yo'q / Kam", callback_data=f"missing_menu:{cid}")
    )
    return m


@bot.message_handler(commands=['start'])
def handle_start(m):
    name = h(m.from_user.first_name or "Mijoz")
    user = get_user(m.chat.id)
    if user.get('role'):
        txt = (f"Assalomu alaykum, <b>{name}</b>! 👋\n\n<b>@ekranchi_bola</b> do'konimizga xush kelibsiz!\n\n"
               f"Pastdagi <b>«🛍 Do'konni ochish»</b> tugmasini bosib buyurtma berishingiz mumkin: 👇")
        bot.send_message(m.chat.id, txt, reply_markup=main_kb(), parse_mode="HTML")
    else:
        txt = (f"Assalomu alaykum, <b>{name}</b>!\nDo'kondan buyurtma berish uchun, iltimos, "
               f"<b>«📱 Telefon raqamimni yuborish»</b> tugmasini bosing: 👇")
        bot.send_message(m.chat.id, txt, reply_markup=contact_kb(), parse_mode="HTML")


@bot.message_handler(commands=['stat'])
def handle_stat(m):
    if not is_admin(m.chat.id):
        return
    users = store_all("users")
    optom = sum(1 for u in users.values() if isinstance(u, dict) and u.get('role') == 'Optom')
    retail = sum(1 for u in users.values() if isinstance(u, dict) and u.get('role') == 'Chakana')
    txt = (f"📊 <b>BOT STATISTIKASI:</b>\n━━━━━━━━━━━━━━━━━━━\n"
           f"📱 Raqam tasdiqlaganlar: <b>{len(users)} ta</b>\n"
           f"🤝 Optomchilar: <b>{optom} ta</b>\n"
           f"👤 Chakanachilar: <b>{retail} ta</b>")
    orders = [o for o in store_all("orders2").values() if isinstance(o, dict)]
    txt += f"\n🧾 Buyurtmalar: <b>{len(orders)} ta</b>\n\n📊 To'liq ma'lumot: /panel"
    if not REDIS_URL:
        txt += "\n\n⚠️ Doimiy baza ulanmagan: ma'lumotlar /tmp da, vaqti-vaqti bilan o'chib ketadi."
    bot.send_message(m.chat.id, txt, parse_mode="HTML")


@bot.message_handler(content_types=['contact'])
def handle_contact(m):
    if not (m.contact and m.contact.user_id == m.from_user.id):
        bot.send_message(m.chat.id, "Iltimos, pastdagi tugma orqali o'z raqamingizni yuboring.", reply_markup=contact_kb())
        return
    num = m.contact.phone_number
    phone = num if num.startswith('+') else '+' + num
    old = get_user(m.chat.id)
    store_set("users", m.chat.id, {"phone": phone, "role": old.get("role"), "name": m.from_user.first_name,
                                   "username": m.from_user.username})
    p = get_payload(m.chat.id)
    if p and not p.get("phone"):
        p["phone"] = phone
        save_order(m.chat.id, p)
        notify_admin(f"📞 <b>Buyurtma #{h(p.get('id', ''))} raqami keldi</b>\n{contact_line(m.chat.id, m.from_user.first_name, m.from_user.username, phone)}"
                     f"\n📍 {h(p.get('deliv'))} | {h(p.get('addr'))}")
        bot.send_message(m.chat.id, "✅ Rahmat! Raqamingiz buyurtmaga qo'shildi, admin tez orada bog'lanadi.",
                         reply_markup=main_kb())
        if old.get("role"):
            return
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton("🤝 Optom (Do'kon / Usta)", callback_data="set_role:Optom"),
           InlineKeyboardButton("👤 Chakana (Dona)", callback_data="set_role:Chakana"))
    bot.send_message(m.chat.id, f"✅ Raqamingiz tasdiqlandi: {h(phone)}\nIltimos, xarid qilish rejimini tanlang:", reply_markup=kb)


@bot.callback_query_handler(func=lambda c: c.data.startswith('set_role:'))
def handle_role_selection(c):
    role = c.data.split(':', 1)[1]
    if role not in ("Optom", "Chakana"):
        return bot.answer_callback_query(c.id)
    user = get_user(c.message.chat.id)
    if user:
        user['role'] = role
        store_set("users", c.message.chat.id, user)
    try: bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=None)
    except Exception: pass
    bot.answer_callback_query(c.id)
    bot.send_message(c.message.chat.id, f"✅ Rejimingiz: <b>{role}</b>\nKatalogni ochib xarid qilishingiz mumkin:",
                     reply_markup=main_kb(), parse_mode="HTML")


@bot.message_handler(content_types=['web_app_data'])
def handle_order(m):
    cid = str(m.chat.id)
    try:
        data = json.loads(m.web_app_data.data)
    except (ValueError, TypeError):
        bot.send_message(m.chat.id, "⚠️ Buyurtmani o'qib bo'lmadi. Do'konni qayta ochib, yana urinib ko'ring.")
        return
    if not isinstance(data, dict):
        bot.send_message(m.chat.id, "⚠️ Buyurtmani o'qib bo'lmadi. Do'konni qayta ochib, yana urinib ko'ring.")
        return
    if data.get('t') == 'nt':
        names = save_watch_request(cid, data.get('w'))
        if names:
            lst = "".join(f"• {h(n[:50])}\n" for n in names[:15])
            bot.send_message(m.chat.id, f"🔔 <b>Kuzatuvga olindi:</b>\n{lst}\nOmborga kelishi bilan sizga shu yerda xabar beramiz.",
                             parse_mode="HTML", reply_markup=main_kb())
        else:
            bot.send_message(m.chat.id, "✅ Tanlagan modellaringiz allaqachon omborda bor. Do'konni ochib buyurtma bering.",
                             reply_markup=main_kb())
        return
    try:
        watched = save_watch_request(cid, data.get('nt')) if data.get('nt') else []
        if watched:
            safe_send(cid, "🔔 <b>Kuzatuvga olindi:</b>\n" + "".join(f"• {h(n[:50])}\n" for n in watched[:15])
                      + "Omborga kelishi bilan xabar beramiz.", parse_mode="HTML")
        user = get_user(cid)
        phone = user.get('phone')
        role = user.get('role') or "—"

        name = str(data.get('n', 'Mijoz'))[:30].strip() or 'Mijoz'
        deliv = data.get('d') if data.get('d') in ALLOWED_DELIVERY else 'BTS'
        addr = str(data.get('a', ''))[:80].strip()
        tg_name = " ".join(x for x in [m.from_user.first_name, m.from_user.last_name] if x)

        # 1) Tovarlarni tekshirish: faqat katalogdagi ID lar, musbat butun son
        catalog = get_catalog()
        clean = {}
        for it in data.get('i', []) or []:
            try:
                item_id, q = str(int(it[0])), int(it[1])
            except (ValueError, TypeError, IndexError):
                continue
            if item_id in catalog and q > 0:
                clean[item_id] = min(MAX_QTY_PER_ITEM, clean.get(item_id, 0) + q)
        if not clean:
            bot.send_message(m.chat.id, "⚠️ Savatingiz bo'sh yoki noto'g'ri. Do'konni qayta ochib ko'ring.")
            return

        # 2) Qoldiqdan band qilish: omborda yetmasa, bori olinadi
        got, short_txt = {}, ""
        for item_id, q in clean.items():
            g = reserve_stock(item_id, q)
            got[item_id] = g
            if g < q:
                nm = catalog[item_id]['name']
                short_txt += (f"• <b>{h(nm[:30])}</b>: {q} ta so'radingiz, omborda <b>{g} ta</b> bor edi\n" if g
                              else f"• <b>{h(nm[:30])}</b>: omborda qolmagan\n")
        clean_ok = {k: v for k, v in got.items() if v > 0}
        if not clean_ok:
            bot.send_message(m.chat.id, "😔 Kechirasiz, tanlagan modellaringiz hozir omborda qolmagan. "
                             "Do'konni qayta ochib, boshqa model tanlang.", reply_markup=main_kb())
            notify_admin(f"⚠️ {h(tg_name or name)} buyurtma bermoqchi edi, lekin tovarlar omborda yo'q:\n{short_txt}")
            return

        # 3) Narx va rejimni SERVER hisoblaydi (mijoz yuborgan summaga ishonilmaydi)
        t_qty = sum(clean_ok.values())
        is_wholesale = t_qty >= WHOLESALE_MIN
        pt = "Optom" if is_wholesale else "Chakana"

        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerow(["№", "Model nomi", "Soni", "Narxi (UZS)", "Umumiy summa (UZS)"])
        payload_items, items_txt, t_sum = [], "", 0
        for idx, (item_id, q) in enumerate(clean_ok.items(), 1):
            cat = catalog[item_id]
            price = int(cat['wholesale'] if is_wholesale else cat['retail'])
            subtotal = q * price
            t_sum += subtotal
            writer.writerow([idx, cat['name'], q, price, subtotal])
            payload_items.append({"id": item_id, "n": cat['name'], "oq": q, "aq": q, "rq": q, "p": price,
                                  "asked": clean[item_id]})
            if idx <= 15:
                items_txt += f"• <b>{h(cat['name'][:30])}</b>: {q} dona\n"
            elif idx == 16:
                items_txt += f"<i>... va yana (jami {len(clean_ok)} xil model)</i>\n"
        writer.writerow([])
        writer.writerow(["", "JAMI", t_qty, "", t_sum])

        oid = next_order_id()
        save_order(cid, {"id": oid, "cid": cid, "created": now_ms(), "status": "yangi",
                         "history": [{"t": now_ms(), "s": "yangi", "by": "mijoz"}],
                         "name": name, "tg_name": tg_name, "username": m.from_user.username, "phone": phone,
                         "role": user.get('role'), "deliv": deliv, "addr": addr, "pt": pt,
                         "qty": t_qty, "total": t_sum, "items": payload_items, "note": "",
                         "stock_reserved": True})

        csv_file = io.BytesIO(csv_buffer.getvalue().encode('utf-8-sig'))
        csv_file.name = f"Buyurtma_{oid}.csv"

        client_txt = (
            f"🛒 <b>Buyurtmangiz #{oid} qabul qilindi!</b>\n━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>Mijoz:</b> {h(name)}\n📞 <b>Telefon:</b> {h(phone or 'yuborilmagan')}\n"
            f"🚚 <b>Yetkazish:</b> {h(deliv)} | 📍 {h(addr)}\n"
            f"📦 <b>Tarkibi:</b>\n{items_txt}"
            + (f"\n⚠️ <b>Omborda yetmadi:</b>\n{short_txt}" if short_txt else "") +
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"💰 <b>JAMI:</b> <b>{t_sum:,} so'm</b> ({pt} narxda, {t_qty} dona)\n\n"
            f"{PAYMENT_TEXT}\n\n{WARRANTY_TEXT}"
        )
        send_with_admin_btn(cid, client_txt)

        if not phone:
            bot.send_message(m.chat.id,
                "📞 Buyurtmangizni tasdiqlashimiz uchun telefon raqamingiz kerak. "
                "Pastdagi <b>«📱 Telefon raqamimni yuborish»</b> tugmasini bosing 👇",
                reply_markup=contact_kb(), parse_mode="HTML")

        client_ts = data.get('ts')
        mismatch = ""
        try:
            if client_ts is not None and int(client_ts) != t_sum:
                mismatch = f"\n⚠️ Ilovadagi summa boshqacha edi: {int(client_ts):,} so'm (server narxi ishlatildi)"
        except (ValueError, TypeError):
            pass

        if ADMIN_ID:
            admin_txt = (
                f"🔔 <b>YANGI BUYURTMA #{oid}</b>\n━━━━━━━━━━━━━━━━━━━\n"
                f"✍️ <b>Ism (formada):</b> {h(name)} ({h(role)})\n"
                f"{contact_line(cid, tg_name or name, m.from_user.username, phone)}\n"
                f"🚚 <b>Yetkazish:</b> {h(deliv)} | 📍 {h(addr)}\n"
                f"📊 <b>Rejim:</b> {pt}\n"
                f"📦 <b>Tovarlar:</b> {t_qty} dona ({len(clean)} xil model)\n"
                f"💰 <b>Jami summa:</b> <b>{t_sum:,} so'm</b>{h(mismatch)}\n"
                f"💬 <i>To'lovni mijoz bilan o'zingiz kelishasiz</i>\n"
                + (f"⚠️ <b>Omborda yetmadi:</b>\n{short_txt}" if short_txt else "") +
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"📥 <i>To'liq ro'yxat pastdagi Excel (.csv) faylda 👇</i>"
            )
            try:
                bot.send_document(ADMIN_ID, document=csv_file, caption=admin_txt,
                                  reply_markup=admin_order_kb(oid), parse_mode="HTML")
            except Exception as e:
                log.exception("send_document")
                notify_admin(f"⚠️ Fayl yuborishda xatolik: {h(e)}")
    except Exception as e:
        log.exception("handle_order")
        notify_admin(f"⚠️ Buyurtmani qayta ishlashda xato ({cid}): {h(e)}")
        safe_send(cid, "⚠️ Texnik xato yuz berdi. Admin bilan bog'laning, buyurtmangizni qo'lda qabul qilamiz.")


def show_missing_menu_screen(chat_id, message_id, p, cid):
    m = InlineKeyboardMarkup(row_width=1)
    for idx, it in enumerate(p.get('items', [])):
        oq, aq, n = it.get('oq', 1), it.get('aq', 1), it.get('n', '')[:22]
        if aq == oq: st = f"✅ BOR: {n} ({aq}/{oq} ta)"
        elif aq == 0: st = f"❌ YO'Q: {n} (0/{oq} ta)"
        else: st = f"⚠️ KAM: {n} ({aq}/{oq} ta)"
        m.add(InlineKeyboardButton(st, callback_data=f"ed:{cid}:{idx}"))
    m.add(InlineKeyboardButton("📤 Mijozga xabar yuborish", callback_data=f"snd_miss:{cid}"),
          InlineKeyboardButton("⬅️ Orqaga", callback_data=f"back_ord:{cid}"))
    edit_text_or_caption(chat_id, message_id, "⚠️ <b>Omborda kam yoki yo'q ekranni tanlang:</b>", m)


def edit_text_or_caption(chat_id, message_id, text, markup):
    """Buyurtma xabari hujjat (CSV) bo'lgani uchun caption tahrirlanadi."""
    try:
        bot.edit_message_caption(text, chat_id, message_id, reply_markup=markup, parse_mode="HTML")
    except Exception:
        try: bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="HTML")
        except Exception: log.exception("edit message")


@bot.callback_query_handler(func=lambda c: c.data.startswith('missing_menu:'))
@admin_only
def handle_missing_menu(c):
    cid = c.data.split(':')[1]
    p = get_payload(cid)
    if not p: return bot.answer_callback_query(c.id, "Buyurtma topilmadi!", show_alert=True)
    bot.answer_callback_query(c.id)
    show_missing_menu_screen(c.message.chat.id, c.message.message_id, p, cid)


def show_edit_item_screen(chat_id, message_id, p, idx, cid):
    it = p['items'][idx]
    oq, aq = it.get('oq', 1), it.get('aq', 1)
    m = InlineKeyboardMarkup().row(
        InlineKeyboardButton("-5", callback_data=f"st:{cid}:{idx}:-5"), InlineKeyboardButton("-1", callback_data=f"st:{cid}:{idx}:-1"),
        InlineKeyboardButton("+1", callback_data=f"st:{cid}:{idx}:1"), InlineKeyboardButton("+5", callback_data=f"st:{cid}:{idx}:5"))
    m.row(InlineKeyboardButton("❌ Yo'q (0 ta)", callback_data=f"st_set:{cid}:{idx}:0"),
          InlineKeyboardButton(f"✅ To'liq ({oq} ta)", callback_data=f"st_set:{cid}:{idx}:{oq}"))
    m.row(InlineKeyboardButton("⬅️ Ro'yxatga qaytish", callback_data=f"back_list:{cid}"))
    txt = f"🛠 <b>MODEL: {h(it.get('n'))}</b>\n📦 Buyurtma: <b>{oq} dona</b>\n✅ Mavjud: <b>{aq} dona</b>\n❌ Kam: <b>{oq-aq} dona</b>"
    edit_text_or_caption(chat_id, message_id, txt, m)


@bot.callback_query_handler(func=lambda c: c.data.startswith('ed:'))
@admin_only
def handle_edit_item(c):
    _, cid, idx = c.data.split(':')
    idx = int(idx)
    p = get_payload(cid)
    if not p or idx >= len(p.get('items', [])): return bot.answer_callback_query(c.id, "Topilmadi")
    bot.answer_callback_query(c.id)
    show_edit_item_screen(c.message.chat.id, c.message.message_id, p, idx, cid)


@bot.callback_query_handler(func=lambda c: c.data.startswith('st:') or c.data.startswith('st_set:'))
@admin_only
def handle_change_qty(c):
    action, cid, idx, val = c.data.split(':')
    idx, val = int(idx), int(val)
    p = get_payload(cid)
    if not p or idx >= len(p.get('items', [])): return bot.answer_callback_query(c.id, "Xato!")
    item = p['items'][idx]
    oq, cur = item.get('oq', 1), item.get('aq', 1)
    item['aq'] = max(0, min(oq, cur + val)) if action == 'st' else max(0, min(oq, val))
    save_order(cid, p)
    bot.answer_callback_query(c.id, f"Mavjud: {item['aq']} ta")
    show_edit_item_screen(c.message.chat.id, c.message.message_id, p, idx, cid)


@bot.callback_query_handler(func=lambda c: c.data.startswith('back_list:'))
@admin_only
def handle_back_list(c):
    bot.answer_callback_query(c.id)
    cid = c.data.split(':')[1]
    p = get_payload(cid)
    if p: show_missing_menu_screen(c.message.chat.id, c.message.message_id, p, cid)


def order_summary(p):
    s_tot = sum(it.get('aq', it.get('oq', 1)) * it.get('p', 0) for it in p.get('items', []))
    q_tot = sum(it.get('aq', it.get('oq', 1)) for it in p.get('items', []))
    return s_tot, q_tot


@bot.callback_query_handler(func=lambda c: c.data.startswith('back_ord:'))
@admin_only
def handle_back_ord(c):
    bot.answer_callback_query(c.id)
    cid = c.data.split(':')[1]
    p = get_payload(cid)
    if not p: return
    s_tot, q_tot = order_summary(p)
    txt = (f"🔔 <b>BUYURTMA #{h(p.get('id', ''))}: {h(p.get('name'))}</b>\n━━━━━━━━━━━━━━━━━━━\n"
           f"{contact_line(cid, p.get('tg_name') or p.get('name'), p.get('username'), p.get('phone'))}\n"
           f"🚚 <b>Yetkazish:</b> {h(p.get('deliv'))} | 📍 {h(p.get('addr'))}\n"
           f"📊 <b>Rejim:</b> {h(p.get('pt'))}\n"
           f"📦 <b>Jami soni:</b> {q_tot} dona\n"
           f"💰 <b>Qayta hisoblangan summa:</b> <b>{s_tot:,} so'm</b>")
    edit_text_or_caption(c.message.chat.id, c.message.message_id, txt, admin_order_kb(cid))


@bot.callback_query_handler(func=lambda c: c.data.startswith('snd_miss:'))
@admin_only
def handle_snd_miss(c):
    cid = c.data.split(':')[1]
    p = get_payload(cid)
    if not p: return bot.answer_callback_query(c.id, "Buyurtma topilmadi!")
    items = p.get('items', [])
    if not any(it.get('aq', it.get('oq')) < it.get('oq') for it in items):
        return bot.answer_callback_query(c.id, "Hamma tovar yetarli!", show_alert=True)
    miss_t = part_t = av_t = ""
    for it in items:
        oq, aq, pr, n = it.get('oq', 1), it.get('aq', 1), it.get('p', 0), h(it.get('n'))
        if aq == 0: miss_t += f"❌ <b>{n}</b> — umuman yo'q\n"
        elif aq < oq: part_t += f"⚠️ <b>{n}</b> — {oq} ta so'ralgan, <b>{aq} ta bor</b>\n"
        else: av_t += f"✅ <b>{n}</b> — {aq} dona ({aq * pr:,} so'm)\n"
    n_sum, n_qty = order_summary(p)
    if p.get("stock_reserved") and not p.get("stock_returned"):
        for it in items:  # omborda yo'q deb belgilangan qismini qoldiqqa qaytaramiz
            extra = int(it.get("rq", it.get("oq", 0)) or 0) - int(it.get("aq", 0) or 0)
            if extra > 0:
                stock_add(it["id"], extra)
                it["rq"] = it.get("aq", 0)
    if p.get("id"):
        p["total"], p["qty"] = n_sum, n_qty
        p.setdefault("history", []).append({"t": now_ms(), "s": p.get("status", "yangi"), "by": "admin",
                                            "note": f"Tarkib o'zgardi: {n_qty} ta, {n_sum:,} so'm"})
        save_order(p["cid"], p)
    msg = (f"⚠️ <b>DIQQAT: AYRIM MODELLAR OMBORDA KAM YOKI YO'Q!</b>\n━━━━━━━━━━━━━━━━━━━\n"
           f"{miss_t}{part_t}━━━━━━━━━━━━━━━━━━━\n"
           f"📦 <b>Bor tovarlar:</b>\n{av_t or 'Qolmadi'}\n━━━━━━━━━━━━━━━━━━━\n"
           f"💰 <b>Qayta hisoblangan summa:</b> <b>{n_sum:,} so'm</b> ({n_qty} ta)\n\n"
           f"{PAYMENT_TEXT}\n\n{WARRANTY_TEXT}")
    send_with_admin_btn(order_cid(cid, p), msg)
    edit_text_or_caption(c.message.chat.id, c.message.message_id,
                         f"✅ <b>Mijozga xabar ketdi!</b>\n💰 Yangi summa: <b>{n_sum:,} so'm</b> ({n_qty} ta)", admin_order_kb(cid))
    bot.answer_callback_query(c.id, "Mijozga yuborildi!")


@bot.message_handler(content_types=['photo'])
def handle_receipt(m):
    cid = str(m.chat.id)
    if is_admin(cid):
        return
    phone = get_user(cid).get('phone')
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton("✅ Bugun yetkazish", callback_data=f"pay:{cid}:today"),
           InlineKeyboardButton("✅ Ertaga yetkazish", callback_data=f"pay:{cid}:tomorrow"),
           InlineKeyboardButton("❌ To'lov tushmadi", callback_data=f"pay:{cid}:fake"))
    try:
        bot.send_photo(ADMIN_ID, m.photo[-1].file_id,
                       caption=f"📷 <b>MIJOZDAN RASM KELDI</b> {('#' + h(get_payload(cid).get('id', ''))) if get_payload(cid) else ''}\n{contact_line(cid, m.from_user.first_name, m.from_user.username, phone)}",
                       reply_markup=kb, parse_mode="HTML")
        set_status(get_payload(cid), "chek", by="mijoz")
        bot.reply_to(m, "✅ Rasm adminga yuborildi, tez orada javob beradi.")
    except Exception:
        log.exception("receipt forward")
        bot.reply_to(m, "⚠️ Rasmni yuborib bo'lmadi, birozdan keyin qayta yuboring.")


PAY_TEXTS = {
    "today": "🎉 Tasdiqlandi! BUGUN yetkaziladi.",
    "tomorrow": "🎉 Tasdiqlandi! ERTAGA yetkaziladi.",
    "cash": "🤝 Tasdiqlandi! To'lov kelishilgandek olinadi.",
    "fake": "⚠️ To'lov hali tushmadi. Iltimos, admin bilan bog'laning.",
    "cancel": "❌ Buyurtma bekor qilindi.",
}

@bot.callback_query_handler(func=lambda c: c.data.startswith('pay:'))
@admin_only
def process_pay(c):
    _, cid, act = c.data.split(':')
    if act not in PAY_TEXTS:
        return bot.answer_callback_query(c.id)
    p = get_payload(cid)
    if p and p.get("id"):
        st = {"today": "tasdiqlandi", "tomorrow": "tasdiqlandi", "cash": "tasdiqlandi",
              "cancel": "bekor", "fake": "yangi"}[act]
        set_status(p, st, note=PAY_TEXTS[act], by="admin")
    safe_send(order_cid(cid, p), f"🔔 {PAY_TEXTS[act]}")
    bot.answer_callback_query(c.id, "Xabar ketdi!")
    try: bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=None)
    except Exception: pass


# ===================== ADMIN PANEL =====================
def _panel_key():
    return (WEBHOOK_SECRET or BOT_TOKEN).encode()

def make_admin_token(days=30):
    exp = int(time.time()) + days * 86400
    sig = hmac.new(_panel_key(), f"admin:{exp}".encode(), hashlib.sha256).hexdigest()[:40]
    return f"{exp}.{sig}"

def check_admin_token(tok):
    try:
        exp, sig = tok.split(".", 1)
        good = hmac.new(_panel_key(), f"admin:{int(exp)}".encode(), hashlib.sha256).hexdigest()[:40]
        return int(exp) > time.time() and hmac.compare_digest(sig, good)
    except Exception:
        return False

@bot.message_handler(commands=['panel'])
def handle_panel(m):
    if not is_admin(m.chat.id):
        return
    url = f"{PUBLIC_URL}/admin?k={make_admin_token()}"
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📊 Admin panelni ochish", web_app=WebAppInfo(url=url)))
    bot.send_message(m.chat.id,
        "📊 <b>Admin panel</b>\nTugma orqali Telegram ichida oching.\n\n"
        f"Kompyuterda ochish uchun havola (30 kun amal qiladi, hech kimga bermang):\n<code>{h(url)}</code>",
        reply_markup=kb, parse_mode="HTML")

def public_catalog():
    cat = get_catalog()
    items = sorted(cat.values(), key=lambda p: (-int(p.get("stock", 0) > 0), int(p["id"]) if str(p["id"]).isdigit() else 0))
    resp = jsonify({"products": [{k: p.get(k) for k in ("id", "brand", "type", "name", "retail", "wholesale", "stock")} for p in items],
                    "wholesale_min": WHOLESALE_MIN, "now": now_ms()})
    resp.headers["Cache-Control"] = "public, s-maxage=10, stale-while-revalidate=30"
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


def _int_or_none(v):
    try:
        return int(round(float(v)))
    except (TypeError, ValueError):
        return None


def admin_api():
    tok = request.headers.get("X-Admin-Token", "")
    if not check_admin_token(tok):
        return jsonify({"error": "Kirish muddati tugagan. Botga /panel yozib, yangi havola oling."}), 401
    action = request.args.get("admin")
    if action == "data" and request.method == "GET":
        orders = [o for o in store_all("orders2").values() if isinstance(o, dict) and o.get("id")]
        orders.sort(key=lambda o: o.get("created", 0), reverse=True)
        users = store_all("users")
        customers = [{"cid": str(k), **v} for k, v in users.items() if isinstance(v, dict)]
        return jsonify({"orders": orders, "customers": customers, "statuses": STATUSES, "now": now_ms(),
                        "persistent": bool(REDIS_URL)})
    if action == "catalog" and request.method == "GET":
        cat = get_catalog(include_hidden=True)
        return jsonify({"products": sorted(cat.values(), key=lambda p: int(p["id"]) if str(p["id"]).isdigit() else 0)})
    if action == "catalog_save" and request.method == "POST":
        body = request.get_json(silent=True) or {}
        cat = get_catalog(include_hidden=True)
        changed, stock_set, errors = {}, {}, []
        for ch in (body.get("changes") or [])[:1000]:
            pid = str(ch.get("id", "")).strip()
            is_new = pid == "" or pid == "new"
            if is_new:
                nums = [int(k) for k in cat if str(k).isdigit()] + [int(k) for k in changed if str(k).isdigit()]
                pid = str(max(nums or [0]) + 1)
                base = {"brand": "", "type": "", "name": "", "retail": 0, "wholesale": 0, "active": True}
            elif pid in cat:
                base = {k: cat[pid].get(k) for k in PRODUCT_FIELDS}
            else:
                errors.append(f"{pid}: topilmadi"); continue
            for k in ("brand", "type", "name"):
                if k in ch: base[k] = str(ch[k]).strip()[:200]
            for k in ("retail", "wholesale"):
                if k in ch:
                    v = _int_or_none(ch[k])
                    if v is None or v < 0: errors.append(f"{base.get('name') or pid}: narx noto'g'ri"); break
                    base[k] = v
            else:
                if "active" in ch: base["active"] = bool(ch["active"])
                if not base.get("name") or not base.get("brand"):
                    errors.append(f"{pid}: nom va brend kerak"); continue
                if base["wholesale"] > base["retail"]:
                    errors.append(f"{base['name']}: optom narx chakanadan qimmat"); continue
                changed[pid] = base
                if "stock" in ch:
                    v = _int_or_none(ch["stock"])
                    if v is None or v < 0: errors.append(f"{base['name']}: qoldiq noto'g'ri"); continue
                    stock_set[pid] = v
        if errors:
            return jsonify({"error": "Saqlanmadi: " + "; ".join(errors[:5])}), 400
        restocked = [pid for pid, v in stock_set.items()
                     if v > 0 and int((cat.get(pid) or {}).get("stock", 0) or 0) <= 0
                     and changed.get(pid, {}).get("active", True) is not False]
        # yashirilgan mahsulot qayta yoqilganda ham xabar beriladi
        restocked += [pid for pid, b in changed.items()
                      if b.get("active") is not False and (cat.get(pid) or {}).get("active") is False
                      and stock_set.get(pid, int((cat.get(pid) or {}).get("stock", 0) or 0)) > 0 and pid not in restocked]
        _set_many("catalog", changed)
        _set_many("stock", stock_set)
        if restocked:
            try:
                notify_restock(restocked)
            except Exception:
                log.exception("notify_restock")
        log.info("Katalog yangilandi: %d mahsulot, %d qoldiq", len(changed), len(stock_set))
        return jsonify({"ok": True, "saved": len(changed), "products": list(get_catalog(include_hidden=True).values())})
    if action == "update" and request.method == "POST":
        body = request.get_json(silent=True) or {}
        p = get_order(str(body.get("id", "")))
        if not p:
            return jsonify({"error": "Buyurtma topilmadi"}), 404
        if "note" in body:
            p["note"] = str(body["note"])[:500]
            save_order(p["cid"], p)
        st = body.get("status")
        if st and st != p.get("status"):
            if st not in STATUSES:
                return jsonify({"error": "Noto'g'ri holat"}), 400
            set_status(p, st, by="panel")
            if body.get("notify") and st in STATUS_CUSTOMER_MSG:
                safe_send(p["cid"], STATUS_CUSTOMER_MSG[st].format(id=h(p["id"])), parse_mode="HTML")
        return jsonify({"ok": True, "order": p})
    return jsonify({"error": "Noma'lum so'rov"}), 400


# ===================== WEBHOOK =====================
@app.route('/', defaults={'path': ''}, methods=['POST', 'GET'])
@app.route('/<path:path>', methods=['POST', 'GET'])
def webhook(path):
    if "catalog" in request.args and request.method == "GET":
        return public_catalog()
    if "admin" in request.args:
        return admin_api()
    if request.method == 'GET':
        if "ulash" in request.args or path.rstrip("/").endswith("ulash"):
            return do_ulash()
        return "✅ Ekranchi bot ishlayapti.", 200
    token = request.headers.get('X-Telegram-Bot-Api-Secret-Token', '')
    if not WEBHOOK_SECRET or not hmac.compare_digest(token, WEBHOOK_SECRET):
        return "Forbidden", 403
    if not (request.headers.get('content-type') or '').startswith('application/json'):
        return "Bad request", 400
    try:
        bot.process_new_updates([telebot.types.Update.de_json(request.get_data().decode('utf-8'))])
    except Exception:
        log.exception("process update")
    return jsonify({"status": "ok"}), 200
