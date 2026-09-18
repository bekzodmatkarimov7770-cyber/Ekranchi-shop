from flask import Flask, request, jsonify
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
import json
import os

BOT_TOKEN = "8484579263:AAGZu38VEXN4Hx5Yup12JoZnBZa1TlCDVy0"
WEB_APP_URL = "https://bekzodmatkarimov7770-cyber.github.io/Ekranchi-shop/market.html?v=redmi_new_95"
ADMIN_ID = 1758833704

CARD_NUMBER = "9860 1266 0304 4796"
CARD_NAME = "Bekzod M. (Humo / Uzcard)"

# Vercel serverida faqat /tmp papkasiga yozishga ruxsat berilgan
USERS_FILE = "/tmp/users.json"
ORDERS_FILE = "/tmp/orders.json"

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
        print(f"Xotiraga yozishda xatolik: {e}")

user_phones = load_data(USERS_FILE)
user_orders = load_data(ORDERS_FILE)

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)

def get_store_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(text="🛍 Do'konni ochish", web_app=WebAppInfo(url=WEB_APP_URL)))
    return markup

def get_contact_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn_phone = KeyboardButton(text="📱 Telefon raqamimni yuborish", request_contact=True)
    markup.add(btn_phone)
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

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = str(message.chat.id)
    user_name = message.from_user.first_name or "Mijoz"
    user_phones = load_data(USERS_FILE)
    
    if user_id in user_phones:
        bot.send_message(
            message.chat.id,
            f"Assalomu alaykum, {user_name}!\n\n"
            f"🛠 <b>Ekranchi</b> do'koniga xush kelibsiz.\n\n"
            f"Pastdagi <b>«🛍 Do'konni ochish»</b> tugmasi orqali katalogga kiring!",
            reply_markup=get_store_keyboard(),
            parse_mode="HTML"
        )
    else:
        bot.send_message(
            message.chat.id,
            f"Assalomu alaykum, {user_name}!\n\n"
            f"🛠 <b>Ekranchi</b> do'koniga xush kelibsiz.\n\n"
            f"⚠️ Soxta buyurtmalarning oldini olish uchun pastdagi "
            f"<b>«📱 Telefon raqamimni yuborish»</b> tugmasini bosing:",
            reply_markup=get_contact_keyboard(),
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
            f"✅ <b>Raqamingiz tasdiqlandi:</b> {phone}\n\nDo'kondan bemalol buyurtma berishingiz mumkin!",
            reply_markup=get_store_keyboard(),
            parse_mode="HTML"
        )
    else:
        bot.send_message(
            message.chat.id,
            "⚠️ Faqat pastdagi tugma orqali o'z raqamingizni yuboring!",
            reply_markup=get_contact_keyboard(),
            parse_mode="HTML"
        )

@bot.message_handler(content_types=['web_app_data'])
def handle_order(message):
    try:
        raw = message.web_app_data.data
        data = json.loads(raw)
        client_id = str(message.chat.id)
        
        for item in data.get('items', []):
            item['is_missing'] = False

        user_orders = load_data(ORDERS_FILE)
        user_orders[client_id] = data
        save_data(ORDERS_FILE, user_orders)

        user_phones = load_data(USERS_FILE)
        verified_phone = user_phones.get(client_id, "Tasdiqlanmagan")
        name = data.get('name', 'Noma\'lum')
        delivery = data.get('delivery', 'Noma\'lum')
        address = data.get('address', 'Noma\'lum')
        total_qty = data.get('total_qty', 0)
        total_sum = data.get('total_sum', 0)
        items = data.get('items', [])
        user_username = f"@{message.from_user.username}" if message.from_user.username else "Mavjud emas"

        items_text = ""
        for idx, item in enumerate(items, 1):
            items_text += f"{idx}. <b>{item.get('name')}</b>\n   └ {item.get('qty')} dona × {item.get('price'):,} = <b>{item.get('subtotal'):,} so'm</b>\n"

        client_markup = InlineKeyboardMarkup()
        client_markup.add(InlineKeyboardButton("💬 Admin bilan bog'lanish (Naqd to'lov)", url=f"tg://user?id={ADMIN_ID}"))

        client_text = (
            f"🛒 <b>Buyurtmangiz rasmiylashtirildi!</b>\n━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>Qabul qiluvchi:</b> {name}\n📞 <b>Telefon:</b> {verified_phone}\n"
            f"🚚 <b>Yetkazish:</b> {delivery} | 📍 {address}\n"
            f"📦 <b>Buyurtma tarkibi:</b>\n{items_text}━━━━━━━━━━━━━━━━━━━\n"
            f"💰 <b>JAMI TO'LOV:</b> <b>{total_sum:,} so'm</b>\n\n"
            f"⚠️ <b>TO'LOV TALABI:</b>\n"
            f"Yetkazish boshlanishi uchun to'lov qilinishi shart!\n\n"
            f"💳 Karta raqami: <code>{CARD_NUMBER}</code>\n"
            f"Qabul qiluvchi: <b>{CARD_NAME}</b>\n\n"
            f"📸 <b>Karta orqali to'lasangiz:</b> Chek skrinshotini shu yerga rasm qilib yuboring.\n"
            f"💵 <b>Naqd to'lamoqchi bo'lsangiz:</b> Pastdagi tugma orqali admin bilan kelishing."
        )
        bot.send_message(int(client_id), client_text, reply_markup=client_markup, parse_mode="HTML")

        if ADMIN_ID:
            admin_text = (
                f"🔔 <b>YANGI BUYURTMA TUSHDI!</b>\n━━━━━━━━━━━━━━━━━━━\n"
                f"👤 <b>Mijoz:</b> {name} ({user_username})\n📞 <b>Raqam:</b> {verified_phone}\n"
                f"🚚 <b>Yetkazish:</b> {delivery} | 📍 {address}\n━━━━━━━━━━━━━━━━━━━\n"
                f"📦 <b>Tovarlar:</b>\n{items_text}━━━━━━━━━━━━━━━━━━━\n"
                f"💰 <b>Summa:</b> <b>{total_sum:,} so'm</b> ({total_qty} ta)"
            )
            bot.send_message(ADMIN_ID, admin_text, reply_markup=get_admin_order_markup(client_id), parse_mode="HTML")

    except Exception as e:
        print(f"Buyurtma xatoligi: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('missing_menu:'))
def show_missing_menu(call):
    client_id = call.data.split(':')[1]
    user_orders = load_data(ORDERS_FILE)
    order = user_orders.get(client_id)
    if not order:
        return bot.answer_callback_query(call.id, "Buyurtma topilmadi!")

    markup = InlineKeyboardMarkup(row_width=1)
    for idx, item in enumerate(order.get('items', [])):
        status_icon = "❌ YO'Q:" if item.get('is_missing') else "✅ BOR:"
        btn_text = f"{status_icon} {item.get('name')[:25]} ({item.get('qty')} ta)"
        markup.add(InlineKeyboardButton(btn_text, callback_data=f"toggle_item:{client_id}:{idx}"))

    markup.add(
        InlineKeyboardButton("📤 Mijozga xabar yuborish", callback_data=f"send_missing:{client_id}"),
        InlineKeyboardButton("⬅️ Orqaga", callback_data=f"back_order:{client_id}")
    )

    bot.edit_message_text(
        "⚠️ <b>Omborda qolmagan ekranlarni tanlang:</b>\n<i>(Ustiga bossangiz holati 'YO'Q' ga o'zgaradi)</i>",
        call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('toggle_item:'))
def toggle_order_item(call):
    _, client_id, idx_str = call.data.split(':')
    idx = int(idx_str)
    user_orders = load_data(ORDERS_FILE)
    order = user_orders.get(client_id)
    if not order or idx >= len(order.get('items', [])):
        return bot.answer_callback_query(call.id, "Xatolik yuz berdi!")

    order['items'][idx]['is_missing'] = not order['items'][idx].get('is_missing', False)
    save_data(ORDERS_FILE, user_orders)
    show_missing_menu(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith('back_order:'))
def back_to_order(call):
    client_id = call.data.split(':')[1]
    user_orders = load_data(ORDERS_FILE)
    order = user_orders.get(client_id)
    if not order:
        return bot.answer_callback_query(call.id, "Buyurtma topilmadi!")

    items_text = ""
    for idx, item in enumerate(order.get('items', []), 1):
        items_text += f"{idx}. <b>{item.get('name')}</b> ({item.get('qty')} ta)\n"

    user_phones = load_data(USERS_FILE)
    text = (
        f"🔔 <b>BUYURTMA: {order.get('name')}</b>\n"
        f"📞 <b>Raqam:</b> {user_phones.get(client_id, '')}\n"
        f"📦 <b>Tovarlar:</b>\n{items_text}\n"
        f"💰 <b>Summa:</b> {order.get('total_sum', 0):,} so'm"
    )
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=get_admin_order_markup(client_id), parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith('send_missing:'))
def send_missing_notice_to_client(call):
    client_id = call.data.split(':')[1]
    user_orders = load_data(ORDERS_FILE)
    order = user_orders.get(client_id)
    if not order:
        return bot.answer_callback_query(call.id, "Buyurtma topilmadi!")

    missing_items = [it for it in order.get('items', []) if it.get('is_missing')]
    available_items = [it for it in order.get('items', []) if not it.get('is_missing')]

    if not missing_items:
        return bot.answer_callback_query(call.id, "Hech qaysi tovar 'YO'Q' qilinmadi!")

    new_total_sum = sum(it.get('subtotal', 0) for it in available_items)
    new_total_qty = sum(it.get('qty', 0) for it in available_items)
    order['total_sum'] = new_total_sum
    order['total_qty'] = new_total_qty
    save_data(ORDERS_FILE, user_orders)

    missing_text = ""
    for it in missing_items:
        missing_text += f"❌ <b>{it.get('name')}</b> — {it.get('qty')} dona (Mavjud emas)\n"

    avail_text = ""
    for idx, it in enumerate(available_items, 1):
        avail_text += f"{idx}. <b>{it.get('name')}</b> — {it.get('qty')} dona ({it.get('subtotal'):,} so'm)\n"

    client_msg = (
        f"⚠️ <b>DIQQAT: BUYURTMANING AYRIM MODELLARI OMBORDA YO'Q!</b>\n━━━━━━━━━━━━━━━━━━━\n"
        f"Quyidagi ekranlar hozirda do'konimizda qolmagan (<b>boshqa yerdan olib turishingiz mumkin</b>):\n\n"
        f"{missing_text}━━━━━━━━━━━━━━━━━━━\n"
        f"✅ <b>Omborda bor va chiqariladigan tovarlar:</b>\n\n"
        f"{avail_text if avail_text else '<i>Bor tovar qolmadi</i>'}━━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>Qayta hisoblangan to'lov:</b> <b>{new_total_sum:,} so'm</b> ({new_total_qty} ta)\n"
        f"💳 Karta: <code>{CARD_NUMBER}</code>\n\n"
        f"Mavjud tovarlarni chiqarishimiz uchun to'lov qilib chekni yuboring yoki admin bilan bog'laning!"
    )

    client_markup = InlineKeyboardMarkup()
    client_markup.add(InlineKeyboardButton("💬 Admin bilan bog'lanish", url=f"tg://user?id={ADMIN_ID}"))
    bot.send_message(int(client_id), client_msg, reply_markup=client_markup, parse_mode="HTML")

    bot.answer_callback_query(call.id, "Mijozga xabar yuborildi!")
    bot.edit_message_text(
        f"✅ <b>Mijozga yo'q tovarlar haqida xabar ketdi!</b>\n\n"
        f"Yangi hisoblangan summa: <b>{new_total_sum:,} so'm</b>",
        call.message.chat.id, call.message.message_id, reply_markup=get_admin_order_markup(client_id), parse_mode="HTML"
    )

@bot.message_handler(content_types=['photo'])
def handle_payment_receipt(message):
    client_id = str(message.chat.id)
    user_orders = load_data(ORDERS_FILE)
    if client_id in user_orders:
        order = user_orders[client_id]
        user_phones = load_data(USERS_FILE)
        phone = user_phones.get(client_id, "Noma'lum")
        name = order.get('name', 'Mijoz')
        total_sum = order.get('total_sum', 0)

        photo_id = message.photo[-1].file_id
        admin_markup = InlineKeyboardMarkup(row_width=2)
        admin_markup.add(
            InlineKeyboardButton("✅ Pul tushdi (Bugun yetkazish)", callback_data=f"pay:{client_id}:today"),
            InlineKeyboardButton("✅ Pul tushdi (Ertaga yetkazish)", callback_data=f"pay:{client_id}:tomorrow"),
            InlineKeyboardButton("❌ Pul tushmadi (Chek soxta)", callback_data=f"pay:{client_id}:fake")
        )

        caption_text = (
            f"🧾 <b>TO'LOV CHEKI KELDI!</b>\n━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>Mijoz:</b> {name}\n📞 <b>Telefon:</b> {phone}\n"
            f"💰 <b>Kutilayotgan summa:</b> {total_sum:,} so'm\n━━━━━━━━━━━━━━━━━━━\n"
            f"Hisobni tekshirib tugmani bosing:"
        )
        bot.send_photo(ADMIN_ID, photo_id, caption=caption_text, reply_markup=admin_markup, parse_mode="HTML")
        bot.reply_to(message, "✅ <b>To'lov chekingiz qabul qilindi!</b> Admin tekshirib buyurtmangizni tasdiqlaydi.", parse_mode="HTML")
    else:
        bot.reply_to(message, "Faol buyurtma topilmadi.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('pay:'))
def process_payment_decision(call):
    try:
        _, client_id, action = call.data.split(':')
        client_id_int = int(client_id)

        responses = {
            "today": "🎉 <b>To'lovingiz tasdiqlandi!</b>\nBuyurtmangiz <b>BUGUN</b> yetkazib beriladi.",
            "tomorrow": "🎉 <b>To'lovingiz tasdiqlandi!</b>\nBuyurtmangiz <b>ERTAGA</b> yetkazib beriladi.",
            "cash": "🤝 <b>Buyurtmangiz tasdiqlandi!</b>\nTo'lov naqd qabul qilinadi.",
            "fake": "⚠️ <b>DIQQAT: Kartaga pul tushmadi!</b>\nIltimos, qayta tekshirib admin bilan bog'laning.",
            "cancel": "❌ <b>Buyurtmangiz bekor qilindi.</b>"
        }

        bot.send_message(client_id_int, f"🔔 <b>Ekranchi xabarnomasi:</b>\n\n{responses.get(action)}", parse_mode="HTML")
        bot.answer_callback_query(call.id, "Mijozga xabarnoma ketdi!")
        try:
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        except:
            pass

        if action in ["today", "tomorrow", "cash", "cancel"]:
            user_orders = load_data(ORDERS_FILE)
            if client_id in user_orders:
                del user_orders[client_id]
                save_data(ORDERS_FILE, user_orders)
    except Exception as e:
        print(f"Status xatosi: {e}")

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
