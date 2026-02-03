import os
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Railway Variables kısmına 'BOT_TOKEN' adıyla eklediğin token'ı alır
BOT_TOKEN = os.getenv("BOT_TOKEN")

def ariza_verisi_yukle():
    # Yeni oluşturduğun tabloyu okur
    with open("ariza_tablosu.json", "r", encoding="utf-8") as f:
        return json.load(f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛠️ Kombi Destek Botu Hazır!\n\nSorununuzu birkaç kelimeyle yazın. (Örn: Basınç yüksek, su akıyor, sıcak su yok)"
    )

async def yanitla(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text.lower()
    data = ariza_verisi_yukle()
    found = False

    for ariza, icerik in data.items():
        # Anahtar kelimelerden herhangi biri mesajda geçiyor mu?
        if any(anahtar in user_msg for anahtar in icerik["anahtarlar"]):
            await update.message.reply_text(f"🔍 Tespit: {ariza.replace('_', ' ').title()}\n\n💡 Çözüm: {icerik['cozum']}")
            found = True
            break
    
    if not found:
        await update.message.reply_text("Bunu tam anlayamadım. Lütfen 'su sızıyor', 'bar artıyor' veya 'sıcak su' gibi net ifadeler kullanın.")

def main():
    if not BOT_TOKEN:
        print("HATA: BOT_TOKEN bulunamadı!")
        return

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, yanitla))
    
    print("Bot yeni sistemle başlatıldı...")
    app.run_polling()

if __name__ == "__main__":
    main()
