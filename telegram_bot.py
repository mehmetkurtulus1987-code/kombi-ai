import requests
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

API_URL = os.getenv("API_URL")
BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Kombi arızasını seçelim. Başlayalım mı?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Başla", callback_data="basla")]
        ])
    )

async def buton(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)

    if query.data == "basla":
        r = requests.post(f"{API_URL}/basla", json={
            "belirti": "basınç",
            "kullanici_id": user_id
        })
        data = r.json()

        await query.message.reply_text(
            data["soru"],
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(b, callback_data=b)] for b in data["butonlar"]
            ])
        )
        return

    r = requests.post(f"{API_URL}/cevap", json={
        "kullanici_id": user_id,
        "cevap": query.data
    })
    data = r.json()

    if "teshis" in data:
        await query.message.reply_text(
            f"🔧 Tespit: {data['teshis']}\n\n"
            f"📌 Olası Sebepler:\n- " + "\n- ".join(data["olasi_sebepler"]) +
            "\n\n✅ İlk Kontrol:\n- " + "\n- ".join(data["ilk_kontrol"])
        )
    else:
        await query.message.reply_text(
            data["soru"],
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(b, callback_data=b)] for b in data["butonlar"]
            ])
        )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buton))
    app.run_polling()

if __name__ == "__main__":
    main()
