"""Ekranchi Telegram bot (Vercel serverless, Flask).

Vercel > Settings > Environment Variables ga quyidagilarni qo'shing:
  BOT_TOKEN        - @BotFather dan olingan YANGI token (eskisini revoke qiling!)
  ADMIN_ID         - admin Telegram ID raqami
  WEBHOOK_SECRET   - istalgan uzun tasodifiy satr (faqat A-Z a-z 0-9 _ -)
  WEB_APP_URL      - (ixtiyoriy) market.html manzili
  CARD_NUMBER, CARD_NAME - (ixtiyoriy) to'lov kartasi
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
WEB_APP_URL = os.environ.get("WEB_APP_URL", "https://bekzodmatkarimov7770-cyber.github.io/Ekranchi-shop/market.html?v=wow_v4")
CARD_NUMBER = os.environ.get("CARD_NUMBER", "9860 1266 0304 4796")
CARD_NAME = os.environ.get("CARD_NAME", "Bekzod M. (Humo / Uzcard)")

PUBLIC_URL = os.environ.get("PUBLIC_URL", "https://ekranchi-shop.vercel.app").rstrip("/")

WHOLESALE_MIN = 50          # shuncha va undan ko'p dona bo'lsa optom narx
MAX_QTY_PER_ITEM = 9999
ALLOWED_DELIVERY = {"BTS", "Taksi"}

# Vercel Marketplace Upstash integratsiyasi KV_REST_API_* nomlarini qo'shadi
REDIS_URL = (os.environ.get("UPSTASH_REDIS_REST_URL") or os.environ.get("KV_REST_API_URL") or "").rstrip("/")
REDIS_TOKEN = os.environ.get("UPSTASH_REDIS_REST_TOKEN") or os.environ.get("KV_REST_API_TOKEN") or ""

CATALOG = {
    '1': {'n': 'A02S / A03S / A03 / A035 / A025 / A04E / A042', 'w': 57000, 'r': 77000},
    '2': {'n': 'A10 2019 / A105 / M10 / M105', 'w': 57000, 'r': 77000},
    '3': {'n': 'POCO M3 / 9T', 'w': 62000, 'r': 84000},
    '4': {'n': '13C 4G / 13C 5G / POCO C65 / 13R / POCO M6 5G', 'w': 63000, 'r': 86000},
    '5': {'n': 'NOTE8 PRO', 'w': 64000, 'r': 87000},
    '6': {'n': 'A135F / A13 4G / A13 LITE / A135 / A137 / F13 / M13', 'w': 59000, 'r': 80000},
    '7': {'n': 'A10S 2020 / A107', 'w': 57000, 'r': 77000},
    '8': {'n': 'Y21T / Y16 / y21 / Y15A / Y15S / Y21A / Y21e / Y21G / Y21S / Y33E / Y31S / Y32 / Y01 / Y02S', 'w': 57000, 'r': 77000},
    '9': {'n': '11A / POCO C55 / A11 / 12C', 'w': 62000, 'r': 84000},
    '10': {'n': '9 PRIME / POCO M2', 'w': 62000, 'r': 84000},
    '11': {'n': 'A20S 2020 / A207', 'w': 59000, 'r': 80000},
    '12': {'n': '10X / NOTE 9', 'w': 66000, 'r': 90000},
    '13': {'n': 'J4+ / J6+ / J415 / J610 / J410', 'w': 57000, 'r': 77000},
    '14': {'n': 'A1 / A1+ / A2 / A2+', 'w': 57000, 'r': 77000},
    '15': {'n': 'A13 5G / A04S / A136U / A047 / A04CORE', 'w': 58000, 'r': 79000},
    '16': {'n': 'A01CORE / A013 / A3CORE', 'w': 60000, 'r': 81000},
    '17': {'n': '10 4G / 10-2022 / 10 prime / 10prime 2022', 'w': 68000, 'r': 92000},
    '18': {'n': 'A5 4G / A5 5G / A5 New / Poco C71', 'w': 66000, 'r': 90000},
    '19': {'n': 'BE8 / HOT12 / Hot20i / POP6 Pro / TECNO SPARK8C / SPARK 8C / SPARK9 / SPARK 9T / SMART 6HD / Hot 12i / HOT12 PRO', 'w': 59000, 'r': 80000},
    '20': {'n': '15C 4G', 'w': 67000, 'r': 91000},
    '21': {'n': 'A15 / M15 / M156', 'w': 66000, 'r': 90000},
    '22': {'n': 'A3 / A3X / POCO C61(yin du)', 'w': 62000, 'r': 84000},
    '23': {'n': 'Hot11 / Spark8P / Spark8t / S18pro / S662L / vision5plus / S662LC / SPARK9PRO', 'w': 63000, 'r': 86000},
    '24': {'n': 'A04 / A045', 'w': 60000, 'r': 81000},
    '25': {'n': 'NOTE10 5G / Note11SE / Note10T 5G / POCO M3 PRO', 'w': 68000, 'r': 92000},
    '26': {'n': 'A06 4G / A065', 'w': 63000, 'r': 86000},
    '27': {'n': 'BD4 / SMART6 / BD4A / BD4I / BD4J / BD4H / SPARK GO2022 / POP5LTE / POP5PRO / BD4T', 'w': 58000, 'r': 79000},
    '28': {'n': 'A07 4G', 'w': 66000, 'r': 90000},
    '29': {'n': 'POCO C40 / 10 POWER / 10INDIA / 10C', 'w': 62000, 'r': 84000},
    '30': {'n': 'HOT12 / HOT12PLAY / HOT12PLAYNFC / NOTE12I / LG7N / POVA4 / HOT20PLAY / HOT20 / LG6 / LG6N / POVANEO2 / LH6N / POVANEO3 / HOT30PLAY / 6835', 'w': 66000, 'r': 90000},
    '31': {'n': 'S16 / Smart5 / SparkGo 2020 / Hot10lite / Vision1pro / Vision1plus', 'w': 57000, 'r': 77000},
    '32': {'n': 'MI 11T / MI11T PRO', 'w': 92000, 'r': 125000},
    '33': {'n': 'A11X / A5 2020 / narzo 20A / A9 2020 / A31 2020 / realmeC3 / Realme5 / Realme5S / narzo10A / A8 2020 / Realme6 / Realme6i / Realme7', 'w': 57000, 'r': 77000},
    '34': {'n': '12R / Note 13R / 12 / 13 5G / 13 / POCO M6 PRO 5G / 12 5G', 'w': 66000, 'r': 90000},
    '35': {'n': 'A01F 2020 / A015', 'w': 59000, 'r': 80000},
    '36': {'n': 'NOTE 8', 'w': 65000, 'r': 88000},
    '37': {'n': 'HOT50 / SPARK30 / SPARK30 4G / HOT50 4G', 'w': 75000, 'r': 102000},
    '38': {'n': 'MI 9T / MI9T PRO', 'w': 74000, 'r': 100000},
    '39': {'n': '14C 4G / 14C 5G / Poco C75', 'w': 63000, 'r': 86000},
    '40': {'n': 'A2Core / A260', 'w': 53000, 'r': 72000},
    '41': {'n': 'S17 / A58 / A58PRO 4G / A49 / A661 / A661L / S661W / SMART6+ / SPARK8', 'w': 59000, 'r': 80000},
    '42': {'n': 'A05 / A055F / M05', 'w': 61000, 'r': 83000},
    '43': {'n': 'A05S / A057', 'w': 71000, 'r': 96000},
    '44': {'n': 'M23', 'w': 65000, 'r': 88000},
    '45': {'n': 'NOTE14 PRO 4GWF', 'w': 125000, 'r': 169000},
    '46': {'n': '8A', 'w': 59000, 'r': 80000},
    '47': {'n': 'POCO X3 / X3 PRO / NOTE9 PRO 5G / MI10T LITE 5G', 'w': 71000, 'r': 96000},
    '48': {'n': 'NOTE11 5G / NOTE 11T 5G / NOTE 11S 5G / POCO M4 PRO 5G', 'w': 84000, 'r': 114000},
    '49': {'n': 'SMART5', 'w': 73000, 'r': 99000},
    '50': {'n': '15 4G / 5G', 'w': 81000, 'r': 110000},
    '51': {'n': 'NARZO 50I', 'w': 71000, 'r': 96000},
    '52': {'n': 'NOTE13PRO 4GWF', 'w': 143000, 'r': 194000},
    '53': {'n': 'HOT40PRO / HOT40', 'w': 80000, 'r': 108000},
    '54': {'n': 'A11 2020 / A115', 'w': 76000, 'r': 103000},
    '55': {'n': 'S10+WF', 'w': 170000, 'r': 230000},
    '56': {'n': '6A', 'w': 69000, 'r': 94000},
    '57': {'n': 'NOTE30I / SPARK20SPRO', 'w': 82000, 'r': 111000},
    '58': {'n': 'Y3 / Y13 / Y3S / Y11 / Y12 / Y15 / Y17 / U3X / U10 / 8A', 'w': 71000, 'r': 96000},
    '59': {'n': 'A16 / A16S / A16K / A15 / A15S / A35 / A54S / A56 4G / 5G / A55 5G', 'w': 71000, 'r': 96000},
    '60': {'n': 'HOT11S / CH6 / CG7 / Camon17PRO / CH7 / Camon18PRO / CI8 / KI7 / LI6 / SPARK8PRO / KJ6 / KJ8', 'w': 77000, 'r': 104000},
    '61': {'n': 'BD3 / KF6 / KF6H / KF6i / KF6J / Spark7 / PR651 / PR651H / POP5P / Smart5Pro / PR652B / Vision2S / HOT10i', 'w': 69000, 'r': 94000},
    '62': {'n': 'KI7 / SPARK10PRO / HOT30 / POVA5 / LH7 / NOTE30 / LH7N', 'w': 78000, 'r': 106000},
    '63': {'n': 'IQ00 Z7x(m) / VIVO Y100i / VIVO Y78m / IQ00 Z7 / VIVO Y78 / IQ00 Z7X / IQ00 Z8 / IQ00 Z8x / VIVO Y77T-5G / VIVO Y78T / VIVO Y78（t1） / VIVO Y100T / VIVO Y36-4G / VIVO Y36 5G', 'w': 68000, 'r': 92000},
    '64': {'n': 'NOTE11PRO 4GWF', 'w': 108000, 'r': 146000},
    '65': {'n': 'NOTE13 PRO 4G', 'w': 87000, 'r': 118000},
    '66': {'n': 'Y3', 'w': 73000, 'r': 99000},
    '67': {'n': 'NOTE 9S / NOTE9 PRO 4G / NOTE9 PROMAX / NOTE10 LITE / XM POCO M2 PRO', 'w': 70000, 'r': 95000},
    '68': {'n': 'CD7 / CD7H / CD6 / CD6J.S / HOT9 / HOT9PRO / SPARK5 / SPARK5PRO / Camon5 / Camon 5air / Note 7lite', 'w': 71000, 'r': 96000},
    '69': {'n': 'Y20 / Y20I / Y20S / Y15A / Y15S / Y11S / Y12S / Y12A / (NEIDAN)Y30 / Y30G / Y31S / IQOOU1X / Y10-(T1 / T2) / Y02', 'w': 66000, 'r': 90000},
    '70': {'n': 'F3 / F4 / Mi 11i / Mi11x / Mi11x Pro / Shark 4 / 4Pro', 'w': 85000, 'r': 115000},
    '71': {'n': 'HOT10 / CE7 / CE7J / LD7 / LD7J / SPARK6 / Pova / Note8i / Camon16 / Camon16SE', 'w': 78000, 'r': 106000},
    '72': {'n': '7A', 'w': 68000, 'r': 92000},
    '73': {'n': 'A6 2018 / A600', 'w': 75000, 'r': 102000},
    '74': {'n': 'NOTE11 / NOTE12', 'w': 79000, 'r': 107000},
    '75': {'n': 'A325N / A325M / A325F / M325FV / M325F', 'w': 79000, 'r': 107000},
    '76': {'n': 'A31 2020 / A315-WF', 'w': 94000, 'r': 127000},
    '77': {'n': 'A15 / A15S / A35 / V3 / A16K / Q2i / Narzo20 / Narzo30a / Rearlme 7i', 'w': 71000, 'r': 96000},
    '78': {'n': 'SPARK6GO', 'w': 69000, 'r': 94000},
    '79': {'n': 'MI 8 LITE', 'w': 73000, 'r': 99000},
    '80': {'n': 'X9C WF', 'w': 372000, 'r': 503000},
    '81': {'n': 'KF7J / SPARK7P / HOT10T / HOT10S / SMART6PLUS / VISION3+ / KF7', 'w': 75000, 'r': 102000},
    '82': {'n': 'A14 5G / A146B / A146F / A145F / A145M(BIG）', 'w': 74000, 'r': 100000},
    '83': {'n': 'LE6 / HOT10PLAY / HOT11PLAY / POVANEO / LE6H / VOSON2+', 'w': 73000, 'r': 99000},
    '84': {'n': 'A36 / A56', 'w': 93000, 'r': 126000},
    '85': {'n': 'NOTE14 4G WF', 'w': 102000, 'r': 138000},
    '86': {'n': 'POCO X3 GT / NOTE10PRO 5G', 'w': 81000, 'r': 110000},
    '87': {'n': 'NOTE 6 / NOTE6 PRO', 'w': 80000, 'r': 108000},
    '88': {'n': 'MI 8', 'w': 104000, 'r': 141000},
    '89': {'n': 'POCO X4 GT', 'w': 93000, 'r': 126000},
    '90': {'n': 'RY X8C', 'w': 180000, 'r': 244000},
    '91': {'n': 'A325 / A32 4G / M32 / M325 / F325 / A32LITE', 'w': 244000, 'r': 330000},
    '92': {'n': 'KJ6 / SPARK20PRO', 'w': 82000, 'r': 111000},
    '93': {'n': 'Note11 / Note12 5G(X671) / Note12pro 4G / 5G(X676B) / Note20 / Note12i', 'w': 81000, 'r': 110000},
    '94': {'n': 'A16-WF', 'w': 98000, 'r': 133000},
    '95': {'n': 'Y93 / Y93A / Y93T / Y91 / Y95 / U1 / Y1S', 'w': 71000, 'r': 96000},
    '96': {'n': 'NOTE12 4G-WF', 'w': 109000, 'r': 148000},
    '97': {'n': 'MI 9', 'w': 125000, 'r': 169000},
    '98': {'n': 'A34 4G-WF', 'w': 116000, 'r': 157000},
    '99': {'n': 'RY  X9', 'w': 88000, 'r': 119000},
    '100': {'n': 'X6C WF', 'w': 125000, 'r': 169000},
    '101': {'n': 'A7 2018 / A750', 'w': 79000, 'r': 107000},
    '102': {'n': 'Y7 2019 / Y7PRO 2019', 'w': 71000, 'r': 96000},
    '103': {'n': 'Y29 4G / Y300I', 'w': 78000, 'r': 106000},
    '104': {'n': 'A12 / A02 / A125 / A127 2021 / A022 / M12', 'w': 69000, 'r': 94000},
    '105': {'n': 'MI 14TPRO / MI14T', 'w': 137000, 'r': 185000},
    '106': {'n': 'KC8 / KC8S / CC7 / CC7S / KC2 / KC2J / HOT8 / HOT8LITE / CAMON12 / SPARK4', 'w': 68000, 'r': 92000},
    '107': {'n': 'BG6 / BG7 / POP8 / KJ5 / KJ5N / SPARKGO2024 / SPARK20C / SPARK20 / SMART8 / SMARTHD / HOTE40I / SMART8PLUS / SMART8PRO / 6525B / BG6H / S24 / BG6I / NOTE40PRO5G / NOTE30VIP / NOTE20PRO', 'w': 71000, 'r': 96000},
    '108': {'n': 'A17WF', 'w': 101000, 'r': 137000},
    '109': {'n': 'SPARK GO 2021', 'w': 73000, 'r': 99000},
    '110': {'n': 'RENO5LITE WF', 'w': 108000, 'r': 146000},
    '111': {'n': 'Y19 / Y5S / Z5I / U3 / U20', 'w': 73000, 'r': 99000},
    '112': {'n': 's6-V1962A / y73s-V2031A / G1-V1962BA / S7 E-V2031A / S10E-V2130A / T1 4G-V2153 / y55 4G-V2154 / Y70外-V2023 / T1 4G-V2168', 'w': 75000, 'r': 102000},
    '113': {'n': 'POVA4PRO / LG8 / LG8N', 'w': 93000, 'r': 126000},
    '114': {'n': 'X8CWF', 'w': 282000, 'r': 381000},
    '115': {'n': 'SPARK8C / S18 / Smart6 / SPARK9T / VISON3 / S661L / S663L / Vision5', 'w': 67000, 'r': 91000},
    '116': {'n': 'NOTE14PRO 4G', 'w': 116000, 'r': 157000},
    '117': {'n': 'NOTE30PRO', 'w': 82000, 'r': 111000},
    '118': {'n': 'MI 12T PRO / MI12T', 'w': 107000, 'r': 145000},
    '119': {'n': 'Y28 4G / Y38 5G / Y37PRO / Y19S / Y29 5G / Y200+', 'w': 77000, 'r': 104000},
    '120': {'n': 'KF8 / Spark7Pro / CG6 / CG6J / Camon17 / Camon18i', 'w': 73000, 'r': 99000},
    '121': {'n': 'X6AWF', 'w': 99000, 'r': 134000},
    '122': {'n': 'A30 / A50 / A50S-WF', 'w': 92000, 'r': 125000},
    '123': {'n': 'A8 2018 / A530', 'w': 79000, 'r': 107000},
    '124': {'n': 'J3 2016 / J320 / J300', 'w': 67000, 'r': 91000},
    '125': {'n': 'RY X8 WF', 'w': 133000, 'r': 180000},
    '126': {'n': 'A15WF', 'w': 94000, 'r': 127000},
    '127': {'n': 'GT20PRO', 'w': 89000, 'r': 121000},
    '128': {'n': 'NOTE13PRO PLUS WF', 'w': 143000, 'r': 194000},
    '129': {'n': 'POP5LITE', 'w': 75000, 'r': 102000},
    '130': {'n': 'Y35+ / Y35M+ / Y27 4G / Y36 / Y27 5G', 'w': 78000, 'r': 106000},
    '131': {'n': 'A6+ 2018 / A605', 'w': 82000, 'r': 111000},
    '132': {'n': 'NOTE40S', 'w': 89000, 'r': 121000},
    '133': {'n': 'Y6P / RY 9A', 'w': 75000, 'r': 102000},
    '134': {'n': 'X9C SMART', 'w': 97000, 'r': 131000},
    '135': {'n': 'Realme8i / Realme9i / A96 4G / Narzo50', 'w': 76000, 'r': 103000},
    '136': {'n': 'RY X8B', 'w': 187000, 'r': 253000},
    '137': {'n': 'CK7 / CK7N / CAMON20PRO', 'w': 80000, 'r': 108000},
    '138': {'n': 'RY X8B WF', 'w': 221000, 'r': 299000},
    '139': {'n': 'A315 / A31-WF', 'w': 226000, 'r': 306000},
    '140': {'n': 'X8BWF', 'w': 272000, 'r': 368000},
    '141': {'n': 'A16 4GWF', 'w': 327000, 'r': 442000},
    '142': {'n': 'Y27S', 'w': 79000, 'r': 107000},
    '143': {'n': 'V40LITE', 'w': 99000, 'r': 134000},
    '144': {'n': 'NOTE12 PRO-WF', 'w': 104000, 'r': 141000},
    '145': {'n': 'POP8PRO', 'w': 77000, 'r': 104000},
    '146': {'n': 'A336 / A33-WF', 'w': 116000, 'r': 157000},
    '147': {'n': 'NOTE11 4G / NOTE11S / M4PRO 4G / NOTE12S', 'w': 83000, 'r': 113000},
    '148': {'n': 'NOTE8T', 'w': 71000, 'r': 96000},
    '149': {'n': 'NOTE7 / NOTE7PRO / NOTE7PLUS / NOTE 7S', 'w': 67000, 'r': 91000},
    '150': {'n': 'RY X8', 'w': 78000, 'r': 106000},
    '151': {'n': 'NOTE8 Overseas version', 'w': 66000, 'r': 90000},
    '152': {'n': 'Camon30 / CL7 / CL6K / CL6', 'w': 88000, 'r': 119000},
    '153': {'n': 'V40', 'w': 143000, 'r': 194000},
    '154': {'n': 'A36 / A76 / A76New', 'w': 78000, 'r': 106000},
    '155': {'n': 'NOTE12PRO-WF', 'w': 101000, 'r': 137000},
    '156': {'n': 'A53 / A536', 'w': 84000, 'r': 114000},
    '157': {'n': 'X7C WF', 'w': 117000, 'r': 158000},
    '158': {'n': 'MI10T / MI10T PRO', 'w': 91000, 'r': 123000},
    '159': {'n': 'X9AWF', 'w': 320000, 'r': 432000},
    '160': {'n': 'J1 2016 / J120', 'w': 67000, 'r': 91000},
    '161': {'n': 'PLAY6TPRO / PLAY7TPRO', 'w': 111000, 'r': 150000},
    '162': {'n': 'A15 / A155 / A156-WF', 'w': 298000, 'r': 403000},
    '163': {'n': 'X9D WF', 'w': 334000, 'r': 451000},
    '164': {'n': 'X9B WF', 'w': 369000, 'r': 499000},
    '165': {'n': 'CAMON15 / 15AIR', 'w': 75000, 'r': 102000},
    '166': {'n': 'ZERO40', 'w': 104000, 'r': 141000},
    '167': {'n': 'Y02 / Y02T / Y02A / Y11-2023', 'w': 69000, 'r': 94000},
    '168': {'n': 'A20 / A205', 'w': 73000, 'r': 99000},
    '169': {'n': 'realme C31', 'w': 73000, 'r': 99000},
    '170': {'n': 'A515 / A51-WF', 'w': 261000, 'r': 353000},
    '171': {'n': 'CC6 / KC3 / CAMON12AIR / S5 / S5LITE', 'w': 72000, 'r': 98000},
    '172': {'n': 'NOTE11 4G-WF', 'w': 101000, 'r': 137000},
    '173': {'n': 'J3Prime / J327', 'w': 80000, 'r': 108000},
    '174': {'n': 'REALME5PRO / REALME Q', 'w': 80000, 'r': 108000},
    '175': {'n': 'NOTE40PRO 4G', 'w': 104000, 'r': 141000},
    '176': {'n': 'S20 4GWF', 'w': 182000, 'r': 246000},
    '177': {'n': 'RY 10LITE(2018)', 'w': 77000, 'r': 104000},
    '178': {'n': 'A26WF', 'w': 130000, 'r': 176000},
    '179': {'n': 'A36WF', 'w': 136000, 'r': 184000},
    '180': {'n': 'A20 2019 / A205-WF', 'w': 84000, 'r': 114000},
    '181': {'n': 'NARZO50IPRIME', 'w': 71000, 'r': 96000},
    '182': {'n': 'V20E', 'w': 78000, 'r': 106000},
    '183': {'n': 'HM5', 'w': 74000, 'r': 100000},
    '184': {'n': 'A30S 2020 / A307', 'w': 73000, 'r': 99000},
    '185': {'n': 'RY X7A', 'w': 77000, 'r': 104000},
    '186': {'n': 'POVA NEO6', 'w': 81000, 'r': 110000},
    '187': {'n': 'A60 4G / Realme C65 4G / Realme C65 5G / Realme Narzo N65 / Realme 12X 5G / Realme 14X 5G / Realme C75x / OPPO A3 Pro / Realme V60 / Realme V60s / OPPO K12x 5G / OPPO A3X 4G / OPPO A3X 5G / OPPO A35G', 'w': 84000, 'r': 114000},
    '188': {'n': 'NOVA10 SE / NOVA11SE / NOVA12SE', 'w': 148000, 'r': 200000},
    '189': {'n': 'X9A WF', 'w': 327000, 'r': 442000},
    '190': {'n': 'N61 / N63 / Realme note60', 'w': 76000, 'r': 103000},
    '191': {'n': 'REALME12X 5G / REALME12 5G / NARZO70X 5G', 'w': 80000, 'r': 108000},
    '192': {'n': 'M53', 'w': 100000, 'r': 135000},
    '193': {'n': 'SPARK GO 2', 'w': 79000, 'r': 107000},
    '194': {'n': 'ZEROX NEO', 'w': 84000, 'r': 114000},
    '195': {'n': 'A57 WF', 'w': 97000, 'r': 131000},
    '196': {'n': 'F19PROWF', 'w': 99000, 'r': 134000},
    '197': {'n': 'XR-FHD', 'w': 149000, 'r': 202000},
    '198': {'n': 'A52WF', 'w': 117000, 'r': 158000},
    '199': {'n': 'XS-F(Q-X)', 'w': 372000, 'r': 503000},
    '200': {'n': 'J2Core / J260', 'w': 67000, 'r': 91000},
    '201': {'n': 'XR', 'w': 87000, 'r': 118000},
    '202': {'n': 'XS', 'w': 92000, 'r': 125000},
    '203': {'n': 'X', 'w': 92000, 'r': 125000},
    '204': {'n': 'NOTE14 4G', 'w': 85000, 'r': 115000},
    '205': {'n': 'A35WF', 'w': 127000, 'r': 172000},
    '206': {'n': 'A24-4G / Galaxy A25 5G / Galaxy M34 5G / A26-Galaxy F34 5G', 'w': 81000, 'r': 110000},
    '207': {'n': 'X8A / X8 2023', 'w': 83000, 'r': 113000},
    '208': {'n': 'NOTE8WF', 'w': 211000, 'r': 285000},
    '209': {'n': 'KM5 / SPARK GO1 / A80(A671L)', 'w': 75000, 'r': 102000},
    '210': {'n': 'A7 / A5S / A7n / AX5S / A12 / Realme3 / Realme3i', 'w': 69000, 'r': 94000},
    '211': {'n': 'REALME12X 5G / REALME12 5G / NARZO70X 5G', 'w': 87000, 'r': 118000},
    '212': {'n': 'A5 / A3S / Realme2 / A5低 / A12e / AX5 / RealmeC1', 'w': 74000, 'r': 100000},
    '213': {'n': '15PRO', 'w': 140000, 'r': 189000},
    '214': {'n': 'A77 / A78WF', 'w': 102000, 'r': 138000},
    '215': {'n': 'A14 4G / A145P / A145B', 'w': 67000, 'r': 91000},
    '216': {'n': '13PROMAX', 'w': 148000, 'r': 200000},
    '217': {'n': 'NOTE9WF', 'w': 211000, 'r': 285000},
    '218': {'n': 'SPARK30PRO / HOT50PRO / S25 / S685LN', 'w': 86000, 'r': 117000},
    '219': {'n': 'realme9 pro plus / realme9 4g / reno7 / oneplus nord ce 2 5G / reno 8t / REALME10 4G', 'w': 83000, 'r': 113000},
    '220': {'n': '11PROMAX', 'w': 108000, 'r': 146000},
    '221': {'n': 'SPARK5AIR / LC7 / LC7S / LC8 / SPARK6AIR / POUVOIR4 / POUVOIR4PRO / SPARKPOWER2', 'w': 77000, 'r': 104000},
    '222': {'n': 'S10WF', 'w': 170000, 'r': 230000},
    '223': {'n': 'X-F(Q)', 'w': 362000, 'r': 489000},
    '224': {'n': 'NOTE10+WF', 'w': 232000, 'r': 314000},
    '225': {'n': 'S23U(USA version)WF', 'w': 236000, 'r': 319000},
    '226': {'n': 'NOTE10-WF', 'w': 242000, 'r': 327000},
    '227': {'n': 'A60 4G / Realme C65 4G / Realme C65 5G / Realme Narzo N65 / Realme 12X 5G / Realme 14X 5G / Realme C75x / OPPO A3 Pro / Realme V60 / Realme V60s / OPPO K12x 5G / OPPO A3X 4G / OPPO A3X 5G / OPPO A3 5G', 'w': 79000, 'r': 107000},
    '228': {'n': 'A35 / A55 4G WF', 'w': 144000, 'r': 195000},
    '229': {'n': 'S21UWF', 'w': 195000, 'r': 264000},
    '230': {'n': 'A52 / A525 A52 4G-WF', 'w': 117000, 'r': 158000},
    '231': {'n': 'Smart 6 HD / Hot 12i / Smart 6HD 2022 / hot20i', 'w': 73000, 'r': 99000},
    '232': {'n': 'Y04 / Y19E / Y29E / Y29S', 'w': 77000, 'r': 104000},
    '233': {'n': 'RY X10 LITE / Y7A / PSMART 2021', 'w': 81000, 'r': 110000},
    '234': {'n': 'Realme8i-5G／A96／K10／narzo50／Realme9i / OPPO A36 / A76 / Realme9pro／K9S / reaimeQ3S／realmeQ3T／Realme v25／realmeQ5／1＋CE2lite / 1+ACE', 'w': 88000, 'r': 119000},
    '235': {'n': 'M52 / M53 / M54', 'w': 89000, 'r': 121000},
    '236': {'n': 'A22 5G(2021) / A226', 'w': 71000, 'r': 96000},
    '237': {'n': 'POVA6NEO', 'w': 79000, 'r': 107000},
    '238': {'n': 'PSMART 2021 / Y7A / RY X10 LITE', 'w': 76000, 'r': 103000},
    '239': {'n': '11', 'w': 89000, 'r': 121000},
    '240': {'n': 'A73-WF', 'w': 126000, 'r': 171000},
    '241': {'n': 'S8+WF', 'w': 165000, 'r': 223000},
    '242': {'n': 'CI6 / CI7N / CI8N / CAMON19 / CI8 / CI7 / CAMON19PRO', 'w': 80000, 'r': 108000},
    '243': {'n': 'A54 5G / A546 WF', 'w': 127000, 'r': 172000},
    '244': {'n': 'A315G / A315N / A315F', 'w': 77000, 'r': 104000},
    '245': {'n': 'A40 2020 / A405-WF', 'w': 116000, 'r': 157000},
    '246': {'n': 'NOTE10 4G-WF', 'w': 98000, 'r': 133000},
    '247': {'n': 'A30 / A50 / A50S-WF', 'w': 228000, 'r': 308000},
    '248': {'n': 'A3 / F7', 'w': 75000, 'r': 102000},
    '249': {'n': '13PRO', 'w': 128000, 'r': 173000},
    '250': {'n': 'RY Y72 / Y72S', 'w': 74000, 'r': 100000},
    '251': {'n': 'NOVA Y90', 'w': 83000, 'r': 113000},
    '252': {'n': 'ZERO304G / 5G', 'w': 104000, 'r': 141000},
    '253': {'n': '11-F(Q)', 'w': 166000, 'r': 225000},
    '254': {'n': 'Reno8 5G / Reno7 Se 5G / Find X5 Lite / realme 10 / F21 PRO / F21s PRO / Realme Narzo 60 5G / realme 9 4G / Reno8 T / Realme Narzo 50 Pro 5G / Reno8 / 11 / OPPO A78 / Reno7 A / Reno7 4', 'w': 72000, 'r': 98000},
    '255': {'n': 'HM 5', 'w': 75000, 'r': 102000},
    '256': {'n': 'MI 11 LITE 4G / 5G', 'w': 84000, 'r': 114000},
    '257': {'n': 'A2 LITE / 6PRO', 'w': 81000, 'r': 110000},
    '258': {'n': 'S22U（EU version）WF', 'w': 255000, 'r': 345000},
    '259': {'n': 'A1K / RealmeC2', 'w': 73000, 'r': 99000},
    '260': {'n': 'RY X5B', 'w': 79000, 'r': 107000},
    '261': {'n': 'HOT40 / SPARK20PRO / KJ6 / KJ7', 'w': 85000, 'r': 115000},
    '262': {'n': 'A11 2020 / A115', 'w': 74000, 'r': 100000},
    '263': {'n': 'X5+', 'w': 76000, 'r': 103000},
    '264': {'n': 'SPARK20PRO5G / NOTE40X5G', 'w': 83000, 'r': 113000},
    '265': {'n': 'S9WF', 'w': 169000, 'r': 229000},
    '266': {'n': 'A53WF', 'w': 113000, 'r': 153000},
    '267': {'n': 'PSMART Z', 'w': 81000, 'r': 110000},
    '268': {'n': 'Y03 / Y18 / Y37 / Y18E / Y18I / Y18S / Y28E 5G / Y03T / Y28S 5G / T3 LITE 5G', 'w': 71000, 'r': 96000},
    '269': {'n': 'SPARK8PRO', 'w': 86000, 'r': 117000},
    '270': {'n': 'NOTE10PRO 4G-WF', 'w': 105000, 'r': 142000},
    '271': {'n': 'Y58', 'w': 81000, 'r': 110000},
    '272': {'n': 'RY X9A / MAGIC 5LITE', 'w': 152000, 'r': 206000},
    '273': {'n': 'S8WF', 'w': 162000, 'r': 219000},
    '274': {'n': 'RY 90WF', 'w': 348000, 'r': 470000},
    '275': {'n': 'NOTE5 PLUS', 'w': 73000, 'r': 99000},
    '276': {'n': 'Spark7T', 'w': 73000, 'r': 99000},
    '277': {'n': 'Y35 5G', 'w': 78000, 'r': 106000},
    '278': {'n': '16PRO', 'w': 194000, 'r': 262000},
    '279': {'n': 'NOTE12Pro 4G-WF', 'w': 276000, 'r': 373000},
    '280': {'n': '14PROMAX-F(Q)', 'w': 828000, 'r': 1118000},
    '281': {'n': 'NOVA10PRO', 'w': 468000, 'r': 632000},
    '282': {'n': 'A04S / A047 / A136B', 'w': 72000, 'r': 98000},
    '283': {'n': 'NOTE5 PLUS', 'w': 73000, 'r': 99000},
    '284': {'n': 'POVA NEO 6', 'w': 78000, 'r': 106000},
    '285': {'n': 'X7D 5G', 'w': 82000, 'r': 111000},
    '286': {'n': 'A35 / A55', 'w': 91000, 'r': 123000},
    '287': {'n': 'NOTE13PRO 4G WF', 'w': 317000, 'r': 428000},
    '288': {'n': 'Mi Note10Pro / Note10Lite', 'w': 409000, 'r': 553000},
    '289': {'n': '9A / 9AT / 9C / 9i / 10A / POCO-C3', 'w': 66000, 'r': 90000},
    '290': {'n': 'Note 10 / Note 10s / POCO M5S', 'w': 82000, 'r': 111000},
    '291': {'n': 'RENO 5LITE WF', 'w': 100000, 'r': 135000},
    '292': {'n': 'A53 / A535-WF', 'w': 115000, 'r': 156000},
    '293': {'n': 'RY X6 / X6X / X8 5G / RY 70LITE / X8A 5G', 'w': 78000, 'r': 106000},
    '294': {'n': 'V27 5G', 'w': 163000, 'r': 221000},
    '295': {'n': 'S9+WF', 'w': 169000, 'r': 229000},
    '296': {'n': '12PROMAX-F-(Q)', 'w': 504000, 'r': 681000},
    '297': {'n': 'A01M 2020 / A015', 'w': 68000, 'r': 92000},
    '298': {'n': 'NOTE5 / NOTE 5 PRO', 'w': 73000, 'r': 99000},
    '299': {'n': 'XSMAX', 'w': 101000, 'r': 137000},
    '300': {'n': 'S24UWF', 'w': 242000, 'r': 327000},
    '301': {'n': 'XSMAX-F(Q)', 'w': 433000, 'r': 585000},
    '302': {'n': 'NOTE11 4G WF', 'w': 290000, 'r': 392000},
    '303': {'n': 'S6 / G1 / S7E / Y70 / Y73S', 'w': 79000, 'r': 107000},
    '304': {'n': 'MI NOTE10 LITE / CC9PRO', 'w': 120000, 'r': 162000},
    '305': {'n': 'Note14pro 5G / Note13proplus / PocoX7 / Note14pro plus', 'w': 153000, 'r': 207000},
    '306': {'n': 'realme C31', 'w': 78000, 'r': 106000},
    '307': {'n': '12 / 12PRO', 'w': 106000, 'r': 144000},
    '308': {'n': 'A24-4G / Galaxy A25 5G / Galaxy M34 5G / A26-Galaxy F34 5G', 'w': 82000, 'r': 111000},
    '309': {'n': 'NOVA10SE', 'w': 323000, 'r': 437000},
    '310': {'n': '13PROMAX-F(Q)', 'w': 639000, 'r': 863000},
    '311': {'n': 'RY 9XLITE(2020) / RY 8X', 'w': 78000, 'r': 106000},
    '312': {'n': 'S20+WF', 'w': 185000, 'r': 250000},
    '313': {'n': 'A20-WF', 'w': 228000, 'r': 308000},
    '314': {'n': 'A5PRO', 'w': 78000, 'r': 106000},
    '315': {'n': 'S20UWF', 'w': 202000, 'r': 273000},
    '316': {'n': 'A30S-WF', 'w': 228000, 'r': 308000},
    '317': {'n': 'NOTE11 PRO 4G / NOTE12 PRO 4G WF', 'w': 276000, 'r': 373000},
    '318': {'n': '16PROMAX', 'w': 224000, 'r': 303000},
    '319': {'n': 'NOTE12 4G-WF', 'w': 264000, 'r': 357000},
    '320': {'n': 'A12 / A02 / A125 / A127 2021 / A022 / A32 5G / M12 / M127 / M02', 'w': 67000, 'r': 91000},
    '321': {'n': 'NOTE11R / 10 5G / 11Prime 5G / POCO M4 5G / M5(INDIA) / NOTE11E', 'w': 75000, 'r': 102000},
    '322': {'n': 'X8A / X8 2023', 'w': 96000, 'r': 130000},
    '323': {'n': 'RY90', 'w': 84000, 'r': 114000},
    '324': {'n': 'A23 4G / A235 / M336', 'w': 72000, 'r': 98000},
    '325': {'n': '11PRO', 'w': 105000, 'r': 142000},
    '326': {'n': '7GW-F(Q)', 'w': 125000, 'r': 169000},
    '327': {'n': '7PW-F(Q)', 'w': 162000, 'r': 219000},
    '328': {'n': 'NOTE13 4G-WF', 'w': 272000, 'r': 368000},
    '329': {'n': 'NARZO 50A', 'w': 70000, 'r': 95000},
    '330': {'n': 'SPARK30PRO / HOT50PRO / S25 / S685LN', 'w': 89000, 'r': 121000},
    '331': {'n': 'A325 / A32 4G / A32LITE-WF', 'w': 248000, 'r': 335000},
    '332': {'n': 'S23U(EU version)WF', 'w': 259000, 'r': 350000},
    '333': {'n': '12PRO-F(Q）', 'w': 473000, 'r': 639000},
    '334': {'n': 'S10+-WF', 'w': 1128000, 'r': 1523000},
    '335': {'n': 'J5 2017 / J5Pro / J530', 'w': 72000, 'r': 98000},
    '336': {'n': 'HOT40(X6836) / SPARK20PRO(KJ6) / Spark10pro(KI7)', 'w': 81000, 'r': 110000},
    '337': {'n': '13MINI-FHD', 'w': 187000, 'r': 253000},
    '338': {'n': 'realme9Pro plus / Realme9 4g / Reno7 / Reno 8t / REALME10 4G', 'w': 84000, 'r': 114000},
    '339': {'n': '11PROMAX-F(Q)', 'w': 514000, 'r': 694000},
    '340': {'n': 'REALME C35 / Narzo 50A prime', 'w': 70000, 'r': 95000},
    '341': {'n': 'A57 5G / A58 5G / A77 5G / A78 5G / NORD N20 SE / NORD N300 5G / A17 / A38 / A18 / A56S 5G / A58X / A57 4G / A17K / A77 4G / A17s / ONE PlusN20se / A1 5G(Vitality Edition Phone) / A17K(A01) / A17K(A40) / A1X 5G / A2M / A2X', 'w': 74000, 'r': 100000},
    '342': {'n': 'BG6 / BG7 / BG7N / SMART8HD / SMART8 PRO / SMART8 PLUS / HOT40I / SPARK GO 2024 / POP8 / BG6H / BG6I / SPARK20 / KJ5 / KJ5N / SPARK20C / A666L / A666LN / A70S / RS4 / S24', 'w': 71000, 'r': 96000},
    '343': {'n': 'S6 5G', 'w': 84000, 'r': 114000},
    '344': {'n': '15PROMAX-F(Q-X)', 'w': 908000, 'r': 1226000},
    '345': {'n': 'Y58', 'w': 77000, 'r': 104000},
    '346': {'n': 'NOTE11S-WF', 'w': 99000, 'r': 134000},
    '347': {'n': '7PB-F(Q)', 'w': 162000, 'r': 219000},
    '348': {'n': 's18e / 30lite 5G / 30lite 4G / T3 5G / Y100 4G / Y100 5 G / Y200E 5G / iqooz9 5G / Y300 5G / Y400 5G / iqoo Z10 lite 4G / Y200 5G', 'w': 224000, 'r': 303000},
    '349': {'n': 'A15 / A155 / A156 / M15 / M156 5G', 'w': 305000, 'r': 412000},
    '350': {'n': 'RY Y72 / Y72S', 'w': 79000, 'r': 107000},
    '351': {'n': 'NOTE11 4G-WF', 'w': 95000, 'r': 129000},
    '352': {'n': 'X7D 5G WF', 'w': 137000, 'r': 185000},
    '353': {'n': 'S21WF', 'w': 184000, 'r': 249000},
    '354': {'n': 'A165 4G / A166 5G / M16 5G / F16 5G / A266 / A26 5G / A175 4G / A176 5G / M176 / F176', 'w': 309000, 'r': 418000},
    '355': {'n': 'A175 4G / A176 5G / M176 / F176 WF', 'w': 334000, 'r': 451000},
    '356': {'n': '16PRO-F(Q)', 'w': 744000, 'r': 1005000},
    '357': {'n': '15PRO-F(Q)', 'w': 1141000, 'r': 1541000},
    '358': {'n': 'Y7P / Y7P 2020', 'w': 76000, 'r': 103000},
    '359': {'n': 'Y35 5G', 'w': 76000, 'r': 103000},
    '360': {'n': 'A40 / A60 / A80 / A3PRO', 'w': 78000, 'r': 106000},
    '361': {'n': 'A3PRO', 'w': 78000, 'r': 106000},
    '362': {'n': 'RY X5B', 'w': 77000, 'r': 104000},
    '363': {'n': 'NOTE10PRO 4G / NOTE10MAX / NOTE11PRO 4G / 5G / NOTE13 4G / POCO X4PRO / NOTE10PRO+ / NOTE11PRO+ / NOTE11E PRO / NOTE14 4G / M7PRO / NOTE12PRO 4G', 'w': 80000, 'r': 108000},
    '364': {'n': 'XSMAX-FHD', 'w': 173000, 'r': 234000},
    '365': {'n': 'A356 / A556 / A55 5G / M35 WF', 'w': 144000, 'r': 195000},
    '366': {'n': 'MI 12PRO / MI12S PRO', 'w': 162000, 'r': 219000},
    '367': {'n': 'X9CWF', 'w': 221000, 'r': 299000},
    '368': {'n': 'J2Core / J260', 'w': 64000, 'r': 87000},
    '369': {'n': 'A32 4G / A325 / A32 LITE WF', 'w': 94000, 'r': 127000},
    '370': {'n': 'F3 / F4 / MI11I', 'w': 279000, 'r': 377000},
    '371': {'n': 'RENO 8T 5G', 'w': 290000, 'r': 392000},
    '372': {'n': 'S23ultra / S918-WF', 'w': 654000, 'r': 883000},
    '373': {'n': 'A21S 2020 / A217', 'w': 67000, 'r': 91000},
    '374': {'n': 'A03CORE / A032', 'w': 67000, 'r': 91000},
    '375': {'n': 'HOT60I', 'w': 78000, 'r': 106000},
    '376': {'n': 'SPARK20PRO5G / NOTE40X5G', 'w': 84000, 'r': 114000},
    '377': {'n': 'S9e-V2048A / S15e-V2190A / VIVO T1 5G -V2150 / VIVO T1 Pro 5G-V2151', 'w': 85000, 'r': 115000},
    '378': {'n': '8PB-F(Q)', 'w': 166000, 'r': 225000},
    '379': {'n': 'X8 WF', 'w': 133000, 'r': 180000},
    '380': {'n': '12 / 12PRO-FHD', 'w': 173000, 'r': 234000},
    '381': {'n': 'Y300', 'w': 204000, 'r': 276000},
    '382': {'n': 'S22+WF', 'w': 211000, 'r': 285000},
    '383': {'n': '11PRO-F(Q)', 'w': 473000, 'r': 639000},
    '384': {'n': 'POCO F3 WF', 'w': 323000, 'r': 437000},
    '385': {'n': 'C21Y/C25Y', 'w': 71000, 'r': 96000},
    '386': {'n': 'NOTE 5 / NOTE 5 PRO', 'w': 71000, 'r': 96000},
    '387': {'n': 'Y100 / Y100-5G / Y200 / S18E / Y300 5G / Y200 5G / 5G', 'w': 87000, 'r': 118000},
    '388': {'n': '8GW-F(Q)', 'w': 130000, 'r': 176000},
    '389': {'n': 'N61 / N63 / Realme note60', 'w': 75000, 'r': 102000},
    '390': {'n': 'X8A / X8 2023', 'w': 77000, 'r': 104000},
    '391': {'n': 'A56WF', 'w': 154000, 'r': 208000},
    '392': {'n': 'RY 50', 'w': 162000, 'r': 219000},
    '393': {'n': 'S23WF', 'w': 215000, 'r': 291000},
    '394': {'n': '13PROMAX-FHD', 'w': 228000, 'r': 308000},
    '395': {'n': 'S23+WF', 'w': 289000, 'r': 391000},
    '396': {'n': 'NOTE10PRO 4G WF', 'w': 104000, 'r': 141000},
    '397': {'n': 'A59 / F1S', 'w': 67000, 'r': 91000},
    '398': {'n': 'A16 4G / A17 / A17 5G / A16 5G / M16 / F16', 'w': 78000, 'r': 106000},
    '399': {'n': 'A515 / A516 / M31S-WF', 'w': 93000, 'r': 126000},
    '400': {'n': '8GB-F(Q)', 'w': 130000, 'r': 176000},
    '401': {'n': 'REALMEC53 / NOTE50', 'w': 75000, 'r': 102000},
    '402': {'n': '8PW-F-(Q)', 'w': 166000, 'r': 225000},
    '403': {'n': 'X7D 4G WF', 'w': 137000, 'r': 185000},
    '404': {'n': 'A245 / A246 / A255 / A256 / M346', 'w': 84000, 'r': 114000},
    '405': {'n': 'X6B', 'w': 75000, 'r': 102000},
    '406': {'n': 'Magic7 Lite / X9C', 'w': 187000, 'r': 253000},
    '407': {'n': 'Y100 4G', 'w': 242000, 'r': 327000},
    '408': {'n': 'S24WF', 'w': 361000, 'r': 488000},
    '409': {'n': 'X9BWF', 'w': 376000, 'r': 508000},
    '410': {'n': 'RY X6 / X6S / X8 5G / 70LITE / X8A 5G', 'w': 70000, 'r': 95000},
    '411': {'n': 'Y56 5G / Y35 4G / Y33S 4GOverseas version', 'w': 70000, 'r': 95000},
    '412': {'n': 'PSMART Z', 'w': 71000, 'r': 96000},
    '413': {'n': 'CW40 / RY X6A / CW40C / X5 Plus / X5B / X5B Plus', 'w': 72000, 'r': 98000},
    '414': {'n': 'A24 4G-WF', 'w': 96000, 'r': 130000},
    '415': {'n': 'MI 13T / MI13TPRO', 'w': 125000, 'r': 169000},
    '416': {'n': 'Note 14 5G / Note 14 / Note 13 / POCO M7 PRO 5G', 'w': 80000, 'r': 108000},
    '417': {'n': 'A725-WF', 'w': 126000, 'r': 171000},
    '418': {'n': '12MINI-FHD', 'w': 187000, 'r': 253000},
    '419': {'n': 'BF7 / BF6 / A60 / A60S / POP7 / KI5K / SPARKGO2023 / SMART10HD / KI5Q / SPARK10(KI5) / SPARK10C / KI8 / KI5N / VISION3 / SMART7 / S23 / POP7PRO / SMARK7HD / A662L / NOTE20 / NOTE12VIP / HOT30I', 'w': 70000, 'r': 95000},
    '420': {'n': 'S6 / G1 / S7E / Y70 / Y73S', 'w': 75000, 'r': 102000},
    '421': {'n': 'SPARK5AIR / LC7 / LC7S / LC8 / SPARK6AIR / POUVOIR4 / POUVOIR4PRO / SPARKPOWER2', 'w': 76000, 'r': 103000},
    '422': {'n': 'RY X5B', 'w': 78000, 'r': 106000},
    '423': {'n': 'A325N / A325M / A325F / M325FV / M325F', 'w': 79000, 'r': 107000},
    '424': {'n': 'NOVA12I', 'w': 84000, 'r': 114000},
    '425': {'n': '13', 'w': 108000, 'r': 146000},
    '426': {'n': '11-FHD', 'w': 149000, 'r': 202000},
    '427': {'n': 'NOVA 5I / NOVA 7I', 'w': 115000, 'r': 156000},
    '428': {'n': 'X7B WF', 'w': 117000, 'r': 158000},
    '429': {'n': 'RY 70', 'w': 158000, 'r': 214000},
    '430': {'n': 'NOVA12 SE', 'w': 160000, 'r': 216000},
    '431': {'n': 'S21+WF', 'w': 184000, 'r': 249000},
    '432': {'n': 'S22WF', 'w': 236000, 'r': 319000},
    '433': {'n': 'V29E', 'w': 242000, 'r': 327000},
    '434': {'n': 'NOVA12 SE', 'w': 335000, 'r': 453000},
    '435': {'n': 'NOVA10PRO', 'w': 475000, 'r': 642000},
    '436': {'n': 'S24U-WF', 'w': 736000, 'r': 994000},
    '437': {'n': 'J6 2018 / J600', 'w': 69000, 'r': 94000},
    '438': {'n': 'A77S', 'w': 70000, 'r': 95000},
    '439': {'n': 'RY X5', 'w': 75000, 'r': 102000},
    '440': {'n': 'NOTE10(X693) / NOTE 11I / NOTE 11S(X698) / NOTE 11Pro(X697) / POVA 2(LE7 / LE7n) / POVA3(LF7) / POVA 5G(LE8)', 'w': 91000, 'r': 123000},
    '441': {'n': '15', 'w': 131000, 'r': 177000},
    '442': {'n': 'A33WF', 'w': 113000, 'r': 153000},
    '443': {'n': 'NOTE12 4G / NOTE 12 5G / POCO X5 4G / POCO X5 5G', 'w': 80000, 'r': 108000},
    '444': {'n': 'RENO 8T 5G', 'w': 135000, 'r': 183000},
    '445': {'n': 'A30S-WF', 'w': 86000, 'r': 117000},
    '446': {'n': 'Magic6 Lite 5G / X9B', 'w': 189000, 'r': 256000},
    '447': {'n': '12PROMAX-FHD', 'w': 248000, 'r': 335000},
    '448': {'n': 'A35 / M35WF', 'w': 273000, 'r': 369000},
    '449': {'n': 'A525 / A526 / A528 / A52S-WF', 'w': 283000, 'r': 383000},
    '450': {'n': 'GT MASTER', 'w': 358000, 'r': 484000},
    '451': {'n': 'S22ultra / S908-WF', 'w': 654000, 'r': 883000},
    '452': {'n': 'A32 4G / A33 / A53 4G / A53S / A54 4G / A55 4G / REALME7I / REALMEC17 / 1+N100', 'w': 71000, 'r': 96000},
    '453': {'n': 'NOTE13 4G-WF', 'w': 129000, 'r': 175000},
    '454': {'n': 'A70 2019 / A705-WF', 'w': 94000, 'r': 127000},
    '455': {'n': 'NOTE14 4G', 'w': 79000, 'r': 107000},
    '456': {'n': 'RY X7C', 'w': 81000, 'r': 110000},
}


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
        "last_order": "/tmp/last_order.json", "meta": "/tmp/meta.json"}

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

def get_user(uid):
    u = store_get("users", uid)
    return u if isinstance(u, dict) else {}

# ---- Buyurtmalar: har biri alohida ID bilan saqlanadi (tarix yo'qolmaydi) ----
STATUSES = {
    "yangi": "Yangi",
    "chek": "Chek keldi",
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
        InlineKeyboardButton("💵 Naqd kelishildi", callback_data=f"pay:{cid}:cash"),
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
    try:
        user = get_user(cid)
        phone = user.get('phone')
        role = user.get('role') or "—"

        name = str(data.get('n', 'Mijoz'))[:30].strip() or 'Mijoz'
        deliv = data.get('d') if data.get('d') in ALLOWED_DELIVERY else 'BTS'
        addr = str(data.get('a', ''))[:80].strip()
        tg_name = " ".join(x for x in [m.from_user.first_name, m.from_user.last_name] if x)

        # 1) Tovarlarni tekshirish: faqat katalogdagi ID lar, musbat butun son
        clean = {}
        for it in data.get('i', []) or []:
            try:
                item_id, q = str(int(it[0])), int(it[1])
            except (ValueError, TypeError, IndexError):
                continue
            if item_id in CATALOG and q > 0:
                clean[item_id] = min(MAX_QTY_PER_ITEM, clean.get(item_id, 0) + q)
        if not clean:
            bot.send_message(m.chat.id, "⚠️ Savatingiz bo'sh yoki noto'g'ri. Do'konni qayta ochib ko'ring.")
            return

        # 2) Narx va rejimni SERVER hisoblaydi (mijoz yuborgan summaga ishonilmaydi)
        t_qty = sum(clean.values())
        is_wholesale = t_qty >= WHOLESALE_MIN
        pt = "Optom" if is_wholesale else "Chakana"

        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerow(["№", "Model nomi", "Soni", "Narxi (UZS)", "Umumiy summa (UZS)"])
        payload_items, items_txt, t_sum = [], "", 0
        for idx, (item_id, q) in enumerate(clean.items(), 1):
            cat = CATALOG[item_id]
            price = cat['w'] if is_wholesale else cat['r']
            subtotal = q * price
            t_sum += subtotal
            writer.writerow([idx, cat['n'], q, price, subtotal])
            payload_items.append({"id": item_id, "n": cat['n'], "oq": q, "aq": q, "p": price})
            if idx <= 15:
                items_txt += f"• <b>{h(cat['n'][:30])}</b>: {q} dona\n"
            elif idx == 16:
                items_txt += f"<i>... va yana (jami {len(clean)} xil model)</i>\n"
        writer.writerow([])
        writer.writerow(["", "JAMI", t_qty, "", t_sum])

        oid = next_order_id()
        save_order(cid, {"id": oid, "cid": cid, "created": now_ms(), "status": "yangi",
                         "history": [{"t": now_ms(), "s": "yangi", "by": "mijoz"}],
                         "name": name, "tg_name": tg_name, "username": m.from_user.username, "phone": phone,
                         "role": user.get('role'), "deliv": deliv, "addr": addr, "pt": pt,
                         "qty": t_qty, "total": t_sum, "items": payload_items, "note": ""})

        csv_file = io.BytesIO(csv_buffer.getvalue().encode('utf-8-sig'))
        csv_file.name = f"Buyurtma_{oid}.csv"

        client_txt = (
            f"🛒 <b>Buyurtmangiz #{oid} qabul qilindi!</b>\n━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>Mijoz:</b> {h(name)}\n📞 <b>Telefon:</b> {h(phone or 'yuborilmagan')}\n"
            f"🚚 <b>Yetkazish:</b> {h(deliv)} | 📍 {h(addr)}\n"
            f"📦 <b>Tarkibi:</b>\n{items_txt}━━━━━━━━━━━━━━━━━━━\n"
            f"💰 <b>JAMI TO'LOV:</b> <b>{t_sum:,} so'm</b> ({pt} narxda, {t_qty} dona)\n\n"
            f"💳 Karta raqami: <code>{h(CARD_NUMBER)}</code>\nQabul qiluvchi: <b>{h(CARD_NAME)}</b>\n\n"
            f"📸 To'lov qilgach, chek rasmini shu chatga yuboring.\n\n{WARRANTY_TEXT}"
        )
        safe_send(cid, client_txt, parse_mode="HTML")

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
                f"💰 <b>Jami summa:</b> <b>{t_sum:,} so'm</b>{h(mismatch)}\n━━━━━━━━━━━━━━━━━━━\n"
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
    if p.get("id"):
        p["total"], p["qty"] = n_sum, n_qty
        p.setdefault("history", []).append({"t": now_ms(), "s": p.get("status", "yangi"), "by": "admin",
                                            "note": f"Tarkib o'zgardi: {n_qty} ta, {n_sum:,} so'm"})
        save_order(p["cid"], p)
    msg = (f"⚠️ <b>DIQQAT: AYRIM MODELLAR OMBORDA KAM YOKI YO'Q!</b>\n━━━━━━━━━━━━━━━━━━━\n"
           f"{miss_t}{part_t}━━━━━━━━━━━━━━━━━━━\n"
           f"📦 <b>Bor tovarlar:</b>\n{av_t or 'Qolmadi'}\n━━━━━━━━━━━━━━━━━━━\n"
           f"💰 <b>Qayta hisoblangan to'lov:</b> <b>{n_sum:,} so'm</b> ({n_qty} ta)\n"
           f"💳 Karta: <code>{h(CARD_NUMBER)}</code> ({h(CARD_NAME)})\n\n{WARRANTY_TEXT}")
    kb = InlineKeyboardMarkup().add(InlineKeyboardButton("💬 Admin bilan bog'lanish", url=f"tg://user?id={ADMIN_ID}"))
    safe_send(order_cid(cid, p), msg, reply_markup=kb, parse_mode="HTML")
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
           InlineKeyboardButton("❌ Soxta chek", callback_data=f"pay:{cid}:fake"))
    try:
        bot.send_photo(ADMIN_ID, m.photo[-1].file_id,
                       caption=f"🧾 <b>TO'LOV CHEKI KELDI!</b> {('#' + h(get_payload(cid).get('id', ''))) if get_payload(cid) else ''}\n{contact_line(cid, m.from_user.first_name, m.from_user.username, phone)}",
                       reply_markup=kb, parse_mode="HTML")
        set_status(get_payload(cid), "chek", by="mijoz")
        bot.reply_to(m, "✅ Chekingiz qabul qilindi! Admin tekshirib, tez orada javob beradi.")
    except Exception:
        log.exception("receipt forward")
        bot.reply_to(m, "⚠️ Chekni yuborib bo'lmadi, birozdan keyin qayta yuboring.")


PAY_TEXTS = {
    "today": "🎉 Tasdiqlandi! BUGUN yetkaziladi.",
    "tomorrow": "🎉 Tasdiqlandi! ERTAGA yetkaziladi.",
    "cash": "🤝 Tasdiqlandi! To'lov naqd olinadi.",
    "fake": "⚠️ To'lov tushmadi. Chekni tekshirib, qayta yuboring.",
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
