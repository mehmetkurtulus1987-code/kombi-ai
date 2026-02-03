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
    found_replies = []

    for ariza, icerik in data.items():
        # Eğer kullanıcının mesajında anahtar kelimelerden HERHANGİ BİRİ geçiyorsa
        for anahtar in icerik["anahtarlar"]:
            if anahtar in user_msg:
                found_replies.append(icerik["cozum"])
                break # Bu kategoriden bir eşleşme bulduk, diğer anahtarlara bakmaya gerek yok

    if found_replies:
        # Birden fazla eşleşme varsa hepsini gönderir (Örn: hem su akıtıyor hem basınç diyorsa)
        combined_reply = "\n\n".join(found_replies)
        await update.message.reply_text(combined_reply)
    else:
        await update.message.reply_text(
            "Anlayamadım. Lütfen 'su akıtıyor', 'basınç' gibi kelimeler kullanarak sorunu anlatın."
        )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ariza_teshis))
    
    print("Bot serbest metin modunda çalışıyor...")
    app.run_polling()

if __name__ == "__main__":
    main()
