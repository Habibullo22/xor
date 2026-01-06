from keep_alive import keep_alive
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

keep_alive()

API_TOKEN = "PASTE_NEW_TOKEN_HERE"
ADMIN_ID = 5815294733
CARD_NUMBER = "9860 6067 5024 7151"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

users = {}
pending = {}

# ===== KEYBOARDS =====
main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add(
    KeyboardButton("💳 Hisob to‘ldirish"),
    KeyboardButton("💸 Mablag‘ chiqarish")
)
main_kb.add(KeyboardButton("📊 Balans"))

paid_kb = ReplyKeyboardMarkup(resize_keyboard=True)
paid_kb.add(KeyboardButton("✅ To‘lov qildim"))
paid_kb.add(KeyboardButton("⬅️ Ortga"))

admin_confirm_kb = InlineKeyboardMarkup()
admin_confirm_kb.add(
    InlineKeyboardButton("✅ Tasdiqlash", callback_data="confirm"),
    InlineKeyboardButton("❌ Rad etish", callback_data="reject")
)

# ===== START =====
@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    users[msg.from_user.id] = {
        "balance": 0,
        "step": None
    }
    await msg.answer(
        "🎉 Xush kelibsiz!\n"
        "Siz *BIG WIN* botidasiz 🎰",
        parse_mode="Markdown",
        reply_markup=main_kb
    )

# ===== HISOB TOLDIRISH =====
@dp.message_handler(text="💳 Hisob to‘ldirish")
async def deposit(msg: types.Message):
    users[msg.from_user.id]["step"] = "amount"
    await msg.answer("💰 Qancha pul kiritmoqchisiz?")

@dp.message_handler(lambda m: users.get(m.from_user.id, {}).get("step") == "amount")
async def get_amount(msg: types.Message):
    if not msg.text.isdigit():
        return await msg.answer("❌ Faqat raqam kiriting")

    users[msg.from_user.id]["amount"] = int(msg.text)
    users[msg.from_user.id]["step"] = "username"
    await msg.answer("🆔 O‘yin ichidagi ID yoki ismingizni yozing")

@dp.message_handler(lambda m: users.get(m.from_user.id, {}).get("step") == "username")
async def get_username(msg: types.Message):
    users[msg.from_user.id]["username"] = msg.text
    users[msg.from_user.id]["step"] = "waiting_payment"

    await msg.answer(
        f"✅ Qabul qilindi\n\n"
        f"💳 KARTA:\n"
        f"`{CARD_NUMBER}`\n"
        f"👤 BIG WIN\n\n"
        f"Pulni o‘tkazib bo‘lgach tugmani bosing 👇",
        parse_mode="Markdown",
        reply_markup=paid_kb
    )

# ===== TOLOV QILDIM TUGMASI =====
@dp.message_handler(text="✅ To‘lov qildim")
async def paid(msg: types.Message):
    users[msg.from_user.id]["step"] = "send_check"
    await msg.answer("📸 Iltimos, CHEK RASMINI yuboring")

# ===== CHEK QABUL =====
@dp.message_handler(content_types=types.ContentType.PHOTO)
async def get_check(msg: types.Message):
    if users.get(msg.from_user.id, {}).get("step") != "send_check":
        return

    pending[msg.from_user.id] = users[msg.from_user.id]

    await bot.send_photo(
        ADMIN_ID,
        msg.photo[-1].file_id,
        caption=(
            "💰 YANGI TO‘LOV\n\n"
            f"👤 User: @{msg.from_user.username}\n"
            f"🆔 ID: {msg.from_user.id}\n"
            f"💵 Summa: {users[msg.from_user.id]['amount']} so‘m\n"
            f"🎮 Ism: {users[msg.from_user.id]['username']}"
        ),
        reply_markup=admin_confirm_kb
    )

    await msg.answer("⏳ To‘lov tekshirilmoqda...")

# ===== ADMIN TASDIQLASH =====
@dp.callback_query_handler(lambda c: c.data in ["confirm", "reject"])
async def admin_action(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return

    user_id = list(pending.keys())[0]

    if call.data == "confirm":
        users[user_id]["balance"] += pending[user_id]["amount"]
        await bot.send_message(user_id, "✅ Hisobingizga pul tushdi")
    else:
        await bot.send_message(user_id, "❌ To‘lov rad etildi")

    pending.pop(user_id)
    await call.answer("Bajarildi")

# ===== BALANS =====
@dp.message_handler(text="📊 Balans")
async def balance(msg: types.Message):
    await msg.answer(f"💰 Balansingiz: {users[msg.from_user.id]['balance']} so‘m")

# ===== MABLAG CHIQARISH =====
@dp.message_handler(text="💸 Mablag‘ chiqarish")
async def withdraw(msg: types.Message):
    await msg.answer("💸 Qancha pul yechmoqchisiz?")

@dp.message_handler(lambda m: m.text.isdigit())
async def deny_withdraw(msg: types.Message):
    await msg.answer("❌ Balansingizda yetarli mablag‘ yo‘q")

# ===== ADMIN PANEL =====
@dp.message_handler(commands=["admin"])
async def admin_panel(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return
    await msg.answer(
        "🛠 ADMIN PANEL\n\n"
        "📢 Reklama\n"
        "💰 To‘lovlar\n"
        "👥 Foydalanuvchilar"
    )

if __name__ == "__main__":
    executor.start_polling(dp)
