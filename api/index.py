from flask import Flask, request
import telebot
from telebot.types import (
    Update, 
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    WebAppInfo, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)
import json
import os

BOT_TOKEN = "8484579263:AAGZu38VEXN4Hx5Yup12JoZnBZa1TlCDVy0"
ADMIN_ID = 1758833704
WEB_APP_URL = "https://bekzodmatkarimov7770-cyber.github.io/Ekranchi-shop/market.html?v=sale202"
CARD_NUMBER = "9860 1266 0304 4796"
CARD_NAME = "Bekzod M. (Humo / Uzcard)"

USERS_FILE = "/tmp/users.json"
ORDERS_FILE = "/tmp/orders.json"

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)

def load_json(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_json(filepath, data):
    try:
        with open(filepath, "w") as f:
            json.dump(data, f)
    except:
        pass

def get_store_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(text="🛍 Do'konni ochish", web_app=WebAppInfo(url=WEB_APP_URL)))
    return markup

def get_contact_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton(text="📱 Telefon raqamimni yuborish", request_contact=True))
    return markup

@bot.message_handler(commands=['start'])
def start_command(message):
    user_phones = load_json(USERS_FILE)
    user_id = str(message.chat.id)
    user_name = message.from_user.first_name or "Mijoz"

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
        user_phones = load_json(USERS_FILE)
        user_phones[str(message.chat.id)] = phone
        save_json(USERS_FILE, user_phones)

        bot.send_message(
            message.chat.id,
            f"✅ <b>Raqamingiz tasdiqlandi:</b> {phone}\n\nDo'kondan bemalol buyurtma berishingiz mumkin!",
            reply_markup=get_store_keyboard(),
            parse_mode="HTML"
        )
    else:
        bot.send_message(
            message.chat.id,
            "⚠️ <b>Xatolik:</b> Faqat o'zingizning shaxsiy raqamingizni pastdagi tugma orqali yuboring!",
            reply_markup=get_contact_keyboard(),
            parse_mode="HTML"
        )

@bot.message_handler(content_types=['web_app_data'])
def handle_order(message):
    try:
        raw = message.web_app_data.data
        data = json.loads(raw)
        client_id = str(message.chat.id)

        user_orders = load_json(ORDERS_FILE)
        user_orders[client_id] = data
        save_json(ORDERS_FILE, user_orders)

        user_phones = load_json(USERS_FILE)
        verified_phone = user_phones.get(client_id, "Telegram orqali tasdiqlangan")
        name = data.get('name', 'Noma\'lum')
        delivery = data.get('delivery', 'Noma\'lum')
        address = data.get('address', 'Noma\'lum')
        total_sum = data.get('total_sum', 0)
        items = data.get('items', [])
        user_username = f"@{message.from_user.username}" if message.from_user.username else "Mavjud emas"

        items_text = ""
        for idx, item in enumerate(items, 1):
            items_text += f"{idx}. <b>{item.get('name')} ({item.get('type')})</b>\n   └ {item.get('qty')} dona × {item.get('price'):,} = <b>{item.get('subtotal'):,} so'm</b>\n"

        # Mijozga to'lov talabi
        client_markup = InlineKeyboardMarkup()
        client_markup.add(InlineKeyboardButton("💬 Admin bilan bog'lanish (Naqd to'lov)", url=f"tg://user?id={ADMIN_ID}"))

        client_text = (
            f"🛒 <b>Buyurtmangiz rasmiylashtirildi!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>Qabul qiluvchi:</b> {name}\n"
            f"📞 <b>Telefon:</b> {verified_phone}\n"
            f"🚚 <b>Yetkazish:</b> {delivery} | 📍 {address}\n"
            f"📦 <b>Buyurtma:</b>\n{items_text}"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"💰 <b>JAMI TO'LOV SUMMASI:</b> <b>{total_sum:,} so'm</b>\n"
            f"━━━━━━━━━━━━━━━━━━━\n\n"
            f"⚠️ <b>DIQQAT: BUYURTMANI YETKAZISH SHARTI:</b>\n"
            f"Buyurtmangiz yo'lga chiqishi uchun to'lov qilinishi shart!\n\n"
            f"💳 <b>Karta raqami:</b> <code>{CARD_NUMBER}</code>\n"
            f"Qabul qiluvchi: <b>{CARD_NAME}</b>\n"
            f"<i>(Raqam ustiga bossangiz avtomatik nusxalanadi)</i>\n\n"
            f"📸 <b>To'lov qilgach:</b> Chek rasmini shu yerga <b>rasm qilib yuboring!</b>\n\n"
            f"💵 <b>Naqd pulda to'lamoqchi bo'lsangiz:</b>\n"
            f"Pastdagi tugma orqali admin bilan bog'laning."
        )
        bot.send_message(int(client_id), client_text, reply_markup=client_markup, parse_mode="HTML")

        # Adminga bildirishnoma
        admin_markup = InlineKeyboardMarkup(row_width=2)
        admin_markup.add(
            InlineKeyboardButton("💵 Naqd kelishildi", callback_data=f"pay:{client_id}:cash"),
            InlineKeyboardButton("⚡️ Bugun yetkazish", callback_data=f"pay:{client_id}:today"),
            InlineKeyboardButton("📦 Ertaga yetkazish", callback_data=f"pay:{client_id}:tomorrow"),
            InlineKeyboardButton("❌ Bekor qilish", callback_data=f"pay:{client_id}:cancel")
        )
        admin_text = (
            f"🔔 <b>YANGI BUYURTMA TUSHDI (TO'LOV KUTILMOQDA)!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>Mijoz:</b> {name}\n"
            f"✈️ <b>Telegram:</b> {user_username}\n"
            f"📞 <b>Telefon:</b> <b>{verified_phone}</b>\n"
            f"🚚 <b>Yetkazish:</b> {delivery} | 📍 {address}\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"📦 <b>Tovarlar:</b>\n{items_text}"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"💰 <b>Summa:</b> <b>{total_sum:,} so'm</b>\n"
            f"📊 <b>Holat:</b> ⏳ To'lov kutilmoqda..."
        )
        bot.send_message(ADMIN_ID, admin_text, reply_markup=admin_markup, parse_mode="HTML")

    except Exception as e:
        bot.send_message(message.chat.id, f"Xatolik: {e}")

@bot.message_handler(content_types=['photo'])
def handle_payment_receipt(message):
    client_id = str(message.chat.id)
    name = message.from_user.first_name or "Mijoz"
    username = f"@{message.from_user.username}" if message.from_user.username else "Mavjud emas"
    photo_id = message.photo[-1].file_id

    user_orders = load_json(ORDERS_FILE)
    order = user_orders.get(client_id, {})
    total_sum = order.get('total_sum', "Noma'lum")

    admin_markup = InlineKeyboardMarkup(row_width=2)
    admin_markup.add(
        InlineKeyboardButton("✅ Pul tushdi (Bugun yetkazish)", callback_data=f"pay:{client_id}:today"),
        InlineKeyboardButton("✅ Pul tushdi (Ertaga yetkazish)", callback_data=f"pay:{client_id}:tomorrow"),
        InlineKeyboardButton("❌ Pul tushmadi (Chek soxta)", callback_data=f"pay:{client_id}:fake")
    )

    caption_text = (
        f"🧾 <b>TO'LOV CHEKI KELIB TUSHDI!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Mijoz:</b> {name} ({username})\n"
        f"💰 <b>Kutilayotgan summa:</b> {total_sum:,} so'm\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"Iltimos, kartangizni tekshirib, quyidagi tugmani bosing:"
    )

    bot.send_photo(ADMIN_ID, photo_id, caption=caption_text, reply_markup=admin_markup, parse_mode="HTML")
    bot.reply_to(message, "✅ <b>To'lov chekingiz adminga yetkazildi!</b>\n\nAdmin tekshirib, bir necha daqiqada tasdiqlaydi.", parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith('pay:'))
def process_payment_decision(call):
    try:
        _, client_id, action = call.data.split(':')
        client_id_int = int(client_id)

        responses = {
            "today": "🎉 <b>To'lovingiz tasdiqlandi!</b>\n\nMahsulotlaringiz <b>BUGUN</b> yetkazib beriladi.",
            "tomorrow": "🎉 <b>To'lovingiz tasdiqlandi!</b>\n\nMahsulotlaringiz <b>ERTAGA</b> yetkazib beriladi.",
            "cash": "🤝 <b>Buyurtmangiz admin tomonidan tasdiqlandi!</b>\n\nTo'lov naqd shaklda qabul qilinadi.",
            "fake": "⚠️ <b>DIQQAT: To'lov hisobga kelib tushmadi!</b>\n\nIltimos, qayta tekshiring yoki admin bilan bog'laning.",
            "cancel": "❌ <b>Buyurtmangiz bekor qilindi.</b>"
        }

        bot.send_message(client_id_int, f"🔔 <b>Ekranchi xabarnomasi:</b>\n\n{responses.get(action)}", parse_mode="HTML")
        bot.answer_callback_query(call.id, "Mijozga xabar yuborildi!")
        try:
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        except:
            pass
    except Exception as e:
        bot.answer_callback_query(call.id, f"Xatolik: {e}")

# Vercel Webhook yo'lagi:
@app.route('/api/index', methods=['POST'])
@app.route('/', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    return 'Forbidden', 403

@app.route('/', methods=['GET'])
def home():
    return "Ekranchi boti Vercel serverida 24/7 ishlab turibdi!", 200
