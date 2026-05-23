import json
import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    CommandHandler,
    filters,
)

TOKEN = "8675542982:AAGXmLUqjQ1lIsAFPvqy32ZwpCWVSFtZ4bg"
ADMIN_ID = 6355551639


# =========================
# 📦 ДАННЫЕ
# =========================

users = {}
dialogs = {}
pending_answers = {}


# =========================
# 💾 СОХРАНЕНИЕ
# =========================


def save_data():
    data = {"users": users, "dialogs": dialogs}

    with open("data.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


# =========================
# 📂 ЗАГРУЗКА
# =========================


def load_data():
    global users, dialogs

    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            users = data.get("users", {})
            dialogs = data.get("dialogs", {})


# =========================
# 🚀 START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = str(update.message.from_user.id)

    # если пользователь уже есть и имя задано
    if user_id in users and "name" in users[user_id]:
        await update.message.reply_text(
            f"👋 С возвращением, {users[user_id]['name']}!\n\n"
            "Можешь задать новый вопрос 👌"
        )
        return

    # иначе спрашиваем имя
    users[user_id] = {
        "waiting_for_name": True
    }

    save_data()

    await update.message.reply_text(
        "👋 Привет!\n\nКак мне к тебе обращаться?"
    )

# =========================
# 💬 СООБЩЕНИЯ
# =========================


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user
    user_id = str(user.id)
    text = update.message.text

    # =========================
    # 👨‍💻 АДМИН ОТВЕЧАЕТ
    # =========================

    if user.id == ADMIN_ID:

        if ADMIN_ID in pending_answers:

            target_user = pending_answers[ADMIN_ID]

            await context.bot.send_message(
                chat_id=int(target_user), text=f"📬 Ответ:\n\n{text}"
            )

            dialogs[target_user].append({"type": "admin", "text": text})

            save_data()

            await update.message.reply_text("✅ Ответ отправлен")

            del pending_answers[ADMIN_ID]

        return

    # =========================
    # 👤 НОВЫЙ ПОЛЬЗОВАТЕЛЬ
    # =========================

    if user_id not in users:
        users[user_id] = {"waiting_for_name": True}
        save_data()

        await update.message.reply_text("Как мне к тебе обращаться?")
        return

    # =========================
    # 📝 ИМЯ
    # =========================

    if users[user_id].get("waiting_for_name"):
        users[user_id]["name"] = text
        users[user_id]["waiting_for_name"] = False

        save_data()

        await update.message.reply_text(
            f"Приятно познакомиться, {text} 💬\n\n" "Теперь можешь задать вопрос 👌"
        )
        return

    # =========================
    # 📜 ДИАЛОГ
    # =========================

    if user_id not in dialogs:
        dialogs[user_id] = []

    dialogs[user_id].append({"type": "user", "text": text})

    save_data()

    name = users[user_id]["name"]

    first_question = len([m for m in dialogs[user_id] if m["type"] == "user"]) == 1

    status_text = "🆕 Первый вопрос" if first_question else "📩 Новый вопрос"

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("💬 Ответить", callback_data=f"reply_{user_id}"),
                InlineKeyboardButton("📜 История", callback_data=f"history_{user_id}"),
            ],
            [InlineKeyboardButton("👤 Профиль", url=f"tg://user?id={user_id}")],
        ]
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"{status_text}\n\n"
            f"👤 Имя: {name}\n"
            f"🆔 ID: {user_id}\n\n"
            f"💬 {text}"
        ),
        reply_markup=keyboard,
    )

    await update.message.reply_text("✅ Твой вопрос отправлен")


# =========================
# 🔘 КНОПКИ
# =========================


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data

    # 💬 ответ
    if data.startswith("reply_"):
        user_id = data.split("_")[1]
        pending_answers[ADMIN_ID] = user_id
        await query.message.reply_text(f"✍️ Напиши ответ пользователю {user_id}")

    # 📜 история
    elif data.startswith("history_"):
        user_id = data.split("_")[1]

        if user_id not in dialogs:
            await query.message.reply_text("❌ История пустая")
            return

        text = "📜 История диалога\n\n"

        for msg in dialogs[user_id]:
            if msg["type"] == "user":
                text += f"👤: {msg['text']}\n\n"
            else:
                text += f"🧑‍💻: {msg['text']}\n\n"

        await query.message.reply_text(text[:4000])


# =========================
# 🚀 ЗАПУСК
# =========================

load_data()

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_click))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
