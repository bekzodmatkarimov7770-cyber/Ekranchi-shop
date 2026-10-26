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

# Boshlang'ich katalog: baza bo'sh bo'lsa yoki CATALOG_VERSION o'zgarsa yoziladi. Keyin narx va qoldiq admin paneldan boshqariladi.
# Manba: PRICE 21.10.2026. Optom = tannarx + ustama (PRICE_VERSION izohiga qarang, minggacha yuqoriga), chakana = optom x 1,35; qoldig'i 0 bo'lganlar yo'q.
# ID lar 1001 dan boshlanadi, eski buyurtmalardagi ID lar (1-456) yangi mahsulotlarga tushib qolmasin.
CATALOG_VERSION = "2026-10-21"
# Faqat narxlar yangilanganda: qoldiq, yashirilgan mahsulotlar va nomlar bazada qoladi, optom va chakana SEED_CATALOG dan olinadi.
# 26.10: hammasiga tannarx + 5 000 (avvalgi 3 000 + 2 000), OLED/Servis (FOG) +25 000, tannarx 250 000+ bo'lsa +50 000.
PRICE_VERSION = "2026-10-26"
SEED_CATALOG = [
    {"id": "1001", "brand": "Samsung", "type": "IPS LCD", "name": "A02S / A03S / A03 / A035 / A025 / A04E / A042", "retail": 79000, "wholesale": 58000, "stock": 3114},
    {"id": "1002", "brand": "Redmi", "type": "Incell HD+", "name": "POCO M3 / 9T", "retail": 84000, "wholesale": 62000, "stock": 1391},
    {"id": "1003", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE8 PRO", "retail": 87000, "wholesale": 64000, "stock": 1299},
    {"id": "1004", "brand": "Samsung", "type": "IPS LCD", "name": "A10 2019 / A105 / M10 / M105", "retail": 80000, "wholesale": 59000, "stock": 1284},
    {"id": "1005", "brand": "Vivo", "type": "Incell HD+", "name": "Y21T / Y16 / y21 / Y15A / Y15S / Y21A / Y21e / Y21G / Y21S / Y33E / Y31S / Y32 / Y01 / Y02S", "retail": 81000, "wholesale": 60000, "stock": 1187},
    {"id": "1006", "brand": "Redmi", "type": "Premium", "name": "9C / 9A / 10A / 9I / POCO C3 / POCO C31", "retail": 96000, "wholesale": 71000, "stock": 1071},
    {"id": "1007", "brand": "Redmi", "type": "Incell HD+", "name": "13C 4G / 13C 5G / POCO C65 / 13R / POCO M6 5G", "retail": 84000, "wholesale": 62000, "stock": 1061},
    {"id": "1008", "brand": "Samsung", "type": "IPS LCD", "name": "A10S 2020 / A107", "retail": 79000, "wholesale": 58000, "stock": 950},
    {"id": "1009", "brand": "Redmi", "type": "Incell HD+", "name": "11A / POCO C55 / A11 / 12C", "retail": 86000, "wholesale": 63000, "stock": 942},
    {"id": "1010", "brand": "Redmi", "type": "Incell HD+", "name": "9 / 9 PRIME / POCO M2", "retail": 84000, "wholesale": 62000, "stock": 876},
    {"id": "1011", "brand": "Samsung", "type": "IPS LCD", "name": "A20S 2020 / A207", "retail": 81000, "wholesale": 60000, "stock": 843},
    {"id": "1012", "brand": "Redmi", "type": "Incell HD+", "name": "10X / NOTE 9", "retail": 88000, "wholesale": 65000, "stock": 752},
    {"id": "1013", "brand": "Samsung", "type": "IPS LCD", "name": "J4+ / J6+ / J415 / J610 / J410", "retail": 79000, "wholesale": 58000, "stock": 738},
    {"id": "1014", "brand": "Samsung", "type": "IPS LCD", "name": "A01CORE / A013 / A3CORE", "retail": 81000, "wholesale": 60000, "stock": 671},
    {"id": "1015", "brand": "Redmi", "type": "Incell HD+", "name": "A1 / A1+ / C51 / C50 / A2 / A2+", "retail": 79000, "wholesale": 58000, "stock": 564},
    {"id": "1016", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE 8", "retail": 87000, "wholesale": 64000, "stock": 552},
    {"id": "1017", "brand": "Redmi", "type": "Incell HD+", "name": "10 4G / 10-2022 / 10 prime / 10prime 2022", "retail": 88000, "wholesale": 65000, "stock": 550},
    {"id": "1018", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "X662B / Hot11 / X662 / Spark8P / KG7 / Spark8t / KG7n / KG7h / KG6P / KH7 / KH7H / KH7N / S18pro / S662L / vision5plus / S662LC / SPARK9PRO / X666B", "retail": 86000, "wholesale": 63000, "stock": 536},
    {"id": "1019", "brand": "Redmi", "type": "Incell HD+", "name": "15C 4G", "retail": 91000, "wholesale": 67000, "stock": 528},
    {"id": "1020", "brand": "Tecno & Infinix", "type": "Premium", "name": "BE8 / X668 / KG5K / HOT12 / X665C / Hot20i / POP6 Pro / KG5Q / TECNO SPARK8C / KG5j / SPARK 8C / KG5p / SPARK9 / KH6 / SPARK 9T / X6512 / SMART 6HD / X665 / Hot 12i / X665B / HOT12 PRO", "retail": 100000, "wholesale": 74000, "stock": 523},
    {"id": "1021", "brand": "Redmi", "type": "Incell HD+", "name": "A5 4G / A5 5G / A5 New / Poco C71", "retail": 88000, "wholesale": 65000, "stock": 493},
    {"id": "1022", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "X657 / x657B / C / S16 / P36 / P36pro / Smart5 / SparkGo 2020 / Hot10lite / W6501 / W6502 / L6502 / Vision1pro / L6501 / Vision1plus", "retail": 79000, "wholesale": 58000, "stock": 450},
    {"id": "1023", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "BD4 / KG5 / X6511 / X6511B / X6511S / SMART6 / BD4A / BD4I / BD4J / BD4H / KG5M / KG5H / SPARK GO2022 / POP5LTE / POP5PRO / BD4T / X6511E", "retail": 80000, "wholesale": 59000, "stock": 446},
    {"id": "1024", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE10 5G / Note11SE / Note10T 5G / POCO M3 PRO", "retail": 90000, "wholesale": 66000, "stock": 429},
    {"id": "1025", "brand": "Oppo", "type": "Incell HD+", "name": "A11X / A5 2020 / C3i / narzo 20A / A9 2020 / A31 2020 / realmeC3 / Realme5 / Realme5S / narzo10A / A8 2020 / Realme6 / Realme6i / Realme7", "retail": 79000, "wholesale": 58000, "stock": 418},
    {"id": "1026", "brand": "Samsung", "type": "IPS LCD", "name": "A01F 2020 / A015", "retail": 81000, "wholesale": 60000, "stock": 406},
    {"id": "1027", "brand": "Samsung", "type": "IPS LCD", "name": "A13 5G / A04S / A136U / A047 / A04CORE / A136B", "retail": 79000, "wholesale": 58000, "stock": 401},
    {"id": "1028", "brand": "Redmi", "type": "Incell HD+", "name": "POCO C40 / 10 POWER / 10INDIA / 10C", "retail": 84000, "wholesale": 62000, "stock": 398},
    {"id": "1029", "brand": "Samsung", "type": "IPS LCD", "name": "A2Core / A260", "retail": 73000, "wholesale": 54000, "stock": 371},
    {"id": "1030", "brand": "Samsung", "type": "IPS LCD", "name": "A135F / A13 4G / A13 LITE / A135 / A137 / F13 / M13", "retail": 79000, "wholesale": 58000, "stock": 371},
    {"id": "1031", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "HOT12 / X6817 / X6816 / X6816C / HOT12PLAY / X6816D / HOT12PLAYNFC / X6817B / X6819 / NOTE12I / LG7N / POVA4 / X6825 / HOT20PLAY / X6826 / X6826B / X6826C / HOT20 / LG6 / LG6N / POVANEO2 / LH6N / POVANEO3 / X6835B / HOT30PLAY / P683L / P40PLUS / 6835", "retail": 90000, "wholesale": 66000, "stock": 371},
    {"id": "1032", "brand": "Samsung", "type": "IPS LCD", "name": "A07 4G", "retail": 87000, "wholesale": 64000, "stock": 359},
    {"id": "1033", "brand": "Xiaomi", "type": "Incell HD+", "name": "MI 9T / MI9T PRO / K20 / K20 PRO", "retail": 98000, "wholesale": 72000, "stock": 356},
    {"id": "1034", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "X6882 / HOT50 / KL6 / SPARK30 / SPARK30 4G / HOT50 4G", "retail": 99000, "wholesale": 73000, "stock": 340},
    {"id": "1035", "brand": "Samsung", "type": "IPS LCD", "name": "A06 4G / A065", "retail": 86000, "wholesale": 63000, "stock": 324},
    {"id": "1036", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "S17 / A58 / A58PRO 4G / A49 / A661 / A661L / S661W / KG6K / X6511G / X6511C / X6511D / SMART6+ / SPARK8", "retail": 80000, "wholesale": 59000, "stock": 309},
    {"id": "1037", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE14 PRO 4G WF", "retail": 158000, "wholesale": 117000, "stock": 304},
    {"id": "1038", "brand": "Samsung", "type": "Premium", "name": "A52 / A525 A52 4G WF", "retail": 173000, "wholesale": 128000, "stock": 300},
    {"id": "1039", "brand": "Redmi", "type": "Incell HD+", "name": "12R / Note13R / 12 / 12 5G / 13 / 13 5G / POCO M6PRO 5G", "retail": 92000, "wholesale": 68000, "stock": 299},
    {"id": "1040", "brand": "Samsung", "type": "Premium", "name": "A166 / A16 5G WF", "retail": 131000, "wholesale": 97000, "stock": 298},
    {"id": "1041", "brand": "Samsung", "type": "Premium", "name": "A06 4G / A065", "retail": 104000, "wholesale": 77000, "stock": 297},
    {"id": "1042", "brand": "Samsung", "type": "Premium", "name": "A11 2020 / A115", "retail": 103000, "wholesale": 76000, "stock": 294},
    {"id": "1043", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE11 5G / NOTE11T 5G / NOTE11S 5G / POCO M4 PRO 5G", "retail": 103000, "wholesale": 76000, "stock": 294},
    {"id": "1044", "brand": "Vivo", "type": "Premium", "name": "Y33S / Y76 5G / Y74S / Y76S / Y52S 5G / Y53S / Y51-2020 / Y31 2020 / Y51A / Y72 5g / Y55 5G / T1 5G / Y72t / Y55s / Y75 5g / Y77 5G / T2X 5G / Y56 5g", "retail": 100000, "wholesale": 74000, "stock": 285},
    {"id": "1045", "brand": "Samsung", "type": "IPS LCD", "name": "A05 / A055F / M05", "retail": 88000, "wholesale": 65000, "stock": 273},
    {"id": "1046", "brand": "Redmi", "type": "Premium", "name": "NOTE11 4G WF", "retail": 145000, "wholesale": 107000, "stock": 273},
    {"id": "1047", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "SMART5", "retail": 87000, "wholesale": 64000, "stock": 269},
    {"id": "1048", "brand": "Xiaomi", "type": "Incell HD+", "name": "POCO X3 / X3 PRO / NOTE9 PRO 5G / MI10T LITE 5G", "retail": 98000, "wholesale": 72000, "stock": 267},
    {"id": "1049", "brand": "Redmi", "type": "Incell HD+", "name": "6 / 6A", "retail": 86000, "wholesale": 63000, "stock": 262},
    {"id": "1050", "brand": "Redmi", "type": "Incell HD+", "name": "14C 4G / 14C 5G / Poco C75", "retail": 87000, "wholesale": 64000, "stock": 254},
    {"id": "1051", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "HOT40PRO / HOT40", "retail": 99000, "wholesale": 73000, "stock": 253},
    {"id": "1052", "brand": "Samsung", "type": "Premium", "name": "A10S 2020 / A107", "retail": 99000, "wholesale": 73000, "stock": 252},
    {"id": "1053", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE 9S / NOTE9 PRO 4G / NOTE9 PROMAX / NOTE10 LITE / XM POCO M2 PRO", "retail": 95000, "wholesale": 70000, "stock": 250},
    {"id": "1054", "brand": "Samsung", "type": "IPS LCD", "name": "M23", "retail": 87000, "wholesale": 64000, "stock": 238},
    {"id": "1055", "brand": "Xiaomi", "type": "Incell HD+", "name": "MI 11T / MI11T PRO", "retail": 119000, "wholesale": 88000, "stock": 226},
    {"id": "1056", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "NOTE30I / SPARK20SPRO", "retail": 99000, "wholesale": 73000, "stock": 225},
    {"id": "1057", "brand": "Redmi", "type": "Incell HD+", "name": "8 / 8A", "retail": 86000, "wholesale": 63000, "stock": 222},
    {"id": "1058", "brand": "Samsung", "type": "TFT", "name": "S10+WF", "retail": 222000, "wholesale": 164000, "stock": 221},
    {"id": "1059", "brand": "Realme", "type": "Incell HD+", "name": "C20 / C21 / C11 2021 / NARZO 50I", "retail": 84000, "wholesale": 62000, "stock": 219},
    {"id": "1060", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE13PRO 4G WF", "retail": 167000, "wholesale": 123000, "stock": 218},
    {"id": "1061", "brand": "Samsung", "type": "IPS LCD", "name": "A23 4G / A235 / M336", "retail": 90000, "wholesale": 66000, "stock": 214},
    {"id": "1062", "brand": "Redmi", "type": "Incell HD+", "name": "15 4G / 5G", "retail": 102000, "wholesale": 75000, "stock": 208},
    {"id": "1063", "brand": "Samsung", "type": "IPS LCD", "name": "A05S / A057", "retail": 95000, "wholesale": 70000, "stock": 204},
    {"id": "1064", "brand": "Samsung", "type": "IPS LCD", "name": "M336 / A23 4G / A235 / M236 / A13 4G / M135 / A137gaoshua", "retail": 104000, "wholesale": 77000, "stock": 200},
    {"id": "1065", "brand": "Samsung", "type": "Premium", "name": "A05S / A057", "retail": 113000, "wholesale": 83000, "stock": 200},
    {"id": "1066", "brand": "Samsung", "type": "Premium", "name": "A53 / A535 WF", "retail": 168000, "wholesale": 124000, "stock": 200},
    {"id": "1067", "brand": "Redmi", "type": "Premium", "name": "NOTE12PRO WF", "retail": 145000, "wholesale": 107000, "stock": 200},
    {"id": "1068", "brand": "Samsung", "type": "Premium", "name": "A14 4G / A145P / A145B", "retail": 99000, "wholesale": 73000, "stock": 197},
    {"id": "1069", "brand": "Samsung", "type": "Premium", "name": "A17WF", "retail": 129000, "wholesale": 95000, "stock": 197},
    {"id": "1070", "brand": "Redmi", "type": "Premium", "name": "NOTE12 4G WF", "retail": 145000, "wholesale": 107000, "stock": 195},
    {"id": "1071", "brand": "Honor", "type": "Premium", "name": "X6B", "retail": 106000, "wholesale": 78000, "stock": 195},
    {"id": "1072", "brand": "Redmi", "type": "Premium", "name": "NOTE13 4G WF", "retail": 165000, "wholesale": 122000, "stock": 194},
    {"id": "1073", "brand": "Vivo", "type": "Incell HD+", "name": "Y3 / Y13 / Y3S / Y11 / Y12 / Y15 / Y17 / U3X / U10 / 8A", "retail": 91000, "wholesale": 67000, "stock": 190},
    {"id": "1074", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "X655 / X655C.D.F / CD7 / CD7H / CD6 / CD6J.S / KD7 / KD7S.H / HOT9 / HOT9PRO / SPARK5 / SPARK5PRO / Camon5 / Camon 5air / Note 7lite / X656", "retail": 84000, "wholesale": 62000, "stock": 189},
    {"id": "1075", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "X682 / X682B / X682C / HOT10 / X683C / X683 / CE7 / CE7J / LD7 / LD7J / KE7 / SPARK6 / Pova / Note8i / Camon16 / Camon16SE", "retail": 94000, "wholesale": 69000, "stock": 189},
    {"id": "1076", "brand": "Redmi", "type": "Premium", "name": "A2 LITE / 6PRO", "retail": 110000, "wholesale": 81000, "stock": 188},
    {"id": "1077", "brand": "Oppo", "type": "Incell HD+", "name": "A16 / A16S / A16K / A15 / A15S / A35 / C11 / C12 / C15 / C25 / C25S / A54S / A56 4G / 5G / A55 5G", "retail": 83000, "wholesale": 61000, "stock": 188},
    {"id": "1078", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "HOT11S / X6812 / X6832 / X6833 / X6815 / X6836 / X6837 / X6711 / CH6 / CG7 / Camon17PRO / CH7 / POVA6NEO / Camon18PRO / CI8 / KI7 / LI6 / KG8 / SPARK8PRO / KJ6 / KJ8 / HOT40 / SPARK20PRO / Spark10pro", "retail": 92000, "wholesale": 68000, "stock": 181},
    {"id": "1079", "brand": "Redmi", "type": "Premium", "name": "5PLUS", "retail": 98000, "wholesale": 72000, "stock": 176},
    {"id": "1080", "brand": "Honor", "type": "Premium", "name": "X7B", "retail": 119000, "wholesale": 88000, "stock": 169},
    {"id": "1081", "brand": "Samsung", "type": "IPS LCD", "name": "A04 / A045", "retail": 79000, "wholesale": 58000, "stock": 168},
    {"id": "1082", "brand": "Redmi", "type": "Incell HD+", "name": "7A", "retail": 86000, "wholesale": 63000, "stock": 168},
    {"id": "1083", "brand": "Xiaomi", "type": "Incell HD+", "name": "F3 / F4 / Mi 11i / Mi11x / Mi11x Pro / Shark 4 / 4Pro", "retail": 107000, "wholesale": 79000, "stock": 168},
    {"id": "1084", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "NOTE11 / NOTE12", "retail": 95000, "wholesale": 70000, "stock": 166},
    {"id": "1085", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "BD3 / KF6 / KF6H / KF6i / KF6J / KG6 / X659 / X659B / Spark7 / PR651 / PR651H / POP5P / Smart5Pro / PR652B / P37 / Vision2S / P651L / HOT10i / X658B", "retail": 83000, "wholesale": 61000, "stock": 165},
    {"id": "1086", "brand": "Vivo", "type": "Incell HD+", "name": "IQ00 Z7x(m) / VIVO Y100i / VIVO Y78m / IQ00 Z7 / VIVO Y78 / IQ00 Z7X / IQ00 Z8 / IQ00 Z8x / VIVO Y77T-5G / VIVO Y78T / VIVO Y78（t1） / VIVO Y100T / VIVO Y36-4G / VIVO Y36 5G", "retail": 88000, "wholesale": 65000, "stock": 164},
    {"id": "1087", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "KE5 / KE5J / KE5K / SPARK6GO / KE5S", "retail": 84000, "wholesale": 62000, "stock": 151},
    {"id": "1088", "brand": "Redmi", "type": "Incell HD+", "name": "A3 / A3X / POCO C61(yin du)", "retail": 84000, "wholesale": 62000, "stock": 150},
    {"id": "1089", "brand": "Redmi", "type": "Premium", "name": "NOTE10 4G WF", "retail": 137000, "wholesale": 101000, "stock": 150},
    {"id": "1090", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE13 PRO 4G", "retail": 108000, "wholesale": 80000, "stock": 149},
    {"id": "1091", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "X688 / LE6 / X688B / HOT10PLAY / X688C / P37PRO / HOT11PLAY / POVANEO / LE6H / P681L / VOSON2+", "retail": 92000, "wholesale": 68000, "stock": 143},
    {"id": "1092", "brand": "Realme", "type": "Incell HD+", "name": "C11 / A16 / A55 / A57 / C35 / Narzo20 / Narzo30a / V3 / C15 / Rearlme 7i", "retail": 83000, "wholesale": 61000, "stock": 133},
    {"id": "1093", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "X689 / KF7J / X689D / X689F / X689C / X689B / SPARK7P / HOT10T / HOT10S / SMART6PLUS / X6823 / P38PRO / VISION3+ / X6823C / P682LP / KF7", "retail": 92000, "wholesale": 68000, "stock": 131},
    {"id": "1094", "brand": "Honor", "type": "Premium", "name": "RY X8C", "retail": 234000, "wholesale": 173000, "stock": 129},
    {"id": "1095", "brand": "Xiaomi", "type": "Incell HD+", "name": "MI 8 LITE", "retail": 95000, "wholesale": 70000, "stock": 127},
    {"id": "1096", "brand": "Samsung", "type": "IPS LCD", "name": "A31 2020 / A315-WF", "retail": 121000, "wholesale": 89000, "stock": 123},
    {"id": "1097", "brand": "Redmi", "type": "Premium", "name": "POCO X4 GT", "retail": 114000, "wholesale": 84000, "stock": 122},
    {"id": "1098", "brand": "Samsung", "type": "IPS LCD", "name": "A36 / A56", "retail": 107000, "wholesale": 79000, "stock": 118},
    {"id": "1099", "brand": "Vivo", "type": "Incell HD+", "name": "Y20 / Y20I / Y20S / Y15A / Y15S / Y11S / Y12S / Y12A / (NEIDAN)Y30 / Y30G / Y31S / IQOOU1X / Y10-(T1 / T2) / Y02", "retail": 83000, "wholesale": 61000, "stock": 118},
    {"id": "1100", "brand": "Samsung", "type": "Premium", "name": "A336 / A33 WF", "retail": 157000, "wholesale": 116000, "stock": 117},
    {"id": "1101", "brand": "Redmi", "type": "Incell HD+", "name": "7 / Y3", "retail": 92000, "wholesale": 68000, "stock": 117},
    {"id": "1102", "brand": "Xiaomi", "type": "Incell HD+", "name": "MI 8", "retail": 127000, "wholesale": 94000, "stock": 116},
    {"id": "1103", "brand": "Honor", "type": "Incell HD+", "name": "RY X9", "retail": 106000, "wholesale": 78000, "stock": 111},
    {"id": "1104", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "Note11 / X663(B / C / D) / X6716 / X670 / Note12 5G(X671) / Note12pro 4G / 5G(X676B) / Note20 / X676C / Note12i / X677", "retail": 98000, "wholesale": 72000, "stock": 109},
    {"id": "1105", "brand": "Samsung", "type": "Premium", "name": "A325 / A32 4G / A32LITE", "retail": 108000, "wholesale": 80000, "stock": 108},
    {"id": "1106", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "X650 / X650D / X650B / X650C / KC8 / KC8S / CC7 / CC7S / KC2 / KC2J / HOT8 / HOT8LITE / CAMON12 / SPARK4", "retail": 83000, "wholesale": 61000, "stock": 107},
    {"id": "1107", "brand": "Samsung", "type": "IPS LCD", "name": "A6 2018 / A600", "retail": 90000, "wholesale": 66000, "stock": 104},
    {"id": "1108", "brand": "Redmi", "type": "Incell HD+", "name": "POCO X3 GT / NOTE10PRO 5G", "retail": 103000, "wholesale": 76000, "stock": 104},
    {"id": "1109", "brand": "Samsung", "type": "IPS LCD", "name": "A34 4G-WF", "retail": 154000, "wholesale": 114000, "stock": 103},
    {"id": "1110", "brand": "Samsung", "type": "OLED", "name": "A325 / A32 4G / M32 / M325 / F325 / A32LITE", "retail": 310000, "wholesale": 229000, "stock": 101},
    {"id": "1111", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "KJ6 / SPARK20PRO", "retail": 99000, "wholesale": 73000, "stock": 101},
    {"id": "1112", "brand": "Honor", "type": "Premium", "name": "X50I / X8A / X8 2023", "retail": 111000, "wholesale": 82000, "stock": 99},
    {"id": "1113", "brand": "Honor", "type": "Incell HD+", "name": "X6A WF", "retail": 121000, "wholesale": 89000, "stock": 98},
    {"id": "1114", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE 6 / NOTE6 PRO", "retail": 99000, "wholesale": 73000, "stock": 97},
    {"id": "1115", "brand": "Xiaomi", "type": "Incell HD+", "name": "MI 9", "retail": 146000, "wholesale": 108000, "stock": 97},
    {"id": "1116", "brand": "Redmi", "type": "Premium", "name": "NOTE11PRO 4G WF", "retail": 152000, "wholesale": 112000, "stock": 97},
    {"id": "1117", "brand": "Samsung", "type": "Premium", "name": "A15 WF", "retail": 131000, "wholesale": 97000, "stock": 96},
    {"id": "1118", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "KF8 / Spark7Pro / CG6 / CG6J / Camon17 / Camon18i", "retail": 87000, "wholesale": 64000, "stock": 96},
    {"id": "1119", "brand": "Huawei", "type": "Incell HD+", "name": "Y7 2019 / Y7PRO 2019", "retail": 84000, "wholesale": 62000, "stock": 94},
    {"id": "1120", "brand": "Xiaomi", "type": "Incell HD+", "name": "MI 14TPRO / MI14T", "retail": 164000, "wholesale": 121000, "stock": 93},
    {"id": "1121", "brand": "Honor", "type": "Servis", "name": "X8C WF", "retail": 430000, "wholesale": 318000, "stock": 93},
    {"id": "1122", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "POVA4PRO / LG8 / LG8N", "retail": 114000, "wholesale": 84000, "stock": 93},
    {"id": "1123", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "NOTE30PRO", "retail": 99000, "wholesale": 73000, "stock": 93},
    {"id": "1124", "brand": "Samsung", "type": "Premium", "name": "A30S WF", "retail": 122000, "wholesale": 90000, "stock": 89},
    {"id": "1125", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE11PRO 4G WF", "retail": 135000, "wholesale": 100000, "stock": 89},
    {"id": "1126", "brand": "Xiaomi", "type": "Incell HD+", "name": "MI 12T PRO / MI12T", "retail": 133000, "wholesale": 98000, "stock": 88},
    {"id": "1127", "brand": "Vivo", "type": "Incell HD+", "name": "V20-V2025 / s6-V1962A / v20se-V2022 / y73s-V2031A / X50 e-V1930 / G1-V1962BA / S7 E-V2031A / S10E-V2130A / T1 4G-V2153 / y55 4G-V2154 / Y70外-V2023 / T1 4G-V2168", "retail": 98000, "wholesale": 72000, "stock": 87},
    {"id": "1128", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "SPARK GO 2021", "retail": 87000, "wholesale": 64000, "stock": 86},
    {"id": "1129", "brand": "Samsung", "type": "IPS LCD", "name": "A7 2018 / A750", "retail": 95000, "wholesale": 70000, "stock": 80},
    {"id": "1130", "brand": "Vivo", "type": "Incell HD+", "name": "Y19 / Y5S / Z5I / U3 / U20", "retail": 92000, "wholesale": 68000, "stock": 80},
    {"id": "1131", "brand": "Honor", "type": "Incell HD+", "name": "RY X8B", "retail": 214000, "wholesale": 158000, "stock": 79},
    {"id": "1132", "brand": "Samsung", "type": "Premium", "name": "A36 / A56", "retail": 133000, "wholesale": 98000, "stock": 77},
    {"id": "1133", "brand": "Samsung", "type": "Premium", "name": "A8 2018 / A530", "retail": 117000, "wholesale": 86000, "stock": 76},
    {"id": "1134", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "GT20PRO", "retail": 107000, "wholesale": 79000, "stock": 76},
    {"id": "1135", "brand": "Oppo", "type": "Incell HD+", "name": "RENO5LITE WF", "retail": 133000, "wholesale": 98000, "stock": 74},
    {"id": "1136", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "POP5LITE", "retail": 92000, "wholesale": 68000, "stock": 72},
    {"id": "1137", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "NOTE40S", "retail": 107000, "wholesale": 79000, "stock": 72},
    {"id": "1138", "brand": "Samsung", "type": "IPS LCD", "name": "J3 2016 / J320 / J300", "retail": 80000, "wholesale": 59000, "stock": 71},
    {"id": "1139", "brand": "Samsung", "type": "Premium", "name": "A23 4G", "retail": 103000, "wholesale": 76000, "stock": 70},
    {"id": "1140", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE14 4G WF", "retail": 142000, "wholesale": 105000, "stock": 70},
    {"id": "1141", "brand": "Honor", "type": "Incell HD+", "name": "X9C SMART", "retail": 117000, "wholesale": 86000, "stock": 70},
    {"id": "1142", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "POP8PRO", "retail": 92000, "wholesale": 68000, "stock": 70},
    {"id": "1143", "brand": "Honor", "type": "Incell HD+", "name": "RY X8 WF", "retail": 156000, "wholesale": 115000, "stock": 67},
    {"id": "1144", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "CK7 / CK7N / CAMON20PRO", "retail": 99000, "wholesale": 73000, "stock": 67},
    {"id": "1145", "brand": "Samsung", "type": "OLED", "name": "A315 / A31-WF", "retail": 284000, "wholesale": 210000, "stock": 66},
    {"id": "1146", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE13PRO PLUS WF", "retail": 167000, "wholesale": 123000, "stock": 66},
    {"id": "1147", "brand": "Honor", "type": "Incell HD+", "name": "RY X8B WF", "retail": 304000, "wholesale": 225000, "stock": 66},
    {"id": "1148", "brand": "Samsung", "type": "OLED", "name": "A515 / A51-WF", "retail": 323000, "wholesale": 239000, "stock": 64},
    {"id": "1149", "brand": "Vivo", "type": "Incell HD+", "name": "Y35+ / Y35M+ / Y27 4G / Y36 / Y27 5G", "retail": 103000, "wholesale": 76000, "stock": 64},
    {"id": "1150", "brand": "Vivo", "type": "Incell HD+", "name": "Y29 4G / Y300I", "retail": 98000, "wholesale": 72000, "stock": 64},
    {"id": "1151", "brand": "Samsung", "type": "IPS LCD", "name": "A01M 2020 / A015", "retail": 84000, "wholesale": 62000, "stock": 63},
    {"id": "1152", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "CAMON15 / 15AIR", "retail": 90000, "wholesale": 66000, "stock": 63},
    {"id": "1153", "brand": "Huawei", "type": "Incell HD+", "name": "Y6P / RY 9A", "retail": 90000, "wholesale": 66000, "stock": 62},
    {"id": "1154", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "KG5K / SPARK8C / KG5j / S18 / P38 / KG5n / X665 / X665B / X6512 / X665C / X665E / KH6 / KH6H / Smart6 / SPARK9T / VISON3 / S661L / S663L / P661W / Vision5", "retail": 83000, "wholesale": 61000, "stock": 62},
    {"id": "1155", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "Camon30 / CL7 / CL6K / CL6", "retail": 107000, "wholesale": 79000, "stock": 62},
    {"id": "1156", "brand": "Honor", "type": "Incell HD+", "name": "RY 10LITE(2018)", "retail": 92000, "wholesale": 68000, "stock": 61},
    {"id": "1157", "brand": "Samsung", "type": "Premium", "name": "A04 / A045", "retail": 100000, "wholesale": 74000, "stock": 60},
    {"id": "1158", "brand": "Samsung", "type": "TFT", "name": "J1 2016 / J120", "retail": 80000, "wholesale": 59000, "stock": 60},
    {"id": "1159", "brand": "Samsung", "type": "OLED", "name": "A15 / A155 / A156-WF", "retail": 364000, "wholesale": 269000, "stock": 60},
    {"id": "1160", "brand": "Samsung", "type": "Premium", "name": "A35 / A55", "retail": 119000, "wholesale": 88000, "stock": 60},
    {"id": "1161", "brand": "Redmi", "type": "Premium", "name": "15 4G / 5G", "retail": 118000, "wholesale": 87000, "stock": 60},
    {"id": "1162", "brand": "Honor", "type": "Premium", "name": "X30I / X40I / PLAY6TPRO / PLAY7TPRO", "retail": 149000, "wholesale": 110000, "stock": 60},
    {"id": "1163", "brand": "Redmi", "type": "OLED", "name": "F3 / F4 / K40 / K40S / K40PRO / (heisha）4 / MI11I", "retail": 343000, "wholesale": 254000, "stock": 59},
    {"id": "1164", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE14PRO 4G", "retail": 141000, "wholesale": 104000, "stock": 59},
    {"id": "1165", "brand": "Honor", "type": "Incell HD+", "name": "X6C WF", "retail": 137000, "wholesale": 101000, "stock": 59},
    {"id": "1166", "brand": "Oppo", "type": "Incell HD+", "name": "A36 / A76 / A76New", "retail": 95000, "wholesale": 70000, "stock": 59},
    {"id": "1167", "brand": "Oppo", "type": "Incell HD+", "name": "V40", "retail": 169000, "wholesale": 125000, "stock": 59},
    {"id": "1168", "brand": "Redmi", "type": "Premium", "name": "7 / Y3", "retail": 108000, "wholesale": 80000, "stock": 58},
    {"id": "1169", "brand": "Samsung", "type": "Premium", "name": "A24 4G WF", "retail": 141000, "wholesale": 104000, "stock": 57},
    {"id": "1170", "brand": "Samsung", "type": "TFT", "name": "S20 4GWF", "retail": 210000, "wholesale": 155000, "stock": 57},
    {"id": "1171", "brand": "Samsung", "type": "IPS LCD", "name": "A15 / M15 / M156", "retail": 92000, "wholesale": 68000, "stock": 57},
    {"id": "1172", "brand": "Samsung", "type": "IPS LCD", "name": "A336 / A33-WF", "retail": 154000, "wholesale": 114000, "stock": 57},
    {"id": "1173", "brand": "Honor", "type": "Incell HD+", "name": "X9A WF", "retail": 422000, "wholesale": 312000, "stock": 57},
    {"id": "1174", "brand": "Oppo", "type": "Incell HD+", "name": "V20E", "retail": 100000, "wholesale": 74000, "stock": 57},
    {"id": "1175", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "NOTE40PRO 4G", "retail": 126000, "wholesale": 93000, "stock": 57},
    {"id": "1176", "brand": "Samsung", "type": "TFT", "name": "S10WF", "retail": 196000, "wholesale": 145000, "stock": 56},
    {"id": "1177", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "ZERO40", "retail": 126000, "wholesale": 93000, "stock": 56},
    {"id": "1178", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE12PRO WF", "retail": 127000, "wholesale": 94000, "stock": 55},
    {"id": "1179", "brand": "Realme", "type": "Incell HD+", "name": "REALME5PRO / REALME Q", "retail": 99000, "wholesale": 73000, "stock": 55},
    {"id": "1180", "brand": "Redmi", "type": "Incell HD+", "name": "K30S / MI10T / MI10T PRO", "retail": 113000, "wholesale": 83000, "stock": 54},
    {"id": "1181", "brand": "Samsung", "type": "TFT", "name": "NOTE10+WF", "retail": 264000, "wholesale": 195000, "stock": 51},
    {"id": "1182", "brand": "iPhone", "type": "Servis", "name": "X-F(Q)", "retail": 540000, "wholesale": 400000, "stock": 50},
    {"id": "1183", "brand": "iPhone", "type": "Servis", "name": "7GW-F(Q)", "retail": 192000, "wholesale": 142000, "stock": 50},
    {"id": "1184", "brand": "iPhone", "type": "Servis", "name": "7PB-F(Q)", "retail": 238000, "wholesale": 176000, "stock": 50},
    {"id": "1185", "brand": "iPhone", "type": "Servis", "name": "7PW-F(Q)", "retail": 238000, "wholesale": 176000, "stock": 50},
    {"id": "1186", "brand": "iPhone", "type": "Servis", "name": "8PB-F(Q)", "retail": 238000, "wholesale": 176000, "stock": 50},
    {"id": "1187", "brand": "iPhone", "type": "Servis", "name": "8PW-F-(Q)", "retail": 244000, "wholesale": 180000, "stock": 50},
    {"id": "1188", "brand": "iPhone", "type": "Servis", "name": "8GB-F(Q)", "retail": 192000, "wholesale": 142000, "stock": 50},
    {"id": "1189", "brand": "iPhone", "type": "Servis", "name": "8GW-F(Q)", "retail": 198000, "wholesale": 146000, "stock": 50},
    {"id": "1190", "brand": "Samsung", "type": "Premium", "name": "A02S / A03S / A03 2021 / A025 / A04E", "retail": 98000, "wholesale": 72000, "stock": 50},
    {"id": "1191", "brand": "Samsung", "type": "Premium", "name": "A31 2020 / A315", "retail": 111000, "wholesale": 82000, "stock": 50},
    {"id": "1192", "brand": "Samsung", "type": "Premium", "name": "A6+ 2018 / A605", "retail": 110000, "wholesale": 81000, "stock": 50},
    {"id": "1193", "brand": "Samsung", "type": "OLED", "name": "A16 4GWF", "retail": 353000, "wholesale": 261000, "stock": 50},
    {"id": "1194", "brand": "Samsung", "type": "Premium", "name": "A40 2020 / A405 WF", "retail": 154000, "wholesale": 114000, "stock": 50},
    {"id": "1195", "brand": "Samsung", "type": "Premium", "name": "A36WF", "retail": 171000, "wholesale": 126000, "stock": 50},
    {"id": "1196", "brand": "Redmi", "type": "OLED", "name": "NOTE11 4G / NOTE 11S / M4PRO 4G / NOTE12S / 10prime", "retail": 449000, "wholesale": 332000, "stock": 50},
    {"id": "1197", "brand": "Redmi", "type": "OLED", "name": "NOTE10PRO 4G WF", "retail": 435000, "wholesale": 322000, "stock": 50},
    {"id": "1198", "brand": "Redmi", "type": "OLED", "name": "NOTE13PRO 4G WF", "retail": 430000, "wholesale": 318000, "stock": 50},
    {"id": "1199", "brand": "Redmi", "type": "OLED", "name": "NOTE13 4G WF", "retail": 405000, "wholesale": 300000, "stock": 50},
    {"id": "1200", "brand": "Redmi", "type": "OLED", "name": "NOTE11PRO WF", "retail": 435000, "wholesale": 322000, "stock": 50},
    {"id": "1201", "brand": "Redmi", "type": "Premium", "name": "NOTE11S WF", "retail": 145000, "wholesale": 107000, "stock": 50},
    {"id": "1202", "brand": "Redmi", "type": "Premium", "name": "NOTE13PRO 4G WF", "retail": 181000, "wholesale": 134000, "stock": 50},
    {"id": "1203", "brand": "Redmi", "type": "Premium", "name": "NOTE14 4G WF", "retail": 152000, "wholesale": 112000, "stock": 50},
    {"id": "1204", "brand": "Redmi", "type": "Premium", "name": "NOTE13PRO PLUS WF", "retail": 244000, "wholesale": 180000, "stock": 50},
    {"id": "1205", "brand": "Redmi", "type": "OLED", "name": "NOTE13PRO PLUS WF", "retail": 500000, "wholesale": 370000, "stock": 50},
    {"id": "1206", "brand": "Honor", "type": "Premium", "name": "RY X6", "retail": 108000, "wholesale": 80000, "stock": 50},
    {"id": "1207", "brand": "Huawei", "type": "Premium", "name": "RY X10 LITE / Y7A / PSMART 2021", "retail": 114000, "wholesale": 84000, "stock": 50},
    {"id": "1208", "brand": "Huawei", "type": "Premium", "name": "PSMART Z", "retail": 106000, "wholesale": 78000, "stock": 50},
    {"id": "1209", "brand": "Huawei", "type": "Premium", "name": "NOVA11I", "retail": 115000, "wholesale": 85000, "stock": 50},
    {"id": "1210", "brand": "Honor", "type": "Premium", "name": "RY X7A", "retail": 108000, "wholesale": 80000, "stock": 50},
    {"id": "1211", "brand": "Honor", "type": "Servis", "name": "RY X5", "retail": 135000, "wholesale": 100000, "stock": 50},
    {"id": "1212", "brand": "Honor", "type": "Servis", "name": "X9C WF", "retail": 535000, "wholesale": 396000, "stock": 50},
    {"id": "1213", "brand": "Honor", "type": "Servis", "name": "X9D WF", "retail": 462000, "wholesale": 342000, "stock": 50},
    {"id": "1214", "brand": "Honor", "type": "Premium", "name": "RY X5B", "retail": 103000, "wholesale": 76000, "stock": 50},
    {"id": "1215", "brand": "Honor", "type": "Premium", "name": "RY Y72 / Y72S", "retail": 106000, "wholesale": 78000, "stock": 50},
    {"id": "1216", "brand": "Huawei", "type": "Premium", "name": "CW40 / RY X6A / CW40C / X5 Plus / X5B / X5B Plus", "retail": 103000, "wholesale": 76000, "stock": 50},
    {"id": "1217", "brand": "Honor", "type": "Premium", "name": "X5+ / X5PLUS", "retail": 103000, "wholesale": 76000, "stock": 50},
    {"id": "1218", "brand": "Honor", "type": "Premium", "name": "X7C WF", "retail": 152000, "wholesale": 112000, "stock": 50},
    {"id": "1219", "brand": "Honor", "type": "Premium", "name": "X6C", "retail": 111000, "wholesale": 82000, "stock": 50},
    {"id": "1220", "brand": "Honor", "type": "Premium", "name": "X7D 4G WF", "retail": 148000, "wholesale": 109000, "stock": 50},
    {"id": "1221", "brand": "Honor", "type": "Premium", "name": "X9A WF", "retail": 473000, "wholesale": 350000, "stock": 50},
    {"id": "1222", "brand": "Honor", "type": "Premium", "name": "RY X8D", "retail": 244000, "wholesale": 180000, "stock": 50},
    {"id": "1223", "brand": "Honor", "type": "Servis", "name": "RY X8D WF", "retail": 603000, "wholesale": 446000, "stock": 50},
    {"id": "1224", "brand": "Oppo", "type": "Premium", "name": "A57 5G / A58 5G / A77 5G / A78 5G / K10 5G / NORD N20 SE / NORD N300 5G / A17 / A38 / A18 / A56S 5G / A58X / A57 4G / A17K / A77 4G / A17s / ONE PlusN20se / A1 5G(Vitality Edition Phone) / A17K(A01) / A17K(A40) / A1X 5G / A2M / A2X", "retail": 95000, "wholesale": 70000, "stock": 50},
    {"id": "1225", "brand": "Realme", "type": "Premium", "name": "A7 / A5S / A7n / AX5S / A12 / Realme3 / Realme3i", "retail": 95000, "wholesale": 70000, "stock": 50},
    {"id": "1226", "brand": "Vivo", "type": "Premium", "name": "Y56 5G / Y35 4G", "retail": 103000, "wholesale": 76000, "stock": 50},
    {"id": "1227", "brand": "Oppo", "type": "Premium", "name": "A5PRO", "retail": 108000, "wholesale": 80000, "stock": 50},
    {"id": "1228", "brand": "Tecno & Infinix", "type": "Premium", "name": "KI7 / SPARK10PRO / HOT30 / X6831 / POVA5 / LH7N / X6833B / NOTE30 / X6833", "retail": 114000, "wholesale": 84000, "stock": 50},
    {"id": "1229", "brand": "Tecno & Infinix", "type": "Premium", "name": "POVA6NEO / X6812", "retail": 108000, "wholesale": 80000, "stock": 50},
    {"id": "1230", "brand": "iPhone", "type": "Servis", "name": "11PRO-F(Q)", "retail": 674000, "wholesale": 499000, "stock": 49},
    {"id": "1231", "brand": "iPhone", "type": "Servis", "name": "7GB-F(Q)", "retail": 198000, "wholesale": 146000, "stock": 49},
    {"id": "1232", "brand": "Samsung", "type": "Premium", "name": "M53", "retail": 140000, "wholesale": 103000, "stock": 49},
    {"id": "1233", "brand": "Redmi", "type": "Premium", "name": "5", "retail": 100000, "wholesale": 74000, "stock": 49},
    {"id": "1234", "brand": "Redmi", "type": "Premium", "name": "10 4G / NOTE11 4G / 10 2022(nei dan)", "retail": 111000, "wholesale": 82000, "stock": 49},
    {"id": "1235", "brand": "Redmi", "type": "OLED", "name": "NOTE12 4G WF", "retail": 362000, "wholesale": 268000, "stock": 49},
    {"id": "1236", "brand": "Redmi", "type": "Premium", "name": "NOTE10PRO 4G WF", "retail": 148000, "wholesale": 109000, "stock": 49},
    {"id": "1237", "brand": "Honor", "type": "Servis", "name": "X8B WF", "retail": 465000, "wholesale": 344000, "stock": 49},
    {"id": "1238", "brand": "Honor", "type": "Premium", "name": "X6B WF", "retail": 131000, "wholesale": 97000, "stock": 49},
    {"id": "1239", "brand": "Honor", "type": "Premium", "name": "X7D 4G", "retail": 114000, "wholesale": 84000, "stock": 49},
    {"id": "1240", "brand": "Honor", "type": "Servis", "name": "RY X8B", "retail": 261000, "wholesale": 193000, "stock": 49},
    {"id": "1241", "brand": "Honor", "type": "Premium", "name": "X7B WF", "retail": 152000, "wholesale": 112000, "stock": 49},
    {"id": "1242", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "X652 / X652A / X652C / X652B / CC6 / KC3 / CAMON12AIR / S5 / S5LITE", "retail": 86000, "wholesale": 63000, "stock": 49},
    {"id": "1243", "brand": "Tecno & Infinix", "type": "Premium", "name": "NOTE10(X693) / NOTE11(X693) / NOTE11S(X698) / NOTE11Pro(X697) / POVA2(LE7 / LE7n) / POVA3(LF7) / POVA 5G(LE8)", "retail": 123000, "wholesale": 91000, "stock": 49},
    {"id": "1244", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "ZEROX NEO", "retail": 107000, "wholesale": 79000, "stock": 49},
    {"id": "1245", "brand": "iPhone", "type": "Incell HD+", "name": "XR-FHD", "retail": 176000, "wholesale": 130000, "stock": 48},
    {"id": "1246", "brand": "Redmi", "type": "Premium", "name": "NOTE 6 / NOTE6 PRO", "retail": 107000, "wholesale": 79000, "stock": 48},
    {"id": "1247", "brand": "Redmi", "type": "OLED", "name": "NOTE12Pro 4G WF", "retail": 411000, "wholesale": 304000, "stock": 48},
    {"id": "1248", "brand": "Honor", "type": "Premium", "name": "X8A WF", "retail": 176000, "wholesale": 130000, "stock": 48},
    {"id": "1249", "brand": "Realme", "type": "Incell HD+", "name": "C31 / realme C31 / C33S", "retail": 91000, "wholesale": 67000, "stock": 48},
    {"id": "1250", "brand": "Oppo", "type": "Premium", "name": "A32 4G / A33 / A11 / A53 4G / A53S / REALME7I / REALMEC17 / 1+N100 / A54 4G / A55 4G / A94", "retail": 95000, "wholesale": 70000, "stock": 48},
    {"id": "1251", "brand": "Oppo", "type": "Incell HD+", "name": "F19PROWF", "retail": 121000, "wholesale": 89000, "stock": 48},
    {"id": "1252", "brand": "Tecno & Infinix", "type": "Premium", "name": "HOT40PRO", "retail": 115000, "wholesale": 85000, "stock": 48},
    {"id": "1253", "brand": "Tecno & Infinix", "type": "Premium", "name": "KD6 / SPARK5AIR / LC7 / LC7S / LC8 / KE6 / SPARK6AIR / KD6A / KE6J / POUVOIR4 / POUVOIR4PRO / SPARKPOWER2", "retail": 102000, "wholesale": 75000, "stock": 48},
    {"id": "1254", "brand": "Tecno & Infinix", "type": "Premium", "name": "SPARK8PRO", "retail": 113000, "wholesale": 83000, "stock": 48},
    {"id": "1255", "brand": "Samsung", "type": "Premium", "name": "A34 4G WF", "retail": 162000, "wholesale": 120000, "stock": 47},
    {"id": "1256", "brand": "Samsung", "type": "Premium", "name": "A41 / A415WF", "retail": 194000, "wholesale": 143000, "stock": 47},
    {"id": "1257", "brand": "Redmi", "type": "Premium", "name": "Note14pro 4G", "retail": 162000, "wholesale": 120000, "stock": 47},
    {"id": "1258", "brand": "Honor", "type": "Premium", "name": "RY X7A WF", "retail": 138000, "wholesale": 102000, "stock": 47},
    {"id": "1259", "brand": "Tecno & Infinix", "type": "Premium", "name": "HOT40 / X6836 / X6837 / SPARK20PRO / KJ6 / KJ7", "retail": 113000, "wholesale": 83000, "stock": 47},
    {"id": "1260", "brand": "Tecno & Infinix", "type": "Premium", "name": "X6882 / HOT50 / KL6 / SPARK30 / SPARK30 4G / HOT50 4G", "retail": 121000, "wholesale": 89000, "stock": 47},
    {"id": "1261", "brand": "Samsung", "type": "Premium", "name": "A35WF", "retail": 162000, "wholesale": 120000, "stock": 46},
    {"id": "1262", "brand": "Redmi", "type": "Premium", "name": "NOTE5 / NOTE 5 PRO", "retail": 100000, "wholesale": 74000, "stock": 46},
    {"id": "1263", "brand": "Redmi", "type": "Premium", "name": "NOTE5 PLUS", "retail": 100000, "wholesale": 74000, "stock": 46},
    {"id": "1264", "brand": "Huawei", "type": "Premium", "name": "NOVA10 SE / NOVA11SE / NOVA12SE", "retail": 191000, "wholesale": 141000, "stock": 46},
    {"id": "1265", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "KL4 / KL5 / KL8 / KM4 / KM5 / SparkGo1 / POP9 / Spark30 / 30C / Hot50 / Hot50i / X6720 / Smart9 / X6725 / X6531 / P65 / A671L / A80 / Pova6 Neo 5G / Spark Go1S / Smart9 HD / X6532 / P673L / A95 5G(A671N) / Note50 / SMART10", "retail": 91000, "wholesale": 67000, "stock": 46},
    {"id": "1266", "brand": "Samsung", "type": "IPS LCD", "name": "J3Prime / J327", "retail": 96000, "wholesale": 71000, "stock": 45},
    {"id": "1267", "brand": "Honor", "type": "Premium", "name": "RY X8", "retail": 106000, "wholesale": 78000, "stock": 45},
    {"id": "1268", "brand": "Honor", "type": "Premium", "name": "X6C WF", "retail": 146000, "wholesale": 108000, "stock": 45},
    {"id": "1269", "brand": "Samsung", "type": "Premium", "name": "A33 4G", "retail": 117000, "wholesale": 86000, "stock": 44},
    {"id": "1270", "brand": "Samsung", "type": "IPS LCD", "name": "A26WF", "retail": 171000, "wholesale": 126000, "stock": 44},
    {"id": "1271", "brand": "Honor", "type": "Servis", "name": "RY X7C", "retail": 148000, "wholesale": 109000, "stock": 44},
    {"id": "1272", "brand": "iPhone", "type": "Incell HD+", "name": "13PROMAX", "retail": 200000, "wholesale": 148000, "stock": 43},
    {"id": "1273", "brand": "Samsung", "type": "IPS LCD", "name": "A14 5G / A146B / A146F / A145F / A145M(BIG）", "retail": 91000, "wholesale": 67000, "stock": 43},
    {"id": "1274", "brand": "Samsung", "type": "TFT", "name": "S23U(USA version)WF", "retail": 269000, "wholesale": 199000, "stock": 43},
    {"id": "1275", "brand": "Honor", "type": "Premium", "name": "X6A WF", "retail": 135000, "wholesale": 100000, "stock": 43},
    {"id": "1276", "brand": "Oppo", "type": "Premium", "name": "A5 / A3S / Realme2 / A12e / AX5 / RealmeC1", "retail": 96000, "wholesale": 71000, "stock": 43},
    {"id": "1277", "brand": "Samsung", "type": "IPS LCD", "name": "A53 / A536", "retail": 100000, "wholesale": 74000, "stock": 42},
    {"id": "1278", "brand": "Vivo", "type": "Incell HD+", "name": "Y93 / Y93A / Y93T / Y91 / Y95 / U1 / Y1S", "retail": 86000, "wholesale": 63000, "stock": 42},
    {"id": "1279", "brand": "Oppo", "type": "Incell HD+", "name": "A57 WF", "retail": 117000, "wholesale": 86000, "stock": 42},
    {"id": "1280", "brand": "Oppo", "type": "Incell HD+", "name": "A77WF", "retail": 126000, "wholesale": 93000, "stock": 42},
    {"id": "1281", "brand": "Tecno & Infinix", "type": "Premium", "name": "KL4 / KL4H / KL8H / KL4S / POP9 / SPARK GO 1 / SPARKGO 1S / SPARK 30 5G / SPARK 30C 5G / KL8 / SPARK 30C / KL5S / SPARK 30C NFC / KL5N / P65 / P671N / P65NFC / A80 / A95 5G / X6720 / X6531 / X6532 / SMART9 / X6857 / POWER 70", "retail": 113000, "wholesale": 83000, "stock": 42},
    {"id": "1282", "brand": "Tecno & Infinix", "type": "Premium", "name": "POVA NEO6", "retail": 108000, "wholesale": 80000, "stock": 42},
    {"id": "1283", "brand": "Realme", "type": "Incell HD+", "name": "A7 / A5S / A7n / AX5S / A12 / Realme3 / Realme3i", "retail": 86000, "wholesale": 63000, "stock": 41},
    {"id": "1284", "brand": "Redmi", "type": "Premium", "name": "NOTE14 4G", "retail": 111000, "wholesale": 82000, "stock": 40},
    {"id": "1285", "brand": "Honor", "type": "Incell HD+", "name": "X7C WF", "retail": 142000, "wholesale": 105000, "stock": 40},
    {"id": "1286", "brand": "Realme", "type": "Premium", "name": "C67 4G / REALME12X 5G / REALME12 5G / NARZO70X 5G", "retail": 115000, "wholesale": 85000, "stock": 40},
    {"id": "1287", "brand": "Realme", "type": "Incell HD+", "name": "C67 4G / REALME12X 5G / REALME12 5G / NARZO70X 5G", "retail": 104000, "wholesale": 77000, "stock": 40},
    {"id": "1288", "brand": "iPhone", "type": "Incell HD+", "name": "15PRO", "retail": 169000, "wholesale": 125000, "stock": 39},
    {"id": "1289", "brand": "Samsung", "type": "IPS LCD", "name": "A36WF", "retail": 176000, "wholesale": 130000, "stock": 39},
    {"id": "1290", "brand": "Tecno & Infinix", "type": "Premium", "name": "BF7 / BF6 / A60 / A50C / POP7 / KI5K / SPARKGO 2023 / SMART10HD / X6516 / X6515 / KI5Q / SPARK10(KI5) / SPARK10C / KI8 / KI5N / VISION3 / SMART7 / S23 / Pop7Pro / A662L / P40 / X669 / X6517", "retail": 95000, "wholesale": 70000, "stock": 39},
    {"id": "1291", "brand": "Samsung", "type": "IPS LCD", "name": "M52 / M53 / M54", "retail": 107000, "wholesale": 79000, "stock": 38},
    {"id": "1292", "brand": "Huawei", "type": "Incell HD+", "name": "PSMART 2021 / Y7A / RY X10 LITE", "retail": 91000, "wholesale": 67000, "stock": 37},
    {"id": "1293", "brand": "Samsung", "type": "IPS LCD", "name": "A35WF", "retail": 164000, "wholesale": 121000, "stock": 36},
    {"id": "1294", "brand": "Xiaomi", "type": "Incell HD+", "name": "MI NOTE10 LITE / CC9PRO", "retail": 130000, "wholesale": 96000, "stock": 36},
    {"id": "1295", "brand": "Samsung", "type": "TFT", "name": "NOTE8WF", "retail": 241000, "wholesale": 178000, "stock": 35},
    {"id": "1296", "brand": "Honor", "type": "Incell HD+", "name": "RY X9A / MAGIC 5LITE", "retail": 176000, "wholesale": 130000, "stock": 35},
    {"id": "1297", "brand": "Samsung", "type": "TFT", "name": "S21UWF", "retail": 207000, "wholesale": 153000, "stock": 34},
    {"id": "1298", "brand": "Honor", "type": "Incell HD+", "name": "X5+", "retail": 92000, "wholesale": 68000, "stock": 34},
    {"id": "1299", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "Smart 6 HD / X6512 / Hot 12i / X665 / X665B / X665CX665E / Smart 6HD 2022 / X6511C / hot20i", "retail": 87000, "wholesale": 64000, "stock": 34},
    {"id": "1300", "brand": "Redmi", "type": "Incell HD+", "name": "", "retail": 86000, "wholesale": 63000, "stock": 33},
    {"id": "1301", "brand": "Oppo", "type": "Incell HD+", "name": "A3 / F7", "retail": 92000, "wholesale": 68000, "stock": 33},
    {"id": "1302", "brand": "Samsung", "type": "TFT", "name": "S8+WF", "retail": 202000, "wholesale": 149000, "stock": 32},
    {"id": "1303", "brand": "Samsung", "type": "TFT", "name": "NOTE9WF", "retail": 241000, "wholesale": 178000, "stock": 32},
    {"id": "1304", "brand": "Honor", "type": "Incell HD+", "name": "RY Y72 / Y72S", "retail": 88000, "wholesale": 65000, "stock": 32},
    {"id": "1305", "brand": "Tecno & Infinix", "type": "Premium", "name": "SPARK30PRO / KL7 / X6881 / HOT50PRO / S25 / S685LN", "retail": 118000, "wholesale": 87000, "stock": 32},
    {"id": "1306", "brand": "iPhone", "type": "Incell HD+", "name": "XR", "retail": 113000, "wholesale": 83000, "stock": 31},
    {"id": "1307", "brand": "Samsung", "type": "TFT", "name": "NOTE10-WF", "retail": 276000, "wholesale": 204000, "stock": 31},
    {"id": "1308", "brand": "Honor", "type": "Servis", "name": "RY X7A", "retail": 133000, "wholesale": 98000, "stock": 31},
    {"id": "1309", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "ZERO304G / 5G", "retail": 126000, "wholesale": 93000, "stock": 31},
    {"id": "1310", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "SPARK GO 2", "retail": 95000, "wholesale": 70000, "stock": 31},
    {"id": "1311", "brand": "Samsung", "type": "Premium", "name": "A725 WF", "retail": 160000, "wholesale": 118000, "stock": 30},
    {"id": "1312", "brand": "Samsung", "type": "Premium", "name": "S22U WF", "retail": 312000, "wholesale": 231000, "stock": 30},
    {"id": "1313", "brand": "Samsung", "type": "Premium", "name": "A54 5G / A546 WF", "retail": 165000, "wholesale": 122000, "stock": 30},
    {"id": "1314", "brand": "Samsung", "type": "Premium", "name": "A70 2019 / A705WF", "retail": 131000, "wholesale": 97000, "stock": 30},
    {"id": "1315", "brand": "Samsung", "type": "Premium", "name": "S20U WF", "retail": 265000, "wholesale": 196000, "stock": 30},
    {"id": "1316", "brand": "Samsung", "type": "Premium", "name": "A26WF", "retail": 154000, "wholesale": 114000, "stock": 30},
    {"id": "1317", "brand": "Samsung", "type": "Premium", "name": "A55WF", "retail": 180000, "wholesale": 133000, "stock": 30},
    {"id": "1318", "brand": "Samsung", "type": "Premium", "name": "S20WF", "retail": 252000, "wholesale": 186000, "stock": 30},
    {"id": "1319", "brand": "Samsung", "type": "Premium", "name": "S21WF", "retail": 257000, "wholesale": 190000, "stock": 30},
    {"id": "1320", "brand": "Samsung", "type": "Premium", "name": "S21U WF", "retail": 262000, "wholesale": 194000, "stock": 30},
    {"id": "1321", "brand": "Redmi", "type": "OLED", "name": "NOTE14 4G WF", "retail": 435000, "wholesale": 322000, "stock": 30},
    {"id": "1322", "brand": "Redmi", "type": "OLED", "name": "NOTE14PRO 4G WF", "retail": 489000, "wholesale": 362000, "stock": 30},
    {"id": "1323", "brand": "Redmi", "type": "Premium", "name": "NOTE14PRO 4G WF", "retail": 233000, "wholesale": 172000, "stock": 30},
    {"id": "1324", "brand": "Redmi", "type": "Premium", "name": "NOTE15 WF", "retail": 241000, "wholesale": 178000, "stock": 30},
    {"id": "1325", "brand": "Honor", "type": "Premium", "name": "RY X9", "retail": 114000, "wholesale": 84000, "stock": 30},
    {"id": "1326", "brand": "Honor", "type": "OLED", "name": "RY 90 WF", "retail": 493000, "wholesale": 365000, "stock": 30},
    {"id": "1327", "brand": "Honor", "type": "Servis", "name": "RY 200Lite WF", "retail": 465000, "wholesale": 344000, "stock": 30},
    {"id": "1328", "brand": "Honor", "type": "Servis", "name": "RY200PRO WF", "retail": 616000, "wholesale": 456000, "stock": 30},
    {"id": "1329", "brand": "Vivo", "type": "Incell HD+", "name": "Y27S", "retail": 95000, "wholesale": 70000, "stock": 30},
    {"id": "1330", "brand": "Tecno & Infinix", "type": "Premium", "name": "SPARK GO 2021", "retail": 103000, "wholesale": 76000, "stock": 30},
    {"id": "1331", "brand": "Redmi", "type": "Premium", "name": "6 / 6A", "retail": 95000, "wholesale": 70000, "stock": 29},
    {"id": "1332", "brand": "Redmi", "type": "Premium", "name": "NOTE15PRO WF", "retail": 238000, "wholesale": 176000, "stock": 29},
    {"id": "1333", "brand": "Honor", "type": "Servis", "name": "RY 200 WF", "retail": 508000, "wholesale": 376000, "stock": 29},
    {"id": "1334", "brand": "iPhone", "type": "Incell HD+", "name": "13PRO", "retail": 173000, "wholesale": 128000, "stock": 28},
    {"id": "1335", "brand": "Samsung", "type": "Premium", "name": "J2Core / J260", "retail": 90000, "wholesale": 66000, "stock": 28},
    {"id": "1336", "brand": "Samsung", "type": "IPS LCD", "name": "A30 / A50 / A50S-WF", "retail": 121000, "wholesale": 89000, "stock": 28},
    {"id": "1337", "brand": "Samsung", "type": "TFT", "name": "S8WF", "retail": 211000, "wholesale": 156000, "stock": 28},
    {"id": "1338", "brand": "Samsung", "type": "TFT", "name": "S22U(EU version)WF", "retail": 324000, "wholesale": 240000, "stock": 28},
    {"id": "1339", "brand": "Samsung", "type": "Premium", "name": "A73WF", "retail": 168000, "wholesale": 124000, "stock": 28},
    {"id": "1340", "brand": "Samsung", "type": "Premium", "name": "A25 WF", "retail": 141000, "wholesale": 104000, "stock": 28},
    {"id": "1341", "brand": "Honor", "type": "Servis", "name": "RY 90LITE WF", "retail": 203000, "wholesale": 150000, "stock": 28},
    {"id": "1342", "brand": "Oppo", "type": "Incell HD+", "name": "A60 4G / Realme C65 4G(5G) / Realme Narzo N65 / 12X 5G / 14X 5G / C75X / A3 Pro / Realme V60 / V60S / K12X 5G / A3X 4G(5G) / A3 5G", "retail": 98000, "wholesale": 72000, "stock": 28},
    {"id": "1343", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "CI6 / CI7N / CI8N / CAMON19 / CI8 / CI7 / CAMON19PRO", "retail": 98000, "wholesale": 72000, "stock": 28},
    {"id": "1344", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "POVA NEO 6", "retail": 94000, "wholesale": 69000, "stock": 28},
    {"id": "1345", "brand": "Samsung", "type": "Premium", "name": "A71 2020 / A715 WF", "retail": 137000, "wholesale": 101000, "stock": 27},
    {"id": "1346", "brand": "Xiaomi", "type": "Servis", "name": "Mi Note10Pro / Note10Lite", "retail": 520000, "wholesale": 385000, "stock": 27},
    {"id": "1347", "brand": "Realme", "type": "Incell HD+", "name": "A1K / RealmeC2", "retail": 87000, "wholesale": 64000, "stock": 27},
    {"id": "1348", "brand": "Tecno & Infinix", "type": "Premium", "name": "X662B / Hot11 / X662 / Spark8P / KG7 / Spark8t / KG7n / KG7h / KG6P / spark9pro / KH7 / KH7H / KH7N / S18pro / S662L / vision5plus / S662LC / X666B", "retail": 106000, "wholesale": 78000, "stock": 27},
    {"id": "1349", "brand": "Samsung", "type": "IPS LCD", "name": "A30S 2020 / A307", "retail": 90000, "wholesale": 66000, "stock": 26},
    {"id": "1350", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE5 PLUS", "retail": 88000, "wholesale": 65000, "stock": 26},
    {"id": "1351", "brand": "Vivo", "type": "Premium", "name": "Y35 5G", "retail": 102000, "wholesale": 75000, "stock": 26},
    {"id": "1352", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "Spark7T", "retail": 87000, "wholesale": 64000, "stock": 26},
    {"id": "1353", "brand": "iPhone", "type": "Incell HD+", "name": "16PRO", "retail": 256000, "wholesale": 189000, "stock": 25},
    {"id": "1354", "brand": "iPhone", "type": "OLED", "name": "X-GX", "retail": 318000, "wholesale": 235000, "stock": 25},
    {"id": "1355", "brand": "iPhone", "type": "OLED", "name": "XSMAX-GX", "retail": 460000, "wholesale": 340000, "stock": 25},
    {"id": "1356", "brand": "iPhone", "type": "OLED", "name": "13-GX", "retail": 468000, "wholesale": 346000, "stock": 25},
    {"id": "1357", "brand": "iPhone", "type": "OLED", "name": "13PROMAX-GX", "retail": 589000, "wholesale": 436000, "stock": 25},
    {"id": "1358", "brand": "iPhone", "type": "OLED", "name": "14PRO-GX", "retail": 546000, "wholesale": 404000, "stock": 25},
    {"id": "1359", "brand": "iPhone", "type": "Servis", "name": "11PROMAX-F(Q)", "retail": 725000, "wholesale": 537000, "stock": 25},
    {"id": "1360", "brand": "iPhone", "type": "Servis", "name": "12 / 12PRO-F(Q)", "retail": 751000, "wholesale": 556000, "stock": 25},
    {"id": "1361", "brand": "iPhone", "type": "Servis", "name": "12PROMAX-F-(Q)", "retail": 700000, "wholesale": 518000, "stock": 25},
    {"id": "1362", "brand": "iPhone", "type": "Servis", "name": "14PROMAX-F(Q)", "retail": 1120000, "wholesale": 829000, "stock": 25},
    {"id": "1363", "brand": "iPhone", "type": "Servis", "name": "15PRO-F(Q)", "retail": 1519000, "wholesale": 1125000, "stock": 25},
    {"id": "1364", "brand": "iPhone", "type": "Servis", "name": "15PROMAX-F(X)", "retail": 1387000, "wholesale": 1027000, "stock": 25},
    {"id": "1365", "brand": "iPhone", "type": "Servis", "name": "XS-F(Q-X)", "retail": 553000, "wholesale": 409000, "stock": 25},
    {"id": "1366", "brand": "iPhone", "type": "Servis", "name": "13PROMAX-F(Q)", "retail": 887000, "wholesale": 657000, "stock": 25},
    {"id": "1367", "brand": "iPhone", "type": "Servis", "name": "13PRO-F(Q-X)", "retail": 923000, "wholesale": 683000, "stock": 25},
    {"id": "1368", "brand": "iPhone", "type": "OLED", "name": "15PROMAX-GX-Hard", "retail": 535000, "wholesale": 396000, "stock": 25},
    {"id": "1369", "brand": "Samsung", "type": "IPS LCD", "name": "A40 2020 / A405-WF", "retail": 156000, "wholesale": 115000, "stock": 25},
    {"id": "1370", "brand": "Samsung", "type": "TFT", "name": "S9WF", "retail": 216000, "wholesale": 160000, "stock": 25},
    {"id": "1371", "brand": "Redmi", "type": "Premium", "name": "NOTE15", "retail": 162000, "wholesale": 120000, "stock": 25},
    {"id": "1372", "brand": "Realme", "type": "Incell HD+", "name": "Realme9 pro plus / Realme9 4G / Reno7 / 1+Nord CE2 5G / Reno 8T / REALME10 4G", "retail": 99000, "wholesale": 73000, "stock": 25},
    {"id": "1373", "brand": "Oppo", "type": "Incell HD+", "name": "RENO 5LITE WF", "retail": 121000, "wholesale": 89000, "stock": 25},
    {"id": "1374", "brand": "iPhone", "type": "OLED", "name": "11PRO-GX", "retail": 345000, "wholesale": 255000, "stock": 24},
    {"id": "1375", "brand": "iPhone", "type": "OLED", "name": "11PROMAX-GX", "retail": 477000, "wholesale": 353000, "stock": 24},
    {"id": "1376", "brand": "iPhone", "type": "OLED", "name": "12 / 12PRO-GX", "retail": 462000, "wholesale": 342000, "stock": 24},
    {"id": "1377", "brand": "iPhone", "type": "OLED", "name": "13PRO-GX", "retail": 576000, "wholesale": 426000, "stock": 24},
    {"id": "1378", "brand": "iPhone", "type": "OLED", "name": "15PRO-GX", "retail": 543000, "wholesale": 402000, "stock": 24},
    {"id": "1379", "brand": "iPhone", "type": "Servis", "name": "14PRO-F(Q)", "retail": 928000, "wholesale": 687000, "stock": 24},
    {"id": "1380", "brand": "iPhone", "type": "OLED", "name": "14PROMAX-GX-Hard", "retail": 539000, "wholesale": 399000, "stock": 24},
    {"id": "1381", "brand": "iPhone", "type": "OLED", "name": "XS-GX(和辉)", "retail": 312000, "wholesale": 231000, "stock": 24},
    {"id": "1382", "brand": "iPhone", "type": "OLED", "name": "12PROMAX-GX-Hard", "retail": 549000, "wholesale": 406000, "stock": 24},
    {"id": "1383", "brand": "Samsung", "type": "IPS LCD", "name": "A20 2019 / A205-WF", "retail": 100000, "wholesale": 74000, "stock": 24},
    {"id": "1384", "brand": "Honor", "type": "Servis", "name": "X9B WF", "retail": 515000, "wholesale": 381000, "stock": 24},
    {"id": "1385", "brand": "Realme", "type": "Incell HD+", "name": "C30 / NARZO50IPRIME / C30S / C33S / C30F / C33-2023", "retail": 84000, "wholesale": 62000, "stock": 24},
    {"id": "1386", "brand": "Realme", "type": "Incell HD+", "name": "REALME C35 / Narzo 50A prime", "retail": 83000, "wholesale": 61000, "stock": 24},
    {"id": "1387", "brand": "Tecno & Infinix", "type": "Premium", "name": "KF8 / Spark7Pro / CG6 / CG6J / Camon17 / Camon18i", "retail": 100000, "wholesale": 74000, "stock": 24},
    {"id": "1388", "brand": "Samsung", "type": "IPS LCD", "name": "A15WF", "retail": 129000, "wholesale": 95000, "stock": 23},
    {"id": "1389", "brand": "Samsung", "type": "IPS LCD", "name": "A54 5G / A546 WF", "retail": 164000, "wholesale": 121000, "stock": 23},
    {"id": "1390", "brand": "Honor", "type": "Servis", "name": "X9A WF", "retail": 476000, "wholesale": 352000, "stock": 23},
    {"id": "1391", "brand": "Realme", "type": "Premium", "name": "C55 / C65 / C67 4G(5G) / REALME12 5G / A3 5G / A3PRO 5G / A3I 5G / A3X 5G / A40 4G / A40M 4G / A5PRO 4G / A60 5G / A80 5G / K12X 5G / C63 5G / C65 5G / V60PRO 5G / V60S / A5I / K13X / C75 5G / C75X / A5X 5G", "retail": 113000, "wholesale": 83000, "stock": 23},
    {"id": "1392", "brand": "Tecno & Infinix", "type": "Premium", "name": "SPARK20PRO5G / NOTE40X5G", "retail": 111000, "wholesale": 82000, "stock": 23},
    {"id": "1393", "brand": "iPhone", "type": "Incell HD+", "name": "16PROMAX", "retail": 284000, "wholesale": 210000, "stock": 22},
    {"id": "1394", "brand": "iPhone", "type": "Servis", "name": "XSMAX-F(Q)", "retail": 694000, "wholesale": 514000, "stock": 22},
    {"id": "1395", "brand": "Samsung", "type": "IPS LCD", "name": "A35 / A55 4G WF", "retail": 185000, "wholesale": 137000, "stock": 22},
    {"id": "1396", "brand": "Samsung", "type": "IPS LCD", "name": "A52 / A525 A52 4G-WF", "retail": 144000, "wholesale": 106000, "stock": 21},
    {"id": "1397", "brand": "Samsung", "type": "IPS LCD", "name": "A16-WF", "retail": 134000, "wholesale": 99000, "stock": 21},
    {"id": "1398", "brand": "Huawei", "type": "Servis", "name": "NOVA10SE", "retail": 470000, "wholesale": 348000, "stock": 21},
    {"id": "1399", "brand": "Realme", "type": "Incell HD+", "name": "Realme8i 5G / A96 / K10 / narzo50 / Realme9i / A36 / A76 / Realme9pro / K9S / K10 5G / Realme9 5G / Q3S / Q3T / V25 / Q5 / 1+CE2lite / 1+ACE", "retail": 122000, "wholesale": 90000, "stock": 21},
    {"id": "1400", "brand": "iPhone", "type": "Incell HD+", "name": "11PROMAX", "retail": 140000, "wholesale": 103000, "stock": 20},
    {"id": "1401", "brand": "iPhone", "type": "Servis", "name": "11-F(Q)", "retail": 244000, "wholesale": 180000, "stock": 20},
    {"id": "1402", "brand": "Samsung", "type": "Premium", "name": "A05 / A055F", "retail": 98000, "wholesale": 72000, "stock": 20},
    {"id": "1403", "brand": "Samsung", "type": "TFT", "name": "S20+WF", "retail": 230000, "wholesale": 170000, "stock": 20},
    {"id": "1404", "brand": "Xiaomi", "type": "Incell HD+", "name": "MI 11 LITE 4G / 5G", "retail": 103000, "wholesale": 76000, "stock": 20},
    {"id": "1405", "brand": "Redmi", "type": "OLED", "name": "NOTE15 WF", "retail": 576000, "wholesale": 426000, "stock": 20},
    {"id": "1406", "brand": "Redmi", "type": "Premium", "name": "NOTE15PRO", "retail": 162000, "wholesale": 120000, "stock": 20},
    {"id": "1407", "brand": "Redmi", "type": "OLED", "name": "NOTE15PRO WF", "retail": 651000, "wholesale": 482000, "stock": 20},
    {"id": "1408", "brand": "Realme", "type": "Incell HD+", "name": "Realme8i / Realme9i / A96 4G / Narzo50 / K10 4G", "retail": 92000, "wholesale": 68000, "stock": 20},
    {"id": "1409", "brand": "Oppo", "type": "Incell HD+", "name": "V27 5G", "retail": 191000, "wholesale": 141000, "stock": 20},
    {"id": "1410", "brand": "Vivo", "type": "Incell HD+", "name": "Y28 4G / Y38 5G / Y37PRO / Y19S / Y29 5G / Y200+", "retail": 86000, "wholesale": 63000, "stock": 20},
    {"id": "1411", "brand": "Realme", "type": "Premium", "name": "C63 / C61 / NARZO N63 / C65S", "retail": 103000, "wholesale": 76000, "stock": 20},
    {"id": "1412", "brand": "Samsung", "type": "Premium", "name": "A13 5G / A04S / A136U / A047 / A04CORE / A136B", "retail": 98000, "wholesale": 72000, "stock": 19},
    {"id": "1413", "brand": "Samsung", "type": "TFT", "name": "S9+WF", "retail": 216000, "wholesale": 160000, "stock": 19},
    {"id": "1414", "brand": "Samsung", "type": "TFT", "name": "S20UWF", "retail": 258000, "wholesale": 191000, "stock": 19},
    {"id": "1415", "brand": "Samsung", "type": "IPS LCD", "name": "S24UWF", "retail": 276000, "wholesale": 204000, "stock": 19},
    {"id": "1416", "brand": "Redmi", "type": "OLED", "name": "NOTE11 4G WF", "retail": 430000, "wholesale": 318000, "stock": 19},
    {"id": "1417", "brand": "Vivo", "type": "Incell HD+", "name": "Y03 / Y18 / Y37 / Y18E / Y18I / Y18S / Y28E 5G / Y03T / Y28S 5G / T3 LITE 5G", "retail": 86000, "wholesale": 63000, "stock": 19},
    {"id": "1418", "brand": "Redmi", "type": "Premium", "name": "Note10 / Note10s / POCO M5S", "retail": 100000, "wholesale": 74000, "stock": 18},
    {"id": "1419", "brand": "Samsung", "type": "OLED", "name": "NOTE11PRO 4G / NOTE12PRO 4G WF", "retail": 411000, "wholesale": 304000, "stock": 18},
    {"id": "1420", "brand": "Honor", "type": "Incell HD+", "name": "RY 9XLITE(2020) / RY 8X", "retail": 94000, "wholesale": 69000, "stock": 18},
    {"id": "1421", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE8T", "retail": 87000, "wholesale": 64000, "stock": 17},
    {"id": "1422", "brand": "Oppo", "type": "Incell HD+", "name": "RENO6Lite / Realme8 4G / Realme6Z 5G / Reno5F / Reno5Z / F19 / F19S / F19Pro 4G / A94 4G / A74 / RM8Pro / A96 5G / RM Q2PRO / RM X7-5G / RM V15 5G / A95 4G / 5G / RM7Pro / F21PRO 5G(403#)", "retail": 92000, "wholesale": 68000, "stock": 17},
    {"id": "1423", "brand": "Samsung", "type": "Premium", "name": "A24 4G / A245 / A25 5G / A256 / M34 5G / A26 / F34 5G", "retail": 111000, "wholesale": 82000, "stock": 16},
    {"id": "1424", "brand": "Samsung", "type": "IPS LCD", "name": "A73-WF", "retail": 162000, "wholesale": 120000, "stock": 16},
    {"id": "1425", "brand": "Honor", "type": "Incell HD+", "name": "RY90", "retail": 100000, "wholesale": 74000, "stock": 16},
    {"id": "1426", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "SPARK30PRO / KL7 / X6881 / HOT50PRO / S25 / S685LN", "retail": 107000, "wholesale": 79000, "stock": 16},
    {"id": "1427", "brand": "Samsung", "type": "IPS LCD", "name": "A53WF", "retail": 140000, "wholesale": 103000, "stock": 15},
    {"id": "1428", "brand": "Samsung", "type": "IPS LCD", "name": "A53 / A535-WF", "retail": 140000, "wholesale": 103000, "stock": 14},
    {"id": "1429", "brand": "Samsung", "type": "OLED", "name": "S10+-WF", "retail": 1288000, "wholesale": 954000, "stock": 14},
    {"id": "1430", "brand": "Samsung", "type": "IPS LCD", "name": "J5 2017 / J5Pro / J530", "retail": 86000, "wholesale": 63000, "stock": 13},
    {"id": "1431", "brand": "Realme", "type": "Premium", "name": "Realme C31 / C33S", "retail": 96000, "wholesale": 71000, "stock": 13},
    {"id": "1432", "brand": "Vivo", "type": "Premium", "name": "Y58", "retail": 108000, "wholesale": 80000, "stock": 13},
    {"id": "1433", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "KI7 / SPARK10PRO / HOT30 / X6831 / POVA5 / LH7 / X6833B / NOTE30 / LH7N / X6833", "retail": 92000, "wholesale": 68000, "stock": 13},
    {"id": "1434", "brand": "iPhone", "type": "Incell HD+", "name": "13MINI-FHD", "retail": 219000, "wholesale": 162000, "stock": 12},
    {"id": "1435", "brand": "Samsung", "type": "OLED", "name": "A30 / A50 / A50S-WF", "retail": 291000, "wholesale": 215000, "stock": 12},
    {"id": "1436", "brand": "Samsung", "type": "IPS LCD", "name": "A35 / A55", "retail": 108000, "wholesale": 80000, "stock": 12},
    {"id": "1437", "brand": "Redmi", "type": "Incell HD+", "name": "Note14pro 5G / Note13proplus / PocoX7 / Note14pro plus", "retail": 180000, "wholesale": 133000, "stock": 12},
    {"id": "1438", "brand": "Huawei", "type": "Servis", "name": "NOVA10PRO", "retail": 651000, "wholesale": 482000, "stock": 12},
    {"id": "1439", "brand": "Vivo", "type": "Premium", "name": "V20SE / S6 / G1 / S7E / Y70 / Y73S / X50E", "retail": 115000, "wholesale": 85000, "stock": 12},
    {"id": "1440", "brand": "Oppo", "type": "Incell HD+", "name": "S6 5G", "retail": 100000, "wholesale": 74000, "stock": 12},
    {"id": "1441", "brand": "iPhone", "type": "Incell HD+", "name": "XS", "retail": 130000, "wholesale": 96000, "stock": 11},
    {"id": "1442", "brand": "iPhone", "type": "Servis", "name": "12PRO-F(Q）", "retail": 669000, "wholesale": 495000, "stock": 11},
    {"id": "1443", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "BF7 / BF6 / A60 / A60S / POP7 / KI5K / SPARKGO2023 / X6516 / X6515 / KI5Q / SPARK10(KI5) / SPARK10C / KI8 / KI5N / VISION3 / SMART7 / S23 / POP7PRO / SMARK7HD / A662L / P40 / NOTE20 / NOTE12VIP / X669 / X6517 / HOT30I / A70", "retail": 83000, "wholesale": 61000, "stock": 11},
    {"id": "1444", "brand": "Tecno & Infinix", "type": "Premium", "name": "X6725 / X6726 / KL4 / KL8 / X6720 / X6728 / X6531 / X6532 / X6857 / KM5 / SPARK GO1 / P65 / A80(A671L) / HOT60I", "retail": 103000, "wholesale": 76000, "stock": 11},
    {"id": "1445", "brand": "iPhone", "type": "Servis", "name": "15PROMAX-F(Q-X)", "retail": 1222000, "wholesale": 905000, "stock": 10},
    {"id": "1446", "brand": "Samsung", "type": "OLED", "name": "A20-WF", "retail": 287000, "wholesale": 212000, "stock": 10},
    {"id": "1447", "brand": "Samsung", "type": "OLED", "name": "S24U-WF", "retail": 902000, "wholesale": 668000, "stock": 10},
    {"id": "1448", "brand": "Honor", "type": "Premium", "name": "RY X6 / X6X / X8 5G / RY 70LITE / X8A 5G", "retail": 104000, "wholesale": 77000, "stock": 10},
    {"id": "1449", "brand": "Vivo", "type": "Incell HD+", "name": "Y02 / Y02T / Y02A / Y11 2023", "retail": 86000, "wholesale": 63000, "stock": 10},
    {"id": "1450", "brand": "Samsung", "type": "IPS LCD", "name": "J2Core / J260", "retail": 79000, "wholesale": 58000, "stock": 9},
    {"id": "1451", "brand": "Redmi", "type": "Incell HD+", "name": "5", "retail": 91000, "wholesale": 67000, "stock": 9},
    {"id": "1452", "brand": "Honor", "type": "Incell HD+", "name": "X30I / X8 4g", "retail": 94000, "wholesale": 69000, "stock": 9},
    {"id": "1453", "brand": "Honor", "type": "Incell HD+", "name": "X9C WF", "retail": 472000, "wholesale": 349000, "stock": 9},
    {"id": "1454", "brand": "Honor", "type": "Servis", "name": "RY X5B", "retail": 130000, "wholesale": 96000, "stock": 9},
    {"id": "1455", "brand": "Oppo", "type": "Premium", "name": "A3PRO", "retail": 102000, "wholesale": 75000, "stock": 9},
    {"id": "1456", "brand": "Vivo", "type": "Incell HD+", "name": "S18e / 30lite 4G(5G) / T3 5G / Y100 4G(5G) / Y200E 5G / iqooz9 5G / V29e 5G / V30 SE / V40 SE 5G / V40Lite 4G(5G) / Y300 5G / Y400 5G / iqoo Z10 lite 4G / Y200 5G", "retail": 260000, "wholesale": 192000, "stock": 9},
    {"id": "1457", "brand": "iPhone", "type": "Incell HD+", "name": "XSMAX-FHD", "retail": 203000, "wholesale": 150000, "stock": 8},
    {"id": "1458", "brand": "Samsung", "type": "IPS LCD", "name": "A21S 2020 / A217", "retail": 84000, "wholesale": 62000, "stock": 8},
    {"id": "1459", "brand": "Samsung", "type": "OLED", "name": "A325 / A32 4G / A32LITE-WF", "retail": 307000, "wholesale": 227000, "stock": 8},
    {"id": "1460", "brand": "Samsung", "type": "OLED", "name": "S23ultra / S918-WF", "retail": 789000, "wholesale": 584000, "stock": 8},
    {"id": "1461", "brand": "Samsung", "type": "Servis", "name": "S10 5GWF", "retail": 1685000, "wholesale": 1248000, "stock": 8},
    {"id": "1462", "brand": "Redmi", "type": "Incell HD+", "name": "A2 LITE / 6PRO", "retail": 99000, "wholesale": 73000, "stock": 8},
    {"id": "1463", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE 5 / NOTE 5 PRO", "retail": 88000, "wholesale": 65000, "stock": 8},
    {"id": "1464", "brand": "Honor", "type": "Incell HD+", "name": "X7D 5G WF", "retail": 146000, "wholesale": 108000, "stock": 8},
    {"id": "1465", "brand": "Vivo", "type": "Incell HD+", "name": "Y58", "retail": 92000, "wholesale": 68000, "stock": 8},
    {"id": "1466", "brand": "Vivo", "type": "Incell HD+", "name": "Y35 5G", "retail": 91000, "wholesale": 67000, "stock": 8},
    {"id": "1467", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "SPARK20PRO5G / NOTE40X5G", "retail": 100000, "wholesale": 74000, "stock": 8},
    {"id": "1468", "brand": "iPhone", "type": "Incell HD+", "name": "12 / 12PRO-FHD", "retail": 203000, "wholesale": 150000, "stock": 7},
    {"id": "1469", "brand": "Samsung", "type": "IPS LCD", "name": "A24-4G / Galaxy A25 5G / Galaxy M34 5G / A26-Galaxy F34 5G", "retail": 100000, "wholesale": 74000, "stock": 7},
    {"id": "1470", "brand": "Samsung", "type": "TFT", "name": "S23U(EU version)WF", "retail": 293000, "wholesale": 217000, "stock": 7},
    {"id": "1471", "brand": "Samsung", "type": "IPS LCD", "name": "A16 4G / A16 5G / A17 4G / A17 5G / M16 / F16 / A26", "retail": 98000, "wholesale": 72000, "stock": 7},
    {"id": "1472", "brand": "Samsung", "type": "TFT", "name": "S23+WF", "retail": 269000, "wholesale": 199000, "stock": 7},
    {"id": "1473", "brand": "Samsung", "type": "IPS LCD", "name": "A356 / A556 / A55 5G / M35 WF", "retail": 168000, "wholesale": 124000, "stock": 7},
    {"id": "1474", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE10 4G WF", "retail": 113000, "wholesale": 83000, "stock": 7},
    {"id": "1475", "brand": "Huawei", "type": "Incell HD+", "name": "P40 LITE E / Y7P / Y7P 2020", "retail": 91000, "wholesale": 67000, "stock": 7},
    {"id": "1476", "brand": "Honor", "type": "Incell HD+", "name": "RY X7C", "retail": 99000, "wholesale": 73000, "stock": 7},
    {"id": "1477", "brand": "Honor", "type": "Incell HD+", "name": "X8 WF", "retail": 156000, "wholesale": 115000, "stock": 7},
    {"id": "1478", "brand": "Vivo", "type": "Incell HD+", "name": "Y300", "retail": 237000, "wholesale": 175000, "stock": 7},
    {"id": "1479", "brand": "iPhone", "type": "Incell HD+", "name": "13PROMAX-FHD", "retail": 264000, "wholesale": 195000, "stock": 6},
    {"id": "1480", "brand": "Samsung", "type": "OLED", "name": "A15 / A155 / A156 / M15 / M156 5G", "retail": 458000, "wholesale": 339000, "stock": 6},
    {"id": "1481", "brand": "Honor", "type": "Servis", "name": "X6B", "retail": 130000, "wholesale": 96000, "stock": 6},
    {"id": "1482", "brand": "Honor", "type": "Incell HD+", "name": "RY 50", "retail": 187000, "wholesale": 138000, "stock": 6},
    {"id": "1483", "brand": "Vivo", "type": "Incell HD+", "name": "Y100 / Y100-5G / Y200 / S18E / Y300 5G / Y200 5G / V40LITE 4G / 5G / V29E 5G / V30LITE 4G", "retail": 104000, "wholesale": 77000, "stock": 6},
    {"id": "1484", "brand": "Oppo", "type": "Incell HD+", "name": "RENO 8T 5G", "retail": 157000, "wholesale": 116000, "stock": 6},
    {"id": "1485", "brand": "Vivo", "type": "Incell HD+", "name": "Y04 / Y19E / Y29E / Y29S", "retail": 92000, "wholesale": 68000, "stock": 6},
    {"id": "1486", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "HOT40(X6836) / X6837 / SPARK20PRO(KJ6) / Spark10pro(KI7)", "retail": 98000, "wholesale": 72000, "stock": 6},
    {"id": "1487", "brand": "Samsung", "type": "IPS LCD", "name": "A20 / A205", "retail": 88000, "wholesale": 65000, "stock": 5},
    {"id": "1488", "brand": "Samsung", "type": "IPS LCD", "name": "A31 / A315N / A315F", "retail": 94000, "wholesale": 69000, "stock": 5},
    {"id": "1489", "brand": "Samsung", "type": "IPS LCD", "name": "A56WF", "retail": 177000, "wholesale": 131000, "stock": 5},
    {"id": "1490", "brand": "Vivo", "type": "Incell HD+", "name": "C21Y / C25Y", "retail": 83000, "wholesale": 61000, "stock": 5},
    {"id": "1491", "brand": "Oppo", "type": "Incell HD+", "name": "A59 / F1S", "retail": 80000, "wholesale": 59000, "stock": 5},
    {"id": "1492", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "BG6 / BG7 / POP8 / X6525 / X6526 / X6528 / KJ5 / KJ5N / SPARKGO2024 / SPARK20C / SPARK20 / SMART8 / SMARTHD / HOTE40I / SMART8PLUS / SMART8PRO / 6525B / P55PLUS / P663L / P663IN / BG6H / X6528B / S24 / BG6I / NOTE40PRO5G / NOTE30VIP / NOTE20PRO", "retail": 88000, "wholesale": 65000, "stock": 5},
    {"id": "1493", "brand": "iPhone", "type": "Incell HD+", "name": "X", "retail": 130000, "wholesale": 96000, "stock": 4},
    {"id": "1494", "brand": "iPhone", "type": "Incell HD+", "name": "11", "retail": 126000, "wholesale": 93000, "stock": 4},
    {"id": "1495", "brand": "iPhone", "type": "Incell HD+", "name": "11-FHD", "retail": 176000, "wholesale": 130000, "stock": 4},
    {"id": "1496", "brand": "Samsung", "type": "IPS LCD", "name": "A11 2020 / A115", "retail": 91000, "wholesale": 67000, "stock": 4},
    {"id": "1497", "brand": "Samsung", "type": "TFT", "name": "S22+WF", "retail": 241000, "wholesale": 178000, "stock": 4},
    {"id": "1498", "brand": "Samsung", "type": "IPS LCD", "name": "S24WF", "retail": 420000, "wholesale": 311000, "stock": 4},
    {"id": "1499", "brand": "Honor", "type": "Incell HD+", "name": "Magic7 Lite / X9C", "retail": 214000, "wholesale": 158000, "stock": 4},
    {"id": "1500", "brand": "Vivo", "type": "OLED", "name": "Y100 4G", "retail": 303000, "wholesale": 224000, "stock": 4},
    {"id": "1501", "brand": "iPhone", "type": "Incell HD+", "name": "13", "retail": 154000, "wholesale": 114000, "stock": 3},
    {"id": "1502", "brand": "iPhone", "type": "Incell HD+", "name": "12MINI-FHD", "retail": 219000, "wholesale": 162000, "stock": 3},
    {"id": "1503", "brand": "Samsung", "type": "TFT", "name": "S22WF", "retail": 304000, "wholesale": 225000, "stock": 3},
    {"id": "1504", "brand": "Samsung", "type": "TFT", "name": "S23WF", "retail": 279000, "wholesale": 206000, "stock": 3},
    {"id": "1505", "brand": "Huawei", "type": "Incell HD+", "name": "NOVA Y90", "retail": 99000, "wholesale": 73000, "stock": 3},
    {"id": "1506", "brand": "Honor", "type": "Incell HD+", "name": "X7B WF", "retail": 142000, "wholesale": 105000, "stock": 3},
    {"id": "1507", "brand": "Honor", "type": "Incell HD+", "name": "RY X6C", "retail": 98000, "wholesale": 72000, "stock": 3},
    {"id": "1508", "brand": "Honor", "type": "Incell HD+", "name": "X7D 5G", "retail": 99000, "wholesale": 73000, "stock": 3},
    {"id": "1509", "brand": "Oppo", "type": "OLED", "name": "RENO 8T 5G", "retail": 354000, "wholesale": 262000, "stock": 3},
    {"id": "1510", "brand": "Samsung", "type": "IPS LCD", "name": "A30 / A50 / A50S", "retail": 95000, "wholesale": 70000, "stock": 2},
    {"id": "1511", "brand": "Samsung", "type": "IPS LCD", "name": "A6+ 2018 / A605", "retail": 92000, "wholesale": 68000, "stock": 2},
    {"id": "1512", "brand": "Samsung", "type": "IPS LCD", "name": "A32 4G / A325 / A32 LITE WF", "retail": 127000, "wholesale": 94000, "stock": 2},
    {"id": "1513", "brand": "Samsung", "type": "IPS LCD", "name": "A515 / A516 / M31S-WF", "retail": 126000, "wholesale": 93000, "stock": 2},
    {"id": "1514", "brand": "Samsung", "type": "TFT", "name": "S21WF", "retail": 212000, "wholesale": 157000, "stock": 2},
    {"id": "1515", "brand": "Samsung", "type": "TFT", "name": "S21+WF", "retail": 212000, "wholesale": 157000, "stock": 2},
    {"id": "1516", "brand": "Huawei", "type": "Servis", "name": "P40 LITE / NOVA 5I / NOVA 7I", "retail": 184000, "wholesale": 136000, "stock": 2},
    {"id": "1517", "brand": "Huawei", "type": "Servis", "name": "NOVA10PRO", "retail": 663000, "wholesale": 491000, "stock": 2},
    {"id": "1518", "brand": "Honor", "type": "Incell HD+", "name": "X50i / X8A / X8 2023", "retail": 94000, "wholesale": 69000, "stock": 2},
    {"id": "1519", "brand": "Honor", "type": "Incell HD+", "name": "RY X5", "retail": 90000, "wholesale": 66000, "stock": 2},
    {"id": "1520", "brand": "Huawei", "type": "Incell HD+", "name": "Y70 / NOVA Y70 / MAIMANG11 / Y71", "retail": 94000, "wholesale": 69000, "stock": 2},
    {"id": "1521", "brand": "Huawei", "type": "Incell HD+", "name": "CW40 / RY X6A / CW40C / X5 Plus / X5B / X5B Plus", "retail": 88000, "wholesale": 65000, "stock": 2},
    {"id": "1522", "brand": "Realme", "type": "Incell HD+", "name": "A32 4G / A33 / A53 4G / A53S / A54 4G / A55 4G / REALME7I / REALMEC17 / 1+N100", "retail": 86000, "wholesale": 63000, "stock": 2},
    {"id": "1523", "brand": "Realme", "type": "Incell HD+", "name": "REALMEC53 / C51 / C60 / NOTE50 / C36", "retail": 90000, "wholesale": 66000, "stock": 2},
    {"id": "1524", "brand": "Vivo", "type": "Incell HD+", "name": "V20SE / S6 / G1 / S7E / Y70 / Y73S / X50E", "retail": 90000, "wholesale": 66000, "stock": 2},
    {"id": "1525", "brand": "Vivo", "type": "Incell HD+", "name": "V21-V2066 / S9e-V2048A / V21 5G-V2050 / S15e-V2190A / VIVO T1 5G-V2150 / VIVO T1 Pro 5G-V2151 / V25-V2202 / 25e-V2201 / x80 Lite 5G-V2208", "retail": 104000, "wholesale": 77000, "stock": 2},
    {"id": "1526", "brand": "Realme", "type": "Incell HD+", "name": "C61 / C63 / N61 / N63 / C65S / Realme note60", "retail": 92000, "wholesale": 68000, "stock": 2},
    {"id": "1527", "brand": "Realme", "type": "Incell HD+", "name": "C65 4G / C65 5G / A40 / A60 / A80 / V60 / V60S / A3PRO", "retail": 103000, "wholesale": 76000, "stock": 2},
    {"id": "1528", "brand": "iPhone", "type": "Incell HD+", "name": "11PRO", "retail": 149000, "wholesale": 110000, "stock": 1},
    {"id": "1529", "brand": "iPhone", "type": "Incell HD+", "name": "15", "retail": 179000, "wholesale": 132000, "stock": 1},
    {"id": "1530", "brand": "iPhone", "type": "Incell HD+", "name": "12PROMAX-FHD", "retail": 287000, "wholesale": 212000, "stock": 1},
    {"id": "1531", "brand": "Samsung", "type": "IPS LCD", "name": "A14 4G / A145P / A145B", "retail": 83000, "wholesale": 61000, "stock": 1},
    {"id": "1532", "brand": "Samsung", "type": "Premium", "name": "A12 / A02 / A125 / A127 2021 / A022 / M12", "retail": 95000, "wholesale": 70000, "stock": 1},
    {"id": "1533", "brand": "Samsung", "type": "IPS LCD", "name": "A70 2019 / A705-WF", "retail": 114000, "wholesale": 84000, "stock": 1},
    {"id": "1534", "brand": "Samsung", "type": "IPS LCD", "name": "A24 4G-WF", "retail": 115000, "wholesale": 85000, "stock": 1},
    {"id": "1535", "brand": "Samsung", "type": "OLED", "name": "S22ultra / S908-WF", "retail": 789000, "wholesale": 584000, "stock": 1},
    {"id": "1536", "brand": "Samsung", "type": "IPS LCD", "name": "A30S-WF", "retail": 106000, "wholesale": 78000, "stock": 1},
    {"id": "1537", "brand": "Samsung", "type": "IPS LCD", "name": "A33WF", "retail": 137000, "wholesale": 101000, "stock": 1},
    {"id": "1538", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE11 4G WF", "retail": 119000, "wholesale": 88000, "stock": 1},
    {"id": "1539", "brand": "Redmi", "type": "Incell HD+", "name": "NOTE11S WF", "retail": 133000, "wholesale": 98000, "stock": 1},
    {"id": "1540", "brand": "Honor", "type": "Incell HD+", "name": "X7B", "retail": 99000, "wholesale": 73000, "stock": 1},
    {"id": "1541", "brand": "Honor", "type": "Incell HD+", "name": "X9B WF", "retail": 484000, "wholesale": 358000, "stock": 1},
    {"id": "1542", "brand": "Huawei", "type": "Servis", "name": "NOVA12 SE", "retail": 211000, "wholesale": 156000, "stock": 1},
    {"id": "1543", "brand": "Honor", "type": "Servis", "name": "RY X5B", "retail": 131000, "wholesale": 97000, "stock": 1},
    {"id": "1544", "brand": "Huawei", "type": "OLED", "name": "NOVA12 SE", "retail": 489000, "wholesale": 362000, "stock": 1},
    {"id": "1545", "brand": "Honor", "type": "Incell HD+", "name": "Magic6 Lite 5G / X9B / X40", "retail": 216000, "wholesale": 160000, "stock": 1},
    {"id": "1546", "brand": "Vivo", "type": "Incell HD+", "name": "Y56 5G / Y35 4G", "retail": 95000, "wholesale": 70000, "stock": 1},
    {"id": "1547", "brand": "Oppo", "type": "OLED", "name": "GT MASTER", "retail": 508000, "wholesale": 376000, "stock": 1},
    {"id": "1548", "brand": "Oppo", "type": "Incell HD+", "name": "A77S", "retail": 84000, "wholesale": 62000, "stock": 1},
    {"id": "1549", "brand": "Tecno & Infinix", "type": "IPS LCD", "name": "KD6 / SPARK5AIR / LC7 / LC7S / LC8 / KE6 / SPARK6AIR / KD6A / KE6J / POUVOIR4 / POUVOIR4PRO / SPARKPOWER2", "retail": 92000, "wholesale": 68000, "stock": 1},
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

_catalog_version_ok = False

def _reseed_if_new_version():
    """CATALOG_VERSION o'zgarsa, bazadagi katalog va qoldiqni SEED_CATALOG bilan bir marta almashtiradi."""
    global _catalog_version_ok
    if _catalog_version_ok:
        return
    # Preview deploy ham shu bazaga ulangan bo'lishi mumkin: faqat production qayta yozadi
    if os.environ.get("VERCEL_ENV", "production") != "production":
        return
    if store_get("meta", "catalog_version") != CATALOG_VERSION:
        log.info("Yangi katalog versiyasi %s: katalog va qoldiq qaytadan yoziladi", CATALOG_VERSION)
        if REDIS_URL:
            _redis("DEL", "catalog", "stock")
        else:
            _file_save("catalog", {})
            _file_save("stock", {})
        _set_many("catalog", {p["id"]: {k: p[k] for k in ("brand", "type", "name", "retail", "wholesale")} | {"active": True}
                              for p in SEED_CATALOG})
        _set_many("stock", {p["id"]: int(p.get("stock") or 0) for p in SEED_CATALOG})
        store_set("meta", "catalog_version", CATALOG_VERSION)
        store_set("meta", "price_version", PRICE_VERSION)
    elif store_get("meta", "price_version") != PRICE_VERSION:
        log.info("Yangi narx versiyasi %s: faqat narxlar yangilanadi", PRICE_VERSION)
        cat = store_all("catalog")
        seed = {p["id"]: p for p in SEED_CATALOG}
        _set_many("catalog", {pid: {**v, "retail": seed[pid]["retail"], "wholesale": seed[pid]["wholesale"]}
                              for pid, v in cat.items() if pid in seed})
        store_set("meta", "price_version", PRICE_VERSION)
    _catalog_version_ok = True

def _ensure_catalog():
    """Baza bo'sh bo'lsa, boshlang'ich katalogni bir marta yozib qo'yadi."""
    _reseed_if_new_version()
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
