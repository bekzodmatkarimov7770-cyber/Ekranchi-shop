from flask import Flask, request, jsonify
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
import json, base64, os
import io, csv
import urllib.request

BOT_TOKEN = "8484579263:AAGZu38VEXN4Hx5Yup12JoZnBZa1TlCDVy0"
WEB_APP_URL = "https://bekzodmatkarimov7770-cyber.github.io/Ekranchi-shop/market.html?v=super_v2"
ADMIN_ID = 1758833704
CARD_NUMBER = "9860 1266 0304 4796"
CARD_NAME = "Bekzod M. (Humo / Uzcard)"

USERS_FILE = "/tmp/users.json"
VISITORS_FILE = "/tmp/visitors.json"
ORDERS_FILE = "/tmp/orders.json"
CACHED_CATALOG = {}

WARRANTY_TEXT = (
    "🛡 <b>KAFOLAT VA QAYTARISH SHARTLARI (2 OY):</b>\n"
    "• Barcha displeylarga <b>2 oy kafolat</b> mavjud.\n"
    "• Zavod braki bo'lsa, xohishingizga ko'ra yangisiga almashtirib beriladi yoki pulingiz to'liq qaytariladi.\n"
    "• ⚠️ <b>Qat'iy talab:</b> Brakligini isbotlovchi aniq <b>video yoki rasm</b> bo'lishi shart! "
    "Rasmi yoki videosi bo'lmasa, mahsulot mutlaqo qaytarib olinmaydi!"
)

# CATALOGNI GITHUBDAN AVTOMATIK O'QIB OLISH (Aslo qotib qolmaydi)
def get_catalog():
    global CACHED_CATALOG
    if CACHED_CATALOG: return CACHED_CATALOG
    try:
        url = "https://bekzodmatkarimov7770-cyber.github.io/Ekranchi-shop/data.js"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            text = response.read().decode('utf-8')
            if 'const productsData =' in text:
                json_str = text.split('const productsData =')[1].split(';')[0].strip()
                data = json.loads(json_str)
                catalog = {}
                for item in data: catalog[str(item.get('id'))] = item
                CACHED_CATALOG = catalog
                return catalog
    except Exception as e: print("Baza o'qishda xatolik:", e)
    return {}

def load_data(path):
    if os.path.exists(path):
        try:
            with open(path, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_data(path, data):
    try:
        with open(path, "w") as f: json.dump(data, f)
    except: pass

def encode_data(d): return base64.b64encode(json.dumps(d, separators=(',', ':')).encode()).decode()

def save_order(cid, payload):
    orders = load_data(ORDERS_FILE)
    orders[str(cid)] = payload
    save_data(ORDERS_FILE, orders)

def get_payload(cid):
    orders = load_data(ORDERS_FILE)
    return orders.get(str(cid))

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)

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
    uid = str(m.chat.id)
    name = m.from_user.first_name or "Mijoz"
    users = load_data(USERS_FILE)
    if uid in users and isinstance(users[uid], dict) and users[uid].get('role'):
        txt = f"Assalomu alaykum, <b>{name}</b>! 👋\n\n<b>@ekranchi_bola</b> do'konimizga xush kelibsiz!\n\nPastdagi <b>«🛍 Do'konni ochish»</b> tugmasini bosib bemalol buyurtma bering: 👇"
        bot.send_message(m.chat.id, txt, reply_markup=main_kb(), parse_mode="HTML")
    else:
        txt = f"Assalomu alaykum, <b>{name}</b>!\nDo'konga kirish uchun <b>«📱 Telefon raqamimni yuborish»</b> tugmasini bosing:"
        bot.send_message(m.chat.id, txt, reply_markup=contact_kb(), parse_mode="HTML")

@bot.message_handler(content_types=['contact'])
def handle_contact(m):
    if m.contact and m.contact.user_id == m.from_user.id:
        phone = '+' + m.contact.phone_number if not m.contact.phone_number.startswith('+') else m.contact.phone_number
        uid = str(m.chat.id)
        users = load_data(USERS_FILE)
        users[uid] = {"phone": phone, "role": None, "name": m.from_user.first_name}
        save_data(USERS_FILE, users)
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(InlineKeyboardButton("🤝 Optom (Do'kon)", callback_data="set_role:Optom"), InlineKeyboardButton("👤 Chakana (Dona)", callback_data="set_role:Chakana"))
        bot.send_message(m.chat.id, f"✅ Raqamingiz: {phone}\nIltimos, rejimni tanlang:", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith('set_role:'))
def handle_role_selection(c):
    role = c.data.split(':')[1]
    uid = str(c.message.chat.id)
    users = load_data(USERS_FILE)
    if uid in users and isinstance(users[uid], dict):
        users[uid]['role'] = role
        save_data(USERS_FILE, users)
    try: bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=None)
    except: pass
    bot.send_message(c.message.chat.id, f"✅ Saqlandi! Rejim: <b>{role}</b>\nKatalogni ochishingiz mumkin:", reply_markup=main_kb(), parse_mode="HTML")

@bot.message_handler(content_types=['web_app_data'])
def handle_order(m):
    try:
        data = json.loads(m.web_app_data.data)
        cid = str(m.chat.id)
        user_info = load_data(USERS_FILE).get(cid, {})
        phone = user_info.get('phone', "Noma'lum") if isinstance(user_info, dict) else str(user_info)
        role = user_info.get('role', 'Noma'lum') if isinstance(user_info, dict) else "Noma'lum"
        
        name = data.get('n', 'Mijoz')
        deliv = data.get('d', 'BTS')
        addr = data.get('a', '')
        t_qty = int(data.get('tq', 0))
        t_sum = int(data.get('ts', 0))
        pt = data.get('pt', 'Chakana')
        items_arr = data.get('i', [])
        uname = f"@{m.from_user.username}" if m.from_user.username else "-"

        # BAZADAN EKRNALARNI ANIQLAB EXCEL YARATISH
        catalog = get_catalog()
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer, delimiter=',')
        writer.writerow(["№", "Model nomi", "Soni", "Narxi (UZS)", "Umumiy summa (UZS)"])

        payload_items, items_txt = [], ""
        idx = 1
        is_wholesale = (pt == "Optom")

        for it in items_arr:
            item_id = str(it[0])
            q_it = int(it[1])
            cat_item = catalog.get(item_id)
            
            if cat_item:
                n_it = cat_item.get('name', f"Model-{item_id}")
                p_it = int(cat_item.get('wholesale', 0)) if is_wholesale else int(cat_item.get('retail', 0))
            else:
                n_it = f"ID: {item_id} (Noma'lum)"
                p_it = 0
                
            subtotal = q_it * p_it
            writer.writerow([idx, n_it, q_it, p_it, subtotal])
            
            if idx <= 8: items_txt += f"• <b>{n_it[:30]}</b>: {q_it} dona\n"
            elif idx == 9: items_txt += f"<i>... va yana tovarlar bor (jami {len(items_arr)} xil)</i>\n"
            
            payload_items.append({"n": n_it, "oq": q_it, "aq": q_it, "p": p_it})
            idx += 1

        payload = {"name": name, "phone": phone, "deliv": deliv, "addr": addr, "pt": pt, "items": payload_items}
        save_order(cid, payload)
        
        # CSV faylni kodlash (Mijoz uchun Excel)
        csv_bytes = csv_buffer.getvalue().encode('utf-8-sig')
        csv_file = io.BytesIO(csv_bytes)
        csv_file.name = f"Buyurtma_{name.replace(' ', '_')}.csv"

        client_txt = (
            f"🛒 <b>Buyurtmangiz qabul qilindi!</b>\n━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>Mijoz:</b> {name}\n📞 <b>Telefon:</b> {phone}\n"
            f"🚚 <b>Yetkazish:</b> {deliv} | 📍 {addr}\n"
            f"📦 <b>Tarkibi:</b>\n{items_txt}━━━━━━━━━━━━━━━━━━━\n"
            f"💰 <b>JAMI TO'LOV:</b> <b>{t_sum:,} so'm</b> ({t_qty} ta)\n\n"
            f"💳 Karta raqami: <code>{CARD_NUMBER}</code>\nQabul qiluvchi: <b>{CARD_NAME}</b>\n\n"
            f"📸 To'lov qilgach, chek rasmini shu chatga yuboring.\n\n{WARRANTY_TEXT}"
        )
        bot.send_message(int(cid), client_txt, parse_mode="HTML")

        # ADMIN XABARI - Hech qachon uzilmaydi (Limitga tushmaydi)
        if ADMIN_ID:
            b64 = encode_data(payload)
            tag = f'<a href="https://t.me/ekranchi?d={b64[:20]}">📦</a>'
            
            admin_txt = (
                f"🔔 <b>YANGI BUYURTMA KELDI!</b> {tag}\n"
                f"👤 <b>Mijoz:</b> {name} ({uname})\n"
                f"📞 <b>Raqam:</b> {phone} ({role})\n"
                f"🚚 <b>Manzil:</b> {deliv} | 📍 {addr[:50]}\n"
                f"📊 <b>Rejim:</b> {pt}\n"
                f"💰 <b>Summa:</b> <b>{t_sum:,} so'm</b> ({t_qty} ta)\n\n"
                f"📥 <i>To'liq ro'yxatni pastdagi Excel (.csv) fayldan ko'ring 👇</i>"
            )
            bot.send_document(ADMIN_ID, csv_file, caption=admin_txt, reply_markup=admin_order_kb(cid), parse_mode="HTML")
            
    except Exception as e:
        print("XATOLIK:", e)

def show_missing_menu_screen(chat_id, message_id, p, cid):
    m = InlineKeyboardMarkup(row_width=1)
    for idx, it in enumerate(p.get('items', [])):
        oq, aq = it.get('oq', 1), it.get('aq', 1)
        if aq == oq: st = f"✅ BOR: {it.get('n')[:20]} ({aq}/{oq} ta)"
        elif aq == 0: st = f"❌ YO'Q: {it.get('n')[:20]} (0/{oq} ta)"
        else: st = f"⚠️ KAM: {it.get('n')[:20]} ({aq}/{oq} ta)"
        m.add(InlineKeyboardButton(st, callback_data=f"ed:{cid}:{idx}"))
    m.add(InlineKeyboardButton("📤 Mijozga xabar yuborish", callback_data=f"snd_miss:{cid}"), InlineKeyboardButton("⬅️ Orqaga", callback_data=f"back_ord:{cid}"))
    try: bot.edit_message_text(f"⚠️ <b>Omborda kam yoki yo'q ekranni tanlang:</b>", chat_id, message_id, reply_markup=m, parse_mode="HTML")
    except: pass

@bot.callback_query_handler(func=lambda c: c.data.startswith('missing_menu:'))
def handle_missing_menu(c):
    cid = c.data.split(':')[1]
    p = get_payload(cid)
    if not p: return bot.answer_callback_query(c.id, "Eski buyurtma tizimdan o'chgan. Mijozga to'g'ridan-to'g'ri yozing.", show_alert=True)
    bot.answer_callback_query(c.id)
    show_missing_menu_screen(c.message.chat.id, c.message.message_id, p, cid)

def show_edit_item_screen(chat_id, message_id, p, idx, cid):
    it = p['items'][idx]
    oq, aq = it.get('oq', 1), it.get('aq', 1)
    m = InlineKeyboardMarkup().row(InlineKeyboardButton("-5", callback_data=f"st:{cid}:{idx}:-5"), InlineKeyboardButton("-1", callback_data=f"st:{cid}:{idx}:-1"), InlineKeyboardButton("+1", callback_data=f"st:{cid}:{idx}:1"), InlineKeyboardButton("+5", callback_data=f"st:{cid}:{idx}:5"))
    m.row(InlineKeyboardButton("❌ Yo'q (0 ta)", callback_data=f"st_set:{cid}:{idx}:0"), InlineKeyboardButton(f"✅ To'liq ({oq} ta)", callback_data=f"st_set:{cid}:{idx}:{oq}"))
    m.row(InlineKeyboardButton("⬅️ Ro'yxatga qaytish", callback_data=f"back_list:{cid}"))
    txt = f"🛠 <b>MODEL: {it.get('n')}</b>\n📦 Buyurtma: <b>{oq} dona</b>\n✅ Mavjud: <b>{aq} dona</b>\n❌ Kam: <b>{oq-aq} dona</b>"
    try: bot.edit_message_text(txt, chat_id, message_id, reply_markup=m, parse_mode="HTML")
    except: pass

@bot.callback_query_handler(func=lambda c: c.data.startswith('ed:'))
def handle_edit_item(c):
    cid, idx = c.data.split(':')[1], int(c.data.split(':')[2])
    p = get_payload(cid)
    if not p or idx >= len(p.get('items', [])): return
    bot.answer_callback_query(c.id)
    show_edit_item_screen(c.message.chat.id, c.message.message_id, p, idx, cid)

@bot.callback_query_handler(func=lambda c: c.data.startswith('st:') or c.data.startswith('st_set:'))
def handle_change_qty(c):
    parts = c.data.split(':')
    action, cid, idx, val = parts[0], parts[1], int(parts[2]), int(parts[3])
    p = get_payload(cid)
    if not p or idx >= len(p.get('items', [])): return bot.answer_callback_query(c.id, "Xato!")
    oq, current_aq = p['items'][idx].get('oq', 1), p['items'][idx].get('aq', 1)
    new_aq = max(0, min(oq, current_aq + val)) if action == 'st' else max(0, min(oq, val))
    p['items'][idx]['aq'] = new_aq
    save_order(cid, p)
    bot.answer_callback_query(c.id, f"Mavjud: {new_aq} ta")
    show_edit_item_screen(c.message.chat.id, c.message.message_id, p, idx, cid)

@bot.callback_query_handler(func=lambda c: c.data.startswith('back_list:'))
def handle_back_list(c):
    bot.answer_callback_query(c.id)
    cid = c.data.split(':')[1]
    p = get_payload(cid)
    if p: show_missing_menu_screen(c.message.chat.id, c.message.message_id, p, cid)

@bot.callback_query_handler(func=lambda c: c.data.startswith('back_ord:'))
def handle_back_ord(c):
    cid = c.data.split(':')[1]
    p = get_payload(cid)
    if not p: return bot.answer_callback_query(c.id, "Eski buyurtma tizimdan o'chirilgan!", show_alert=True)
    bot.answer_callback_query(c.id)
    s_tot, q_tot = sum(it.get('aq', it.get('oq', 1)) * it.get('p', 0) for it in p.get('items', [])), sum(it.get('aq', it.get('oq', 1)) for it in p.get('items', []))
    txt = f"🔔 <b>BUYURTMA: {p.get('name')}</b>\n📞 <b>Raqam:</b> {p.get('phone')}\n🚚 <b>Yetkazish:</b> {p.get('deliv')}\n📊 <b>Rejim:</b> {p.get('pt')}\n💰 <b>Summa:</b> <b>{s_tot:,} so'm</b> ({q_tot} ta)"
    try: bot.edit_message_text(txt, c.message.chat.id, c.message.message_id, reply_markup=admin_order_kb(cid), parse_mode="HTML")
    except: pass

@bot.callback_query_handler(func=lambda c: c.data.startswith('snd_miss:'))
def handle_snd_miss(c):
    cid = c.data.split(':')[1]
    p = get_payload(cid)
    if not p: return bot.answer_callback_query(c.id, "Xato!")
    items = p.get('items', [])
    if not any(it.get('aq', it.get('oq')) < it.get('oq') for it in items): return bot.answer_callback_query(c.id, "Hamma tovar yetarli!", show_alert=True)
    
    miss_t, part_t, av_t, n_sum, n_qty = "", "", "", 0, 0
    for it in items:
        oq, aq, pr = it.get('oq', 1), it.get('aq', 1), it.get('p', 0)
        sub = aq * pr
        n_sum += sub
        n_qty += aq
        if aq == 0: miss_t += f"❌ <b>{it.get('n')}</b> — (Umuman yo'q)\n"
        elif aq < oq: part_t += f"⚠️ <b>{it.get('n')}</b> — {oq} ta so'ralgan, <b>{aq} ta bor</b>\n"
        else: av_t += f"✅ <b>{it.get('n')}</b> — {aq} dona ({sub:,} so'm)\n"

    msg = f"⚠️ <b>DIQQAT: AYRIM MODELLAR OMBORDA KAM YOKI YO'Q!</b>\n━━━━━━━━━━━━━━━━━━━\n{miss_t}{part_t}━━━━━━━━━━━━━━━━━━━\n📦 <b>Bor tovarlar:</b>\n{av_t if av_t else 'Qolmadi'}\n━━━━━━━━━━━━━━━━━━━\n💰 <b>Qayta hisoblangan to'lov: {n_sum:,} so'm</b> ({n_qty} ta)\n💳 Karta: <code>{CARD_NUMBER}</code> ({CARD_NAME})"
    try: bot.send_message(int(cid), msg, reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("💬 Admin bilan bog'lanish", url=f"tg://user?id={ADMIN_ID}")), parse_mode="HTML")
    except: pass
    try: bot.edit_message_text(f"✅ <b>Mijozga xabar ketdi!</b>\n💰 Yangi summa: <b>{n_sum:,} so'm</b> ({n_qty} ta)", c.message.chat.id, c.message.message_id, reply_markup=admin_order_kb(cid), parse_mode="HTML")
    except: pass
    bot.answer_callback_query(c.id, "Mijozga yuborildi!")

@bot.message_handler(content_types=['photo'])
def handle_receipt(m):
    cid = str(m.chat.id)
    phone = load_data(USERS_FILE).get(cid, {}).get('phone', "Noma'lum") if isinstance(load_data(USERS_FILE).get(cid, {}), dict) else "Noma'lum"
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton("✅ Bugun yetkazish", callback_data=f"pay:{cid}:today"), InlineKeyboardButton("✅ Ertaga yetkazish", callback_data=f"pay:{cid}:tomorrow"), InlineKeyboardButton("❌ Soxta chek", callback_data=f"pay:{cid}:fake"))
    bot.send_photo(ADMIN_ID, m.photo[-1].file_id, caption=f"🧾 <b>TO'LOV CHEKI KELDI!</b>\n👤 {m.from_user.first_name}\n📞 {phone}\n🆔 <code>{cid}</code>", reply_markup=kb, parse_mode="HTML")
    bot.reply_to(m, "✅ Chekingiz qabul qilindi!")

@bot.callback_query_handler(func=lambda c: c.data.startswith('pay:'))
def process_pay(c):
    _, cid, act = c.data.split(':')
    res = {"today": "🎉 Tasdiqlandi! BUGUN yetkaziladi.", "tomorrow": "🎉 Tasdiqlandi! ERTAGA yetkaziladi.", "cash": "🤝 Tasdiqlandi! To'lov naqd olinadi.", "fake": "⚠️ Kartaga pul tushmadi! Tekshiring.", "cancel": "❌ Bekor qilindi."}
    bot.send_message(int(cid), f"🔔 {res.get(act, '')}")
    bot.answer_callback_query(c.id, "Xabar ketdi!")
    try: bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=None)
    except: pass

@app.route('/', defaults={'path': ''}, methods=['POST', 'GET'])
@app.route('/<path:path>', methods=['POST', 'GET'])
def webhook(path):
    if request.method == 'GET': return "Ekranchi Bot Active", 200
    if request.headers.get('content-type') == 'application/json':
        bot.process_new_updates([telebot.types.Update.de_json(request.get_data().decode('utf-8'))])
        return jsonify({"status": "ok"}), 200
    return "Forbidden", 403
