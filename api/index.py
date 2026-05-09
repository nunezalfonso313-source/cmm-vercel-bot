import os
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("8226788618:AAEAoAvt7l9mwI8arZJ2R-Yq49eIjDB_lUc")
GROQ_KEY = os.getenv("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")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

SISTEMA_CMM = """[IDENTIDAD: INSTRUCTOR TÉCNICO ASME Y14.5]
Tu único propósito es enseñar GD&T y CMM.
"""

user_sessions = {}

def get_ai_response(user_id, user_input):
    if user_id not in user_sessions:
        user_sessions[user_id] = [
            {"role": "system", "content": SISTEMA_CMM}
        ]

    user_sessions[user_id].append(
        {"role": "user", "content": user_input}
    )

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": user_sessions[user_id],
        "temperature": 0.0
    }

    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }

    r = requests.post(
        GROQ_URL,
        headers=headers,
        json=payload,
        timeout=15
    )

    msg = r.json()["choices"][0]["message"]["content"]

    user_sessions[user_id].append(
        {"role": "assistant", "content": msg}
    )

    return msg


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "INSTRUCTOR CMM ONLINE"
    )


async def handle(update: Update, context):
    resp = get_ai_response(
        update.effective_user.id,
        update.message.text
    )

    await update.message.reply_text(resp)


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(
    MessageHandler(
        filters.TEXT & (~filters.COMMAND),
        handle
    )
)


async def handler(request):
    data = await request.json()
    update = Update.de_json(data, app.bot)
    await app.process_update(update)

    return {
        "statusCode": 200,
        "body": "ok"
    }
