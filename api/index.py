from flask import Flask, request, jsonify
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
import json
import base64
import os

BOT_TOKEN = "8484579263:AAGZu38VEXN4Hx5Yup12JoZnBZa1TlCDVy0"
WEB_APP_URL = "https://bekzodmatkarimov7770-cyber.github.io/Ekranchi-shop/market.html?v=pro_v50"
ADMIN_ID = 1758833704

CARD_NUMBER = "9860 1266 0304 4796"
CARD_NAME = "Bekzod M. (Humo / Uzcard)"

USERS_FILE = "/tmp/users.json"
ALL_VISITORS_FILE = "/tmp/all_visitors.json"

def load_data(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(filepath, data):
    try:
        with open(filepath, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Xotira xatosi: {e}")

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)

# ==========================================
# FOYDALANUVCHILARNI SANASH TIZIMI
# ==========================================
def record_visitor(user_id):
    visitors = load_data(ALL_VISITORS_FILE)
    if not isinstance(visitors, dict):
        visitors = {}
    if str(user_id) not in visitors:
        visitors[str(user_id)] = True
        save_data(ALL_VISITORS_FILE, visitors)
    return len(visitors)

def get_user_count_display(user_id):
    count = record_visitor(user_id)
    # Baza nufuzi uchun 1250 ta doimiy mijoz + yangi a'zolar
    total = 1250 + count
    return f"{total:,}".replace(",", " ")

# ==========================================
# STATELESS BUYURTMA PAYLOADI
# ==========================================
def encode_order_payload(data):
    raw = json.dumps(data, separators=(',', ':')).encode('utf-8')
    return base64.b64encode(raw).decode('utf-8')

def extract_order_payload(text):
    if not text or "ORD_DATA:" not in text:
        return None
    try:
        b64_part = text.split("ORD_DATA:")[1].split("</tg-spoiler>")[0].strip()
        b64_clean = b64_part.split()[0]
        raw = base64.b64decode(b64_clean.encode('utf-8')).decode('utf-8')
        return json.loads(raw)
    except Exception as e:
        print(f"Payload xatosi: {e}")
        return None

def get_store_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(text="🛍 Do'konni ochish", web_app=WebAppInfo(url=WEB_APP_URL)))
    return markup

def get_contact_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton(text="📱 Telefon raqamimni yuborish", request_contact=True))
    return markup

def get_admin_order_markup(client_id):
    admin_markup = InlineKeyboardMarkup(row_width=2)
    admin_markup.add(
        InlineKeyboardButton("💵 Naqd kelishildi", callback_data=f"pay:{client_id}:cash"),
        InlineKeyboardButton("⚡️ Bugun yetkazish", callback_data=f"pay:{client_id}:today"),
        InlineKeyboardButton("📦 Ertaga yetkazish", callback_data=f"pay:{client_id}:tomorrow"),
        InlineKeyboardButton("❌ Bekor qilish", callback_data=f"pay:{client_id}:cancel"),
        InlineKeyboardButton("⚠️ Ayrim tovarlar yo'q (Belgilash)", callback_data=f"missing_menu:{client_id}")
    )
    return admin_markup

# ==========================================
# /START BUYRUG'I VA CHIROYLI SALOMLASHISH
# ==========================================
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = str(message.chat.id)
    user_name = message.from_user.first_name or "Hurmatli mijoz"
    users_display = get_user_count_display(user_id)
    user_phones = load_data(USERS_FILE)

    if user_id in user_phones:
        welcome_text = (
            f"Assalomu alaykum, <b>{user_name}</b>! 👋\n\n"
            f"🌟 <b>@ekranchi_bola</b> rasmiy kanalining <b>yagona original do'kon botiga</b> xush kelibsiz!\n\n"
            f"👥 <b>Faol ustalar safimiz:</b> {users_display}+ nafar\n"
            f"📦 <b>Omborda:</b> 95 xil yuqori sifatli Samsung va Redmi displeylari\n"
            f"🚚 <b>Yetkazib berish:</b> Butun O'zbekiston bo'ylab BTS Pochta va tezkor taksi\n\n"
            f"⚡️ Displeylar ro'yxati, ulgurji (optom 50+) va dona narxlar bilan tanishish hamda buyurtma berish uchun pastdagi tugmani bosing: 👇"
        )
        bot.send_message(message.chat.id, welcome_text, reply_markup=get_store_keyboard(), parse_mode="HTML")
    else:
        welcome_text = (
            f"Assalomu alaykum, <b>{user_name}</b>! 👋\n\n"
            f"🌟 <b>@ekranchi_bola</b> rasmiy kanalining <b>yagona original do'kon botiga</b> xush kelibsiz!\n\n"
            f"👥 <b>Botimizdan foydalanuvchilar:</b> {users_display}+ nafar usta va do'kondorlar\n"
            f"🛠 Telefon ekranlarining to'g'ridan-to'g'ri birinchi qo'l ulgurji va chakana ombori.\n\n"
            f"⚠️ <i>Buyurtmalarni tezkor va xavfsiz qabul qilish uchun, iltimos, pastdagi tugma orqali telefon raqamingizni tasdiqlang:</i> 👇"
        )
        bot.send_message(message.chat.id, welcome_text, reply_markup=get_contact_keyboard(), parse_mode="HTML")

@bot.message_handler(commands=['stat'])
def stats_command(message):
    if message.chat.id == ADMIN_ID:
        visitors = load_data(ALL_VISITORS_FILE)
        phones = load_data(USERS_FILE)
        bot.send_message(
            ADMIN_ID,
            f"📊 <b>BOT STATISTIKASI:</b>\n━━━━━━━━━━━━━━━━━━━\n"
            f"👥 <b>Jami kirganlar:</b> {len(visitors)} kishi\n"
            f"📞 <b>Raqamini tasdiqlaganlar:</b> {len(phones)} kishi\n"
            f"🌟 <b>Kanal:</b> @ekranchi_bola",
            parse_mode="HTML"
        )

@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    if message.contact and message.contact.user_id == message.from_user.id:
        phone = message.contact.phone_number
        if not phone.startswith('+'):
            phone = '+' + phone
        user_phones = load_data(USERS_FILE)
        user_phones[str(message.chat.id)] = phone
        save_data(USERS_FILE, user_phones)
        
        bot.send_message(
            message.chat.id,
            f"✅ <b>Raqamingiz muvaffaqiyatli tasdiqlandi:</b> {phone}\n\n"
            f"Endi do'konimizdan istalgancha displeylarni xarid qilishingiz mumkin!\n"
            f"Pastdagi <b>«🛍 Do'konni ochish»</b> tugmasini bosing:",
            reply_markup=get_store_keyboard(),
            parse_mode="HTML"
        )
    else:
        bot.send_message(
            message.chat.id,
            "⚠️ <b>Xatolik:</b> Iltimos, faqat pastdagi <b>«📱 Telefon raqamimni yuborish»</b> tugmasini bosing!",
            reply_markup=get_contact_keyboard(),
            parse_mode="HTML"
        )

# ==========================================
# BUYURTMANI QABUL QILISH
# ==========================================
@bot.message_handler(content_types=['web_app_data'])
def handle_order(message):
    try:
        raw = message.web_app_data.data
        data = json.loads(raw)
        client_id = str(message.chat.id)

        user_phones = load_data(USERS_FILE)
        verified_phone = user_phones.get(client_id, "Ko'rsatilmagan")
        name = data.get('name', 'Noma\'lum')
        delivery = data.get('delivery', 'BTS')
        address = data.get('address', 'Keltirilmagan')
        total_qty = data.get('total_qty', 0)
        total_sum = data.get('total_sum', 0)
        price_type = data.get('price_type', 'Chakana')
        items = data.get('items', [])
        user_username = f"@{message.from_user.username}" if message.from_user.username else "Mavjud emas"

        payload_items = []
        items_text = ""
        for idx, item in enumerate(items, 1):
            items_text += f"{idx}. <b>{item.get('name')}</b>\n   └ {item.get('qty')} dona × {item.get('price'):,} = <b>{item.get('subtotal'):,} so'm</b>\n"
            payload_items.append({
                "n": item.get('name'),
                "t": item.get('type', ''),
                "q": item.get('qty', 1),
                "p": item.get('price', 0),
                "s": item.get('subtotal', 0),
                "m": 0
            })

        order_payload = {
            "cid": client_id,
            "name": name,
            "phone": verified_phone,
            "deliv": delivery,
            "addr": address,
            "pt": price_type,
            "items": payload_items
        }
        b64_str = encode_order_payload(order_payload)

        client_markup = InlineKeyboardMarkup()
        client_markup.add(InlineKeyboardButton("💬 Admin bilan bog'lanish", url=f"tg://user?id={ADMIN_ID}"))

        client_text = (
            f"🛒 <b>Buyurtmangiz qabul qilindi!</b>\n━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>Qabul qiluvchi:</b> {name}\n📞 <b>Telefon:</b> {verified_phone}\n"
            f"🚚 <b>Yetkazish:</b> {delivery} | 📍 {address}\n"
            f"📊 <b>Narx turi:</b> <b>{price_type}</b>\n"
            f"📦 <b>Buyurtma tarkibi:</b>\n{items_text}━━━━━━━━━━━━━━━━━━━\n"
            f"💰 <b>JAMI TO'LOV:</b> <b>{total_sum:,} so'm</b> ({total_qty} ta)\n\n"
            f"💳 Karta raqami: <code>{CARD_NUMBER}</code>\n"
            f"Qabul qiluvchi: <b>{CARD_NAME}</b>\n\n"
            f"📸 To'lov qilgach, to'lov cheki rasmini shu chatga yuboring."
        )
        bot.send_message(int(client_id), client_text, reply_markup=client_markup, parse_mode="HTML")

        if ADMIN_ID:
            admin_text = (
                f"🔔 <b>YANGI BUYURTMA TUSHDI!</b>\n━━━━━━━━━━━━━━━━━━━\n"
                f"👤 <b>Mijoz:</b> {name} ({user_username})\n📞 <b>Raqam:</b> {verified_phone}\n"
                f"🚚 <b>Yetkazish:</b> {delivery} | 📍 {address}\n"
                f"📊 <b>Rejim:</b> {price_type}\n━━━━━━━━━━━━━━━━━━━\n"
                f"📦 <b>Tovarlar:</b>\n{items_text}━━━━━━━━━━━━━━━━━━━\n"
                f"💰 <b>Summa:</b> <b>{total_sum:,} so'm</b> ({total_qty} ta)\n\n"
                f"<tg-spoiler>ORD_DATA:{b64_str}</tg-spoiler>"
            )
            bot.send_message(ADMIN_ID, admin_text, reply_markup=get_admin_order_markup(client_id), parse_mode="HTML")

    except Exception as e:
        print(f"Xatolik: {e}")

# ==========================================
# OMBORDA YO'Q TOVARLARNI BOSHQARISH
# ==========================================
@bot.callback_query_handler(func=lambda call: call.data.startswith('missing_menu:'))
def show_missing_menu(call):
    payload = extract_order_payload(call.message.text)
    if not payload:
        return bot.answer_callback_query(call.id, "Buyurtma topilmadi yoki eskirgan!", show_alert=True)

    client_id = payload.get('cid')
    markup = InlineKeyboardMarkup(row_width=1)
    for idx, item in enumerate(payload.get('items', [])):
        is_missing = item.get('m') == 1
        status_icon = "❌ YO'Q:" if is_missing else "✅ BOR:"
        btn_text = f"{status_icon} {item.get('n')[:24]} ({item.get('q')} ta)"
        markup.add(InlineKeyboardButton(btn_text, callback_data=f"tog:{idx}"))

    markup.add(
        InlineKeyboardButton("📤 Mijozga xabar yuborish", callback_data="send_missing"),
        InlineKeyboardButton("⬅️ Orqaga", callback_data=f"back_order:{client_id}")
    )

    b64_str = encode_order_payload(payload)
    bot.edit_message_text(
        f"⚠️ <b>Omborda qolmagan ekranlarni tanlang:</b>\n"
        f"<i>(Ustiga bossangiz holati 'YO'Q' ga o'zgaradi)</i>\n\n"
        f"<tg-spoiler>ORD_DATA:{b64_str}</tg-spoiler>",
        call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('tog:'))
def toggle_order_item(call):
    idx = int(call.data.split(':')[1])
    payload = extract_order_payload(call.message.text)
    if not payload or idx >= len(payload.get('items', [])):
        return bot.answer_callback_query(call.id, "Xatolik yuz berdi!")

    current_m = payload['items'][idx].get('m', 0)
    payload['items'][idx]['m'] = 0 if current_m == 1 else 1

    client_id = payload.get('cid')
    markup = InlineKeyboardMarkup(row_width=1)
    for i, item in enumerate(payload.get('items', [])):
        is_missing = item.get('m') == 1
        status_icon = "❌ YO'Q:" if is_missing else "✅ BOR:"
        btn_text = f"{status_icon} {item.get('n')[:24]} ({item.get('q')} ta)"
        markup.add(InlineKeyboardButton(btn_text, callback_data=f"tog:{i}"))

    markup.add(
        InlineKeyboardButton("📤 Mijozga xabar yuborish", callback_data="send_missing"),
        InlineKeyboardButton("⬅️ Orqaga", callback_data=f"back_order:{client_id}")
    )

    new_b64 = encode_order_payload(payload)
    bot.edit_message_text(
        f"⚠️ <b>Omborda qolmagan ekranlarni tanlang:</b>\n"
        f"<i>(Ustiga bossangiz holati 'YO'Q' ga o'zgaradi)</i>\n\n"
        f"<tg-spoiler>ORD_DATA:{new_b64}</tg-spoiler>",
        call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML"
    )
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('back_order:'))
def back_to_order(call):
    payload = extract_order_payload(call.message.text)
    if not payload:
        return bot.answer_callback_query(call.id, "Buyurtma topilmadi!")

    client_id = payload.get('cid')
    items_text = ""
    total_sum = 0
    total_qty = 0
    for idx, it in enumerate(payload.get('items', []), 1):
        items_text += f"{idx}. <b>{it.get('n')}</b>\n   └ {it.get('q')} dona × {it.get('p'):,} = <b>{it.get('s'):,} so'm</b>\n"
        total_sum += it.get('s', 0)
        total_qty += it.get('q', 0)

    b64_str = encode_order_payload(payload)
    text = (
        f"🔔 <b>BUYURTMA: {payload.get('name')}</b>\n━━━━━━━━━━━━━━━━━━━\n"
        f"📞 <b>Raqam:</b> {payload.get('phone')}\n"
        f"🚚 <b>Yetkazish:</b> {payload.get('deliv')} | 📍 {payload.get('addr')}\n"
        f"📊 <b>Rejim:</b> {payload.get('pt')}\n━━━━━━━━━━━━━━━━━━━\n"
        f"📦 <b>Tovarlar:</b>\n{items_text}━━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>Summa:</b> <b>{total_sum:,} so'm</b> ({total_qty} ta)\n\n"
        f"<tg-spoiler>ORD_DATA:{b64_str}</tg-spoiler>"
    )
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=get_admin_order_markup(client_id), parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == 'send_missing')
def send_missing_notice_to_client(call):
    payload = extract_order_payload(call.message.text)
    if not payload:
        return bot.answer_callback_query(call.id, "Buyurtma topilmadi!")

    client_id = payload.get('cid')
    missing_items = [it for it in payload.get('items', []) if it.get('m') == 1]
    available_items = [it for it in payload.get('items', []) if it.get('m') == 0]

    if not missing_items:
        return bot.answer_callback_query(call.id, "Hech qaysi tovar 'YO'Q' deb belgilanmadi!", show_alert=True)

    new_total_sum = sum(it.get('s', 0) for it in available_items)
    new_total_qty = sum(it.get('q', 0) for it in available_items)

    missing_text = ""
    for it in missing_items:
        missing_text += f"❌ <b>{it.get('n')}</b> — {it.get('q')} dona (Mavjud emas)\n"

    avail_text = ""
    for idx, it in enumerate(available_items, 1):
        avail_text += f"{idx}. <b>{it.get('n')}</b> — {it.get('q')} dona ({it.get('s'):,} so'm)\n"

    client_msg = (
        f"⚠️ <b>DIQQAT: BUYURTMANING AYRIM MODELLARI OMBORDA YO'Q!</b>\n━━━━━━━━━━━━━━━━━━━\n"
        f"Quyidagi ekranlar hozirda do'konda qolmagan (<b>boshqa yerdan olib turishingiz mumkin</b>):\n\n"
        f"{missing_text}\n"
        f"✅ <b>Omborda bor va chiqariladigan tovarlar:</b>\n\n"
        f"{avail_text if avail_text else '<i>Bor tovar qolmadi</i>'}\n━━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>Qayta hisoblangan to'lov:</b> <b>{new_total_sum:,} so'm</b> ({new_total_qty} ta)\n"
        f"💳 Karta raqami: <code>{CARD_NUMBER}</code>\n\n"
        f"Mavjud tovarlarni chiqarishimiz uchun to'lov qilib chekni yuboring yoki admin bilan bog'laning!"
    )

    client_markup = InlineKeyboardMarkup()
    client_markup.add(InlineKeyboardButton("💬 Admin bilan bog'lanish", url=f"tg://user?id={ADMIN_ID}"))
    bot.send_message(int(client_id), client_msg, reply_markup=client_markup, parse_mode="HTML")

    new_b64 = encode_order_payload(payload)
    bot.edit_message_text(
        f"✅ <b>Mijozga yo'q tovarlar haqida xabar ketdi!</b>\n\n"
        f"💰 Qayta hisoblangan summa: <b>{new_total_sum:,} so'm</b> ({new_total_qty} ta)\n"
        f"Mijozdan yangi summa bo'yicha to'lov kutilmoqda.\n\n"
        f"<tg-spoiler>ORD_DATA:{new_b64}</tg-spoiler>",
        call.message.chat.id, call.message.message_id, reply_markup=get_admin_order_markup(client_id), parse_mode="HTML"
    )
    bot.answer_callback_query(call.id, "Mijozga xabarnoma yuborildi!")

# ==========================================
# TO'LOV CHEKINI QABUL QILISH
# ==========================================
@bot.message_handler(content_types=['photo'])
def handle_payment_receipt(message):
    client_id = str(message.chat.id)
    user_phones = load_data(USERS_FILE)
    phone = user_phones.get(client_id, "Ko'rsatilmagan")
    name = message.from_user.first_name or "Mijoz"
    username = f"@{message.from_user.username}" if message.from_user.username else "Mavjud emas"

    photo_id = message.photo[-1].file_id
    admin_markup = InlineKeyboardMarkup(row_width=2)
    admin_markup.add(
        InlineKeyboardButton("✅ Pul tushdi (Bugun yetkazish)", callback_data=f"pay:{client_id}:today"),
        InlineKeyboardButton("✅ Pul tushdi (Ertaga yetkazish)", callback_data=f"pay:{client_id}:tomorrow"),
        InlineKeyboardButton("❌ Pul tushmadi (Chek soxta)", callback_data=f"pay:{client_id}:fake")
    )

    caption_text = (
        f"🧾 <b>TO'LOV CHEKI KELIB TUSHDI!</b>\n━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Mijoz:</b> {name} ({username})\n"
        f"📞 <b>Telefon:</b> {phone}\n"
        f"🆔 <b>ID:</b> <code>{client_id}</code>\n━━━━━━━━━━━━━━━━━━━\n"
        f"Kartangizni tekshirib, qarorni tanlang:"
    )
    bot.send_photo(ADMIN_ID, photo_id, caption=caption_text, reply_markup=admin_markup, parse_mode="HTML")
    bot.reply_to(message, "✅ <b>To'lov chekingiz qabul qilindi!</b> Admin tekshirib buyurtmangizni tasdiqlaydi.", parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith('pay:'))
def process_payment_decision(call):
    try:
        _, client_id, action = call.data.split(':')
        client_id_int = int(client_id)

        responses = {
            "today": "🎉 <b>To'lovingiz tasdiqlandi!</b>\nBuyurtmangiz <b>BUGUN</b> yetkazib beriladi.",
            "tomorrow": "🎉 <b>To'lovingiz tasdiqlandi!</b>\nBuyurtmangiz <b>ERTAGA</b> yetkazib beriladi.",
            "cash": "🤝 <b>Buyurtmangiz tasdiqlandi!</b>\nTo'lov naqd qabul qilinadi.",
            "fake": "⚠️ <b>DIQQAT: Kartaga pul tushmadi!</b>\nIltimos, chekni qayta tekshirib admin bilan bog'laning.",
            "cancel": "❌ <b>Buyurtmangiz bekor qilindi.</b>"
        }

        bot.send_message(client_id_int, f"🔔 <b>Ekranchi xabarnomasi:</b>\n\n{responses.get(action)}", parse_mode="HTML")
        bot.answer_callback_query(call.id, "Mijozga xabar ketdi!")
        try:
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        except:
            pass
    except Exception as e:
        print(f"Qaror xatosi: {e}")

# ==========================================
# VERCEL WEBHOOK
# ==========================================
@app.route('/', defaults={'path': ''}, methods=['POST', 'GET'])
@app.route('/<path:path>', methods=['POST', 'GET'])
def webhook(path):
    if request.method == 'GET':
        return "Ekranchi Bot 24/7 Vercel serverida ishlamoqda!", 200
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return jsonify({"status": "ok"}), 200
    return "Forbidden", 403
