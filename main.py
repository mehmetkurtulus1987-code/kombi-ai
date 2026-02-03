import os
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

def ariza_verisi_yukle():
    # Dosya adını ariza_tablosu.json olarak güncellediğini varsayıyorum
    with open("ariza_tablosu.json", "r", encoding="utf-8") as f:
        return json.load(f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛠️ Kombi Destek Botuna Hoş Geldiniz!\n\nLütfen yaşadığınız sorunu kısaca yazın (Örn: Basınç yükseliyor, sıcak su gelmiyor...)"
    )

async def ariza_teshis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text.lower()
    data = ariza_verisi_yukle()
    found = False

    for ariza, icerik in data.items():
        # Kullanıcının yazdığı mesajda belirlediğimiz anahtar kelimelerden biri geçiyor mu?
        if any(anahtar in user_msg for anahtar in icerik["anahtarlar"]):
            await update.message.reply_text(icerik["cozum"])
            found = True
            break
    
    if not found:
        await update.message.reply_text(
            "Anlayamadım. Lütfen 'su akıtıyor', 'basınç düşüyor' gibi anahtar kelimeler içeren bir cümle kurun veya bir teknik servise danışın."
        )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ariza_teshis))
    
    print("Bot serbest metin modunda çalışıyor...")
    app.run_polling()

if __name__ == "__main__":
    main()
