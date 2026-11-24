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
import json, os, io, csv, hmac, hashlib, time, logging, re, secrets, types, requests

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("ekranchi")

PUBLIC_URL_DEFAULT = "https://ekranchi-shop.vercel.app"
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0") or 0)
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")
WEB_APP_URL = os.environ.get("WEB_APP_URL", PUBLIC_URL_DEFAULT + "/market.html?v=wow_v8")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "").lstrip("@").strip()
PAYMENT_TEXT = "💬 <b>To'lov masalasida admin siz bilan o'zi bog'lanadi.</b> Savollar bo'lsa, pastdagi tugma orqali adminga yozing."

PUBLIC_URL = os.environ.get("PUBLIC_URL", PUBLIC_URL_DEFAULT).rstrip("/")

WHOLESALE_MIN = 50          # shuncha va undan ko'p dona bo'lsa optom narx
MAX_QTY_PER_ITEM = 9999
ALLOWED_DELIVERY = {"BTS", "Taksi"}

# Vercel Marketplace Upstash integratsiyasi KV_REST_API_* nomlarini qo'shadi
REDIS_URL = (os.environ.get("UPSTASH_REDIS_REST_URL") or os.environ.get("KV_REST_API_URL") or "").rstrip("/")
REDIS_TOKEN = os.environ.get("UPSTASH_REDIS_REST_TOKEN") or os.environ.get("KV_REST_API_TOKEN") or ""

# Boshlang'ich katalog: baza bo'sh bo'lsa yoki CATALOG_VERSION o'zgarsa yoziladi. Keyin narx va qoldiq admin paneldan boshqariladi.
# Manba: PRICE 21.10.2026; qoldig'i 0 bo'lganlar yo'q.
# ID lar 1001 dan boshlanadi, eski buyurtmalardagi ID lar (1-456) yangi mahsulotlarga tushib qolmasin.
CATALOG_VERSION = "2026-10-21"
# Faqat narxlar yangilanganda: qoldiq, yashirilgan mahsulotlar va nomlar bazada qoladi, optom va chakana SEED_CATALOG dan olinadi.
# 26.10 (2): mijozlar uchun PDF bilan bir xil. 21.10 gacha bo'lgan eski do'kon narxi, keyin qo'shilgan 174 ta modelga Bekzod yozgan narx; chakana = optom x 1,35.
PRICE_VERSION = "2026-10-26b"
def _load_seed():
    """Boshlang'ich katalog bitta faylda turadi: catalog.seed.json (do'kon sahifasi ham zaxira sifatida shuni o'qiydi)."""
    here = os.path.dirname(os.path.abspath(__file__))
    for path in (os.path.join(here, "..", "catalog.seed.json"), os.path.join(os.getcwd(), "catalog.seed.json")):
        try:
            with open(path, encoding="utf-8") as f:
                return [{**p, "id": str(p["id"])} for p in json.load(f)]
        except FileNotFoundError:
            continue
        except Exception:
            log.exception("catalog.seed.json o'qilmadi: %s", path)
    log.error("catalog.seed.json topilmadi: katalog faqat bazadan olinadi")
    return []

SEED_CATALOG = _load_seed()


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
        "catalog": "/tmp/catalog.json", "stock": "/tmp/stock.json", "watch": "/tmp/watch.json",
        "applogin": "/tmp/applogin.json"}

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
PRODUCT_FIELDS = ("brand", "type", "name", "retail", "wholesale", "active", "img")
IMG_RE = re.compile(r"^https://[^\s\"'<>]{4,490}$")

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
    if not SEED_CATALOG:  # seed o'qilmagan bo'lsa, bazadagi katalogni o'chirib yubormaymiz
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
        # seed ga keyin qo'shilgan mahsulotlar (masalan 24.11 Samsung Change Glass, ID 2001-2024) bazaga qo'shiladi;
        # bazadagi narx, qoldiq va yashirilganlar o'zgarmaydi
        new = [p for p in SEED_CATALOG if p["id"] not in cat]
        if new:
            log.info("Yangi mahsulotlar qo'shilmoqda: %d ta", len(new))
            _set_many("catalog", {p["id"]: {k: p[k] for k in ("brand", "type", "name", "retail", "wholesale")} | {"active": True}
                                  for p in new})
            _set_many("stock", {p["id"]: int(p.get("stock") or 0) for p in new})
            cat = store_all("catalog")
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

def rereserve_order_stock(p):
    """Bekor qilingan buyurtma qayta tiklanganda tovarlarni ombordan yana band qiladi.
    Omborda yetmasa, bor qismi olinadi va mavjud son (aq) shunga tushiriladi. Yetmagan modellar ro'yxatini qaytaradi."""
    if not p or not p.get("stock_reserved") or not p.get("stock_returned"):
        return []
    short = []
    for it in p.get("items", []):
        want = int(it.get("rq", it.get("aq", 0)) or 0)
        got = reserve_stock(it["id"], want) if want > 0 else 0
        it["rq"] = got
        if got < int(it.get("aq", 0) or 0):
            it["aq"] = got
        if got < want:
            short.append(f"{it.get('n', it['id'])}: {want} o'rniga {got} ta")
    p["stock_returned"] = False
    p["total"], p["qty"] = order_summary(p)
    return short

def set_status(p, status, note=None, by="bot"):
    if not p or not p.get("id") or status not in STATUSES:
        return p
    if p.get("status") != status or note:
        if status == "bekor":
            release_order_stock(p, by)
        elif p.get("status") == "bekor":
            short = rereserve_order_stock(p)
            if short:
                note = ((note + " | ") if note else "") + "Omborda yetmadi: " + "; ".join(short)[:300]
                notify_admin(f"⚠️ <b>#{h(p['id'])} qayta tiklandi, lekin omborda yetmadi:</b>\n" + "\n".join(h(x) for x in short[:15]))
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
    payload = (m.text or "").split(maxsplit=1)[1].strip() if len((m.text or "").split(maxsplit=1)) > 1 else ""
    if payload.startswith("app_"):
        return ask_app_login(m, payload[4:])
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
    return process_order(m)


def process_order(m, src="bot"):
    """Buyurtmani qabul qiladi. Saqlangan buyurtmani qaytaradi; qabul qilinmasa None (sababi mijozga Telegramda yoziladi)."""
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
        geo = None   # ilovadan biriktirilgan joylashuv: [kenglik, uzunlik]
        try:
            g = data.get('g')
            if isinstance(g, (list, tuple)) and len(g) == 2 and -90 <= float(g[0]) <= 90 and -180 <= float(g[1]) <= 180:
                geo = [round(float(g[0]), 6), round(float(g[1]), 6)]
        except (TypeError, ValueError):
            geo = None

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
        order = {"id": oid, "cid": cid, "created": now_ms(), "status": "yangi",
                 "history": [{"t": now_ms(), "s": "yangi", "by": "mijoz"}],
                 "name": name, "tg_name": tg_name, "username": m.from_user.username, "phone": phone,
                 "role": user.get('role'), "deliv": deliv, "addr": addr, "pt": pt,
                 "qty": t_qty, "total": t_sum, "items": payload_items, "note": "",
                 "stock_reserved": True, "src": src}
        if geo:
            order["geo"] = geo
        save_order(cid, order)

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
                f"🔔 <b>YANGI BUYURTMA #{oid}</b>{' 📱 ilovadan' if src == 'app' else ''}\n━━━━━━━━━━━━━━━━━━━\n"
                f"✍️ <b>Ism (formada):</b> {h(name)} ({h(role)})\n"
                f"{contact_line(cid, tg_name or name, m.from_user.username, phone)}\n"
                f"🚚 <b>Yetkazish:</b> {h(deliv)} | 📍 {h(addr)}\n"
                + (f"🗺 <a href=\"https://maps.google.com/?q={geo[0]},{geo[1]}\">Xaritada ko'rish</a>\n" if geo else "") +
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
        return order
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
    if p.get('status') == 'bekor':
        return bot.answer_callback_query(c.id, "Buyurtma bekor qilingan, tarkibini o'zgartirib bo'lmaydi.", show_alert=True)
    item = p['items'][idx]
    oq, cur = item.get('oq', 1), item.get('aq', 1)
    new = max(0, min(oq, cur + val)) if action == 'st' else max(0, min(oq, val))
    # "Mijozga yuborish"dan keyin kamaytirilgan qism omborga qaytgan bo'ladi: ko'paytirilsa, yana band qilamiz
    held = int(item.get('rq', oq) or 0)
    if p.get('stock_reserved') and not p.get('stock_returned') and new > held:
        got = reserve_stock(item['id'], new - held)
        item['rq'] = held + got
        if got < new - held:
            new = held + got
            bot.answer_callback_query(c.id, f"Omborda faqat {got} ta qo'shimcha bor edi", show_alert=True)
            item['aq'] = new; save_order(cid, p)
            return show_edit_item_screen(c.message.chat.id, c.message.message_id, p, idx, cid)
    item['aq'] = new
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
    if not ADMIN_ID:
        return
    phone = get_user(cid).get('phone')
    order = get_payload(cid)
    if not order:
        bot.reply_to(m, "ℹ️ Sizda faol buyurtma yo'q. Avval «🛍 Do'konni ochish» orqali buyurtma bering.",
                     reply_markup=main_kb())
        return
    kb = InlineKeyboardMarkup(row_width=2)
    key = order.get("id") or cid  # aniq buyurtma ID si: mijoz yangi buyurtma bersa ham tugma eskisiga tegadi
    kb.add(InlineKeyboardButton("✅ Bugun yetkazish", callback_data=f"pay:{key}:today"),
           InlineKeyboardButton("✅ Ertaga yetkazish", callback_data=f"pay:{key}:tomorrow"),
           InlineKeyboardButton("❌ To'lov tushmadi", callback_data=f"pay:{key}:fake"))
    try:
        bot.send_photo(ADMIN_ID, m.photo[-1].file_id,
                       caption=f"📷 <b>MIJOZDAN RASM KELDI</b> #{h(order.get('id', ''))}\n{contact_line(cid, m.from_user.first_name, m.from_user.username, phone)}",
                       reply_markup=kb, parse_mode="HTML")
        if order.get("status") in ("yangi", "chek"):
            set_status(order, "chek", by="mijoz")
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
    resp = jsonify({"products": [{k: p.get(k) for k in ("id", "brand", "type", "name", "retail", "wholesale", "stock", "img") if k != "img" or p.get("img")} for p in items],
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
            if "img" in ch:
                img = str(ch["img"] or "").strip()
                if img and not IMG_RE.match(img):
                    errors.append(f"{base.get('name') or pid}: rasm havolasi https:// bilan boshlanishi kerak"); continue
                base["img"] = img
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


# ===================== ILOVA (APK): Telegram orqali kirish, buyurtma va tarix =====================
APP_LOGIN_TTL = 600            # kirish kodi 10 daqiqa amal qiladi
APP_TOKEN_DAYS = 180
_bot_username = os.environ.get("BOT_USERNAME", "").lstrip("@").strip()

def bot_username():
    global _bot_username
    if not _bot_username:
        _bot_username = bot.get_me().username or ""
    return _bot_username

def make_app_token(cid, days=APP_TOKEN_DAYS):
    exp = int(time.time()) + days * 86400
    sig = hmac.new(_panel_key(), f"app:{cid}:{exp}".encode(), hashlib.sha256).hexdigest()[:40]
    return f"{cid}.{exp}.{sig}"

def check_app_token(tok):
    """To'g'ri bo'lsa mijozning chat ID sini, aks holda None qaytaradi."""
    try:
        cid, exp, sig = str(tok).split(".")
        good = hmac.new(_panel_key(), f"app:{int(cid)}:{int(exp)}".encode(), hashlib.sha256).hexdigest()[:40]
        return cid if int(exp) > time.time() and hmac.compare_digest(sig, good) else None
    except Exception:
        return None

def _sha(v):
    return hashlib.sha256(str(v).encode()).hexdigest()

def _login_get(code):
    rec = store_get("applogin", code) if re.fullmatch(r"[A-Za-z0-9_-]{8,32}", str(code or "")) else None
    if not isinstance(rec, dict) or now_ms() - int(rec.get("t", 0)) > APP_LOGIN_TTL * 1000:
        return None
    return rec

def _login_del(code):
    try:
        if REDIS_URL:
            _redis("HDEL", "applogin", str(code))
        else:
            data = _file_load("applogin"); data.pop(str(code), None); _file_save("applogin", data)
    except Exception:
        log.exception("applogin del")

def ask_app_login(m, code):
    """Ilovadagi «Telegram orqali kirish» tugmasidan kelgan mijoz: kirishni o'zi tasdiqlashi kerak."""
    if not _login_get(code):
        bot.send_message(m.chat.id, "⚠️ Kirish havolasi eskirgan. Ilovada «Telegram orqali kirish» tugmasini qayta bosing.")
        return
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("✅ Ha, ilovaga kiraman", callback_data=f"applogin:{code}"))
    bot.send_message(m.chat.id,
        "📱 <b>Ekranchi_Bola ilovasiga kirish</b>\n\n"
        "Ilovada kirish tugmasini <b>o'zingiz</b> bosgan bo'lsangiz, pastdagi tugma bilan tasdiqlang.\n\n"
        "⚠️ Bu havolani sizga boshqa birov yuborgan bo'lsa, <b>bosmang</b>: u sizning nomingizdan buyurtma bera oladi.",
        reply_markup=kb, parse_mode="HTML")

@bot.callback_query_handler(func=lambda c: c.data.startswith('applogin:'))
def handle_app_login(c):
    code = c.data.split(':', 1)[1]
    rec = _login_get(code)
    try: bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=None)
    except Exception: pass
    if not rec or rec.get("cid"):
        bot.answer_callback_query(c.id, "Havola eskirgan. Ilovada qayta urinib ko'ring.", show_alert=True)
        return
    rec["cid"] = str(c.from_user.id)
    store_set("applogin", code, rec)
    user = get_user(c.from_user.id)
    user.update({"name": c.from_user.first_name, "username": c.from_user.username})
    store_set("users", c.from_user.id, user)
    bot.answer_callback_query(c.id, "Tasdiqlandi")
    bot.send_message(c.message.chat.id, "✅ Tasdiqlandi. Endi <b>Ekranchi_Bola</b> ilovasiga qayting.", parse_mode="HTML")
    if not user.get("phone"):
        bot.send_message(c.message.chat.id, "📞 Buyurtmalaringiz bo'yicha bog'lanishimiz uchun telefon raqamingizni yuboring 👇",
                         reply_markup=contact_kb())

def _app_user(cid):
    u = get_user(cid)
    return {"name": u.get("name") or "", "phone": u.get("phone") or "", "role": u.get("role") or ""}

def _app_order(o):
    return {"id": o.get("id"), "created": o.get("created"), "status": o.get("status"),
            "status_label": STATUSES.get(o.get("status"), o.get("status")),
            "total": sum(int(i.get("p", 0)) * int(i.get("rq", i.get("aq", 0)) or 0) for i in o.get("items", [])) or o.get("total", 0),
            "pt": o.get("pt"), "deliv": o.get("deliv"), "addr": o.get("addr"), "geo": o.get("geo"),
            "items": [{"id": i.get("id"), "n": i.get("n"), "q": int(i.get("rq", i.get("aq", 0)) or 0),
                       "asked": i.get("asked"), "p": i.get("p")} for i in o.get("items", [])]}

def app_api():
    action = request.args.get("app")
    if action == "login_start" and request.method == "POST":
        try:
            name = bot_username()
        except Exception:
            log.exception("bot_username")
            name = ""
        if not name:
            return jsonify({"error": "Bot bilan aloqa yo'q. Birozdan keyin urinib ko'ring."}), 503
        pending = store_all("applogin")
        if len(pending) > 2000:   # eskirgan kodlarni tozalash
            for k, v in pending.items():
                if not isinstance(v, dict) or now_ms() - int(v.get("t", 0)) > APP_LOGIN_TTL * 1000:
                    _login_del(k)
        code, poll = secrets.token_urlsafe(9), secrets.token_urlsafe(24)
        store_set("applogin", code, {"t": now_ms(), "poll": _sha(poll), "cid": None})
        return jsonify({"code": code, "poll": poll, "url": f"https://t.me/{name}?start=app_{code}", "expires": APP_LOGIN_TTL})
    if action == "login_check" and request.method == "POST":
        body = request.get_json(silent=True) or {}
        code = str(body.get("code", ""))
        rec = _login_get(code)
        if not rec or not hmac.compare_digest(rec.get("poll", ""), _sha(body.get("poll", ""))):
            return jsonify({"error": "Kirish muddati tugadi. Qayta urinib ko'ring."}), 410
        if not rec.get("cid"):
            return jsonify({"pending": True})
        _login_del(code)
        return jsonify({"token": make_app_token(rec["cid"]), "user": _app_user(rec["cid"])})

    cid = check_app_token(request.headers.get("X-App-Token", ""))
    if not cid:
        return jsonify({"error": "Qaytadan kiring."}), 401
    if action == "me" and request.method == "GET":
        orders = [o for o in store_all("orders2").values() if isinstance(o, dict) and str(o.get("cid")) == cid]
        orders.sort(key=lambda o: o.get("created", 0), reverse=True)
        return jsonify({"user": _app_user(cid), "orders": [_app_order(o) for o in orders[:30]]})
    if action == "order" and request.method == "POST":
        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            return jsonify({"error": "Buyurtmani o'qib bo'lmadi."}), 400
        u = get_user(cid)
        fake = types.SimpleNamespace(
            chat=types.SimpleNamespace(id=int(cid)),
            from_user=types.SimpleNamespace(id=int(cid), first_name=u.get("name"), last_name=None, username=u.get("username")),
            web_app_data=types.SimpleNamespace(data=json.dumps(body)))
        order = process_order(fake, src="app")
        if not order:
            return jsonify({"error": "Buyurtma qabul qilinmadi: tanlangan tovarlar omborda qolmagan bo'lishi mumkin. Katalogni yangilab, qayta urinib ko'ring."}), 409
        return jsonify({"ok": True, "order": _app_order(order), "need_phone": not order.get("phone")})
    return jsonify({"error": "Noma'lum so'rov"}), 400


# ===================== WEBHOOK =====================
@app.route('/', defaults={'path': ''}, methods=['POST', 'GET'])
@app.route('/<path:path>', methods=['POST', 'GET'])
def webhook(path):
    if "catalog" in request.args and request.method == "GET":
        return public_catalog()
    if "admin" in request.args:
        return admin_api()
    if "app" in request.args:
        return app_api()
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
