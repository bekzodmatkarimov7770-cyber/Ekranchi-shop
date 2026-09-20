from flask import Flask, request, jsonify
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
import json, base64, os
import io, csv

BOT_TOKEN = "8484579263:AAGZu38VEXN4Hx5Yup12JoZnBZa1TlCDVy0"
WEB_APP_URL = "https://bekzodmatkarimov7770-cyber.github.io/Ekranchi-shop/market.html?v=excel_v1"
ADMIN_ID = 1758833704
CARD_NUMBER = "9860 1266 0304 4796"
CARD_NAME = "Bekzod M. (Humo / Uzcard)"

USERS_FILE = "/tmp/users.json"
VISITORS_FILE = "/tmp/visitors.json"
ORDERS_FILE = "/tmp/orders.json"
CACHE_ORDERS = {}

WARRANTY_TEXT = (
    "🛡 <b>KAFOLAT VA QAYTARISH SHARTLARI (2 OY):</b>\n"
    "• Barcha displeylarga <b>2 oy kafolat</b> mavjud.\n"
    "• Zavod braki bo'lsa, xohishingizga ko'ra yangisiga almashtirib beriladi yoki pulingiz to'liq qaytariladi.\n"
    "• ⚠️ <b>Qat'iy talab:</b> Brakligini isbotlovchi aniq <b>video yoki rasm</b> bo'lishi shart! "
    "Rasmi yoki videosi bo'lmasa, mahsulot mutlaqo qaytarib olinmaydi!"
)

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

def encode_data(d):
    return base64.b64encode(json.dumps(d, separators=(',', ':')).encode()).decode()

def decode_data(b64_str):
    try:
        return json.loads(base64.b64decode(b64_str.encode()).decode())
    except: return None

def save_order(cid, payload):
    CACHE_ORDERS[str(cid)] = payload
    orders = load_data(ORDERS_FILE)
    orders[str(cid)] = payload
    save_data(ORDERS_FILE, orders)

def get_payload(c, cid):
    cid_str = str(cid)
    if cid_str in CACHE_ORDERS: return CACHE_ORDERS[cid_str]
    orders = load_data(ORDERS_FILE)
    if cid_str in orders:
        CACHE_ORDERS[cid_str] = orders[cid_str]
        return orders[cid_str]
    if c.message and c.message.entities:
        for e in c.message.entities:
            if e.type == 'text_link' and e.url and 'd=' in e.url:
                p = decode_data(e.url.split('d=')[1])
                if p:
                    save_order(cid_str, p)
                    return p
    return None

def get_users_count(uid):
    d = load_data(VISITORS_FILE)
    if str(uid) not in d:
        d[str(uid)] = True
        save_data(VISITORS_FILE, d)
    return f"{1200 + len(d):,}".replace(",", " ")

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
    u_count = get_users_count(uid)
    users = load_data(USERS_FILE)

    if uid in users and isinstance(users[uid], dict) and users[uid].get('role'):
        txt = (
            f"Assalomu alaykum, <b>{name}</b>! 👋\n\n"
            f"<b>@ekranchi_bola</b> do'konimizga xush kelibsiz!\n\n"
            f"👥 <b>Faol ustalar safimiz:</b> {u_count}+ nafar\n"
            f"📦 Omborda barcha turdagi Samsung va Redmi displeylari mavjud.\n"
            f"🚚 Butun O'zbekiston bo'ylab BTS Pochta va tezkor taksi orqali yetkazib beramiz.\n\n"
            f"Pastdagi <b>«🛍 Do'konni ochish»</b> tugmasini bosib buyurtma berishingiz mumkin: 👇"
        )
        bot.send_message(m.chat.id, txt, reply_markup=main_kb(), parse_mode="HTML")
    else:
        txt = (
            f"Assalomu alaykum, <b>{name}</b>! 👋\n\n"
            f"<b>@ekranchi_bola</b> do'konimizga xush kelibsiz!\n\n"
            f"👥 <b>Foydalanuvchilar:</b> {u_count}+ nafar ustalar\n\n"
            f"Displeylarni tanlash va buyurtma berish uchun, iltimos, pastdagi <b>«📱 Telefon raqamimni yuborish»</b> tugmasini bosing: 👇"
        )
        bot.send_message(m.chat.id, txt, reply_markup=contact_kb(), parse_mode="HTML")

@bot.message_handler(commands=['stat'])
def handle_stat(m):
    if str(m.chat.id) == str(ADMIN_ID):
        users = load_data(USERS_FILE)
        visitors = load_data(VISITORS_FILE)
        total_v = max(len(users), len(visitors))
        optom_count = sum(1 for u in users.values() if isinstance(u, dict) and u.get('role') == 'Optom')
        retail_count = sum(1 for u in users.values() if isinstance(u, dict) and u.get('role') == 'Chakana')
        
        txt = (
            f"📊 <b>BOT STATISTIKASI (CRM):</b>\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"👥 Jami botga kirganlar: <b>{1200 + total_v} ta</b>\n"
            f"📱 Raqam tasdiqlaganlar: <b>{len(users)} ta</b>\n"
            f"🤝 Optomchilar (Usta/Do'kon): <b>{optom_count} ta</b>\n"
            f"👤 Chakanachilar (Dona): <b>{retail_count} ta</b>"
        )
        bot.send_message(m.chat.id, txt, parse_mode="HTML")

@bot.message_handler(content_types=['contact'])
def handle_contact(m):
    if m.contact and m.contact.user_id == m.from_user.id:
        phone = m.contact.phone_number
        if not phone.startswith('+'): phone = '+' + phone
        uid = str(m.chat.id)
        
        users = load_data(USERS_FILE)
        users[uid] = {"phone": phone, "role": None, "name": m.from_user.first_name}
        save_data(USERS_FILE, users)

        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton("🤝 Optom (Do'kon / Usta)", callback_data="set_role:Optom"),
            InlineKeyboardButton("👤 Chakana (Dona)", callback_data="set_role:Chakana")
        )
        bot.send_message(
            m.chat.id, 
            f"✅ <b>Raqamingiz tasdiqlandi:</b> {phone}\n\nIltimos, xarid qilish rejimini tanlang:", 
            reply_markup=kb, 
            parse_mode="HTML"
        )

@bot.callback_query_handler(func=lambda c: c.data.startswith('set_role:'))
def handle_role_selection(c):
    role = c.data.split(':')[1]
    uid = str(c.message.chat.id)
    
    users = load_data(USERS_FILE)
    if uid in users and isinstance(users[uid], dict):
        users[uid]['role'] = role
        save_data(USERS_FILE, users)
        
    bot.answer_callback_query(c.id, f"Siz '{role}' rejimini tanladingiz!")
    try:
        bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=None)
    except: pass
        
    txt = (
        f"✅ <b>Muvaffaqiyatli saqlandi!</b> Sizning rejimingiz: <b>{role}</b>\n\n"
        f"Endi pastdagi <b>«🛍 Do'konni ochish»</b> tugmasi orqali katalikka o'tishingiz mumkin:"
    )
    bot.send_message(c.message.chat.id, txt, reply_markup=main_kb(), parse_mode="HTML")

@bot.message_handler(content_types=['web_app_data'])
def handle_order(m):
    try:
        data = json.loads(m.web_app_data.data)
        cid = str(m.chat.id)
        user_info = load_data(USERS_FILE).get(cid, {})
        phone = user_info.get('phone', 'Ko\'rsatilmagan') if isinstance(user_info, dict) else str(user_info)
        role = user_info.get('role', 'Aniqlanmagan') if isinstance(user_info, dict) else 'Aniqlanmagan'
        
        name = data.get('n', data.get('name', 'Mijoz'))
        deliv = data.get('d', data.get('delivery', 'BTS'))
        addr = data.get('a', data.get('address', ''))
        t_qty = data.get('tq', data.get('total_qty', 0))
        t_sum = data.get('ts', data.get('total_sum', 0))
        pt = data.get('pt', data.get('price_type', 'Chakana'))
        items = data.get('i', data.get('items', []))
        uname = f"@{m.from_user.username}" if m.from_user.username else "-"

        # EXCEL FAYL YARATISH (Python xotirasida)
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer, delimiter=',')
        writer.writerow(["№", "Model nomi", "Soni", "Narxi (UZS)", "Umumiy summa (UZS)"])

        payload_items, items_txt = [], ""
        for i, it in enumerate(items, 1):
            n_it = it.get('n', it.get('name', 'Boshqa'))
            q_it = int(it.get('q', it.get('qty', 1)))
            p_it = int(it.get('p', it.get('price', 0)))
            
            # Excelga yozish
            writer.writerow([i, n_it, q_it, p_it, q_it * p_it])
            
            # Xabarni qisqartirish (uzun ro'yxat bo'lib ketmasligi uchun)
            if i <= 15:
                items_txt += f"{i}. <b>{n_it[:30]}</b>\n   └ {q_it} dona × {p_it:,} = <b>{q_it*p_it:,} so'm</b>\n"
            elif i == 16:
                items_txt += f"\n... <i>va yana {len(items)-15} xil tovar. (To'liq ro'yxat Excelda!)</i>\n"
            
            payload_items.append({"n": n_it, "oq": q_it, "aq": q_it, "p": p_it})

        payload = {"cid": cid, "name": name, "phone": phone, "deliv": deliv, "addr": addr, "pt": pt, "items": payload_items}
        save_order(cid, payload)
        
        # Excel ma'lumotlarini UTF-8 orqali tayyorlash
        csv_buffer.seek(0)
        csv_bytes = csv_buffer.getvalue().encode('utf-8-sig')

        b64 = encode_data(payload)
        tag = f'<a href="https://t.me/ekranchi?d={b64}">📦</a>'

        client_txt = (
            f"🛒 <b>Buyurtmangiz qabul qilindi!</b>\n━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>Qabul qiluvchi:</b> {name}\n📞 <b>Telefon:</b> {phone}\n"
            f"🚚 <b>Yetkazish:</b> {deliv} | 📍 {addr}\n📊 <b>Rejim:</b> {pt}\n"
            f"📦 <b>Tarkibi:</b>\n{items_txt}━━━━━━━━━━━━━━━━━━━\n"
            f"💰 <b>JAMI TO'LOV:</b> <b>{t_sum:,} so'm</b> ({t_qty} ta)\n\n"
            f"💳 Karta raqami: <code>{CARD_NUMBER}</code>\n"
            f"Qabul qiluvchi: <b>{CARD_NAME}</b>\n\n"
            f"📸 To'lov qilgach, chek rasmini shu chatga yuboring.\n\n"
            f"{WARRANTY_TEXT}"
        )
        client_kb = InlineKeyboardMarkup().add(InlineKeyboardButton("💬 Admin bilan bog'lanish", url=f"tg://user?id={ADMIN_ID}"))
        bot.send_message(int(cid), client_txt, reply_markup=client_kb, parse_mode="HTML", disable_web_page_preview=True)

        if ADMIN_ID:
            admin_txt = (
                f"🔔 <b>YANGI BUYURTMA TUSHDI!</b>\n━━━━━━━━━━━━━━━━━━━\n"
                f"👤 <b>Mijoz:</b> {name} ({uname})\n📞 <b>Raqam:</b> {phone}\n"
                f"🏷 <b>Mijoz Turi (CRM):</b> <b>{role}</b>\n"
                f"🚚 <b>Yetkazish:</b> {deliv} | 📍 {addr}\n📊 <b>Rejim:</b> {pt}\n"
                f"💰 <b>Summa:</b> <b>{t_sum:,} so'm</b> ({t_qty} ta)\n\n"
                f"{tag} <i>Buyurtmaning to'liq ro'yxati quyidagi Excel faylda: 👇</i>"
            )
            bot.send_document(
                ADMIN_ID, 
                document=('Buyurtma_Ekranchi.csv', csv_bytes),
                caption=admin_txt,
                reply_markup=admin_order_kb(cid),
                parse_mode="HTML"
            )
    except Exception as e:
        print(f"Order error: {e}")

def show_edit_item_screen(chat_id, message_id, p, idx, cid):
    it = p['items'][idx]
    oq = it.get('oq', 1)
    aq = it.get('aq', oq)
    diff = oq - aq

    m = InlineKeyboardMarkup()
    m.row(
        InlineKeyboardButton("-5", callback_data=f"st:{cid}:{idx}:-5"),
        InlineKeyboardButton("-1", callback_data=f"st:{cid}:{idx}:-1"),
        InlineKeyboardButton("+1", callback_data=f"st:{cid}:{idx}:1"),
        InlineKeyboardButton("+5", callback_data=f"st:{cid}:{idx}:5")
    )
    m.row(
        InlineKeyboardButton("❌ Yo'q (0 ta)", callback_data=f"st_set:{cid}:{idx}:0"),
        InlineKeyboardButton(f"✅ To'liq ({oq} ta)", callback_data=f"st_set:{cid}:{idx}:{oq}")
    )
    m.row(InlineKeyboardButton("⬅️ Ro'yxatga qaytish", callback_data=f"back_list:{cid}"))

    b64 = encode_data(p)
    tag = f'<a href="https://t.me/ekranchi?d={b64}">🛠</a>'

    txt = (
        f"{tag} <b>MODEL: {it.get('n')}</b>\n━━━━━━━━━━━━━━━━━━━\n"
        f"📦 Buyurtma qilingan: <b>{oq} dona</b>\n"
        f"✅ Omborda mavjud soni: <b>{aq} dona</b>\n"
        f"❌ Yetishmayotgani: <b>{diff} dona</b>\n━━━━━━━━━━━━━━━━━━━\n"
        f"Pastdagi tugmalar orqali sonini belgilang:"
    )
    try: bot.edit_message_text(txt, chat_id, message_id, reply_markup=m, parse_mode="HTML", disable_web_page_preview=True)
    except Exception: pass

def show_missing_menu_screen(chat_id, message_id, p, cid):
    m = InlineKeyboardMarkup(row_width=1)
    for idx, it in enumerate(p.get('items', [])):
        oq, aq = it.get('oq', 1), it.get('aq', 1)
        if aq == oq: st = f"✅ BOR: {it.get('n')[:20]} ({aq}/{oq} ta)"
        elif aq == 0: st = f"❌ YO'Q: {it.get('n')[:20]} (0/{oq} ta)"
        else: st = f"⚠️ KAM: {it.get('n')[:20]} ({aq}/{oq} ta)"
        m.add(InlineKeyboardButton(st, callback_data=f"ed:{cid}:{idx}"))

    m.add(
        InlineKeyboardButton("📤 Mijozga xabar yuborish", callback_data=f"snd_miss:{cid}"),
        InlineKeyboardButton("⬅️ Orqaga", callback_data=f"back_ord:{cid}")
    )

    b64 = encode_data(p)
    tag = f'<a href="https://t.me/ekranchi?d={b64}">⚠️</a>'
    txt = f"{tag} <b>Omborda kam yoki yo'q ekranni tanlang:</b>\n<i>(Kerakli model ustiga bosing)</i>"
    try: bot.edit_message_text(txt, chat_id, message_id, reply_markup=m, parse_mode="HTML", disable_web_page_preview=True)
    except Exception: pass

@bot.callback_query_handler(func=lambda c: c.data.startswith('missing_menu:'))
def handle_missing_menu(c):
    cid = c.data.split(':')[1]
    p = get_payload(c, cid)
    if not p: return bot.answer_callback_query(c.id, "Buyurtma topilmadi!", show_alert=True)
    bot.answer_callback_query(c.id)
    show_missing_menu_screen(c.message.chat.id, c.message.message_id, p, cid)

@bot.callback_query_handler(func=lambda c: c.data.startswith('ed:'))
def handle_edit_item(c):
    bot.answer_callback_query(c.id)
    parts = c.data.split(':')
    cid, idx = parts[1], int(parts[2])
    p = get_payload(c, cid)
    if not p or idx >= len(p.get('items', [])): return
    show_edit_item_screen(c.message.chat.id, c.message.message_id, p, idx, cid)

@bot.callback_query_handler(func=lambda c: c.data.startswith('st:') or c.data.startswith('st_set:'))
def handle_change_qty(c):
    parts = c.data.split(':')
    action, cid, idx, val = parts[0], parts[1], int(parts[2]), int(parts[3])

    p = get_payload(c, cid)
    if not p or idx >= len(p.get('items', [])): return bot.answer_callback_query(c.id, "Xatolik!")

    oq = p['items'][idx].get('oq', 1)
    current_aq = p['items'][idx].get('aq', oq)

    if action == 'st': new_aq = max(0, min(oq, current_aq + val))
    else: new_aq = max(0, min(oq, val))

    p['items'][idx]['aq'] = new_aq
    save_order(cid, p)

    bot.answer_callback_query(c.id, f"Mavjud: {new_aq} ta")
    show_edit_item_screen(c.message.chat.id, c.message.message_id, p, idx, cid)

@bot.callback_query_handler(func=lambda c: c.data.startswith('back_list:'))
def handle_back_list(c):
    bot.answer_callback_query(c.id)
    cid = c.data.split(':')[1]
    p = get_payload(c, cid)
    if p: show_missing_menu_screen(c.message.chat.id, c.message.message_id, p, cid)

@bot.callback_query_handler(func=lambda c: c.data.startswith('back_ord:'))
def handle_back_ord(c):
    bot.answer_callback_query(c.id)
    cid = c.data.split(':')[1]
    p = get_payload(c, cid)
    if not p: return

    s_tot, q_tot = 0, 0
    for it in p.get('items', []):
        q = it.get('aq', it.get('oq', 1))
        s_tot += q * it.get('p', 0)
        q_tot += q

    b64 = encode_data(p)
    tag = f'<a href="https://t.me/ekranchi?d={b64}">📦</a>'
    txt = (
        f"🔔 <b>BUYURTMA: {p.get('name')}</b>\n━━━━━━━━━━━━━━━━━━━\n"
        f"📞 <b>Raqam:</b> {p.get('phone')}\n"
        f"🚚 <b>Yetkazish:</b> {p.get('deliv')} | 📍 {p.get('addr')}\n"
        f"📊 <b>Rejim:</b> {p.get('pt')}\n━━━━━━━━━━━━━━━━━━━\n"
        f"{tag} <i>(Tovarlar ro'yxati tepadagi Excel faylda)</i>\n━━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>Summa:</b> <b>{s_tot:,} so'm</b> ({q_tot} ta)"
    )
    try: bot.edit_message_text(txt, c.message.chat.id, c.message.message_id, reply_markup=admin_order_kb(cid), parse_mode="HTML", disable_web_page_preview=True)
    except Exception: pass

@bot.callback_query_handler(func=lambda c: c.data.startswith('snd_miss:'))
def handle_snd_miss(c):
    cid = c.data.split(':')[1]
    p = get_payload(c, cid)
    if not p: return bot.answer_callback_query(c.id, "Buyurtma topilmadi!")

    items = p.get('items', [])
    has_change = any(it.get('aq', it.get('oq')) < it.get('oq') for it in items)
    if not has_change: return bot.answer_callback_query(c.id, "Hech qanday tovar kamaytirilmagan!", show_alert=True)

    miss_t, part_t, av_t, n_sum, n_qty = "", "", "", 0, 0
    for it in items:
        oq, aq, pr = it.get('oq', 1), it.get('aq', it.get('oq', 1)), it.get('p', 0)
        sub = aq * pr
        n_sum += sub
        n_qty += aq
        if aq == 0: miss_t += f"❌ <b>{it.get('n')}</b> — (Umuman yo'q)\n"
        elif aq < oq: part_t += f"⚠️ <b>{it.get('n')}</b> — {oq} ta so'ralgan, <b>{aq} ta bor</b>\n"
        else: av_t += f"✅ <b>{it.get('n')}</b> — {aq} dona ({sub:,} so'm)\n"

    msg = (
        f"⚠️ <b>DIQQAT: BUYURTMANING AYRIM MODELLARI OMBORDA KAM YOKI YO'Q!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━\n{miss_t}{part_t}━━━━━━━━━━━━━━━━━━━\n"
        f"📦 <b>Omborda bor tovarlar:</b>\n{av_t if av_t else '<i>Bor tovar qolmadi</i>'}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>Qayta hisoblangan to'lov:</b> <b>{n_sum:,} so'm</b> ({n_qty} ta)\n"
        f"💳 Karta raqami: <code>{CARD_NUMBER}</code>\n"
        f"Qabul qiluvchi: <b>{CARD_NAME}</b>\n\n"
        f"Mavjud tovarlarni chiqarishimiz uchun to'lov qilib chekni yuboring!\n\n"
        f"{WARRANTY_TEXT}"
    )
    kb = InlineKeyboardMarkup().add(InlineKeyboardButton("💬 Admin bilan bog'lanish", url=f"tg://user?id={ADMIN_ID}"))
    try: bot.send_message(int(cid), msg, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)
    except Exception: pass

    b64 = encode_data(p)
    tag = f'<a href="https://t.me/ekranchi?d={b64}">📦</a>'
    try:
        bot.edit_message_text(
            f"✅ <b>Mijozga xabar ketdi!</b>\n\n💰 Yangi summa: <b>{n_sum:,} so'm</b> ({n_qty} ta)\n{tag}",
            c.message.chat.id, c.message.message_id, reply_markup=admin_order_kb(cid), parse_mode="HTML", disable_web_page_preview=True
        )
    except Exception: pass
    bot.answer_callback_query(c.id, "Mijozga yuborildi!")

@bot.message_handler(content_types=['photo'])
def handle_receipt(m):
    cid = str(m.chat.id)
    user_info = load_data(USERS_FILE).get(cid, {})
    phone = user_info.get('phone', 'Ko\'rsatilmagan') if isinstance(user_info, dict) else str(user_info)
    role = user_info.get('role', 'Aniqlanmagan') if isinstance(user_info, dict) else 'Aniqlanmagan'
    
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("✅ Bugun yetkazish", callback_data=f"pay:{cid}:today"),
        InlineKeyboardButton("✅ Ertaga yetkazish", callback_data=f"pay:{cid}:tomorrow"),
        InlineKeyboardButton("❌ Soxta chek", callback_data=f"pay:{cid}:fake")
    )
    cap = f"🧾 <b>TO'LOV CHEKI KELDI!</b>\n👤 {m.from_user.first_name}\n📞 {phone}\n🏷 Tur: <b>{role}</b>\n🆔 <code>{cid}</code>"
    bot.send_photo(ADMIN_ID, m.photo[-1].file_id, caption=cap, reply_markup=kb, parse_mode="HTML")
    bot.reply_to(m, "✅ Chekingiz qabul qilindi!")

@bot.callback_query_handler(func=lambda c: c.data.startswith('pay:'))
def process_pay(c):
    _, cid, act = c.data.split(':')
    res = {
        "today": "🎉 To'lovingiz tasdiqlandi! Buyurtmangiz BUGUN yetkaziladi.",
        "tomorrow": "🎉 To'lovingiz tasdiqlandi! Buyurtmangiz ERTAGA yetkaziladi.",
        "cash": "🤝 Buyurtma tasdiqlandi! To'lov naqd olinadi.",
        "fake": "⚠️ Kartaga pul tushmadi! Chekni qayta tekshiring.",
        "cancel": "❌ Buyurtmangiz bekor qilindi."
    }
    bot.send_message(int(cid), f"🔔 {res.get(act, '')}")
    bot.answer_callback_query(c.id, "Mijozga xabar ketdi!")
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
