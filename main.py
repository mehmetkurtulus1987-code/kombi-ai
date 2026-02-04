import os
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

def ariza_verisi_yukle():
    with open("ariza_tablosu.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Türkçe karakter dostu küçük harfe çevirme fonksiyonu
def turkce_lower(metin):
    metin = metin.replace('İ', 'i').replace('I', 'ı')
    return metin.lower()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛠️ Kombi Destek Botu Hazır! Sorununuzu yazın.")

async def yanitla(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Kullanıcının mesajını Türkçe karakterlere uygun şekilde küçültüyoruz
    user_msg = turkce_lower(update.message.text)
    data = ariza_verisi_yukle()
    found = False

    for ariza, icerik in data.items():
        # JSON'daki anahtarları kontrol et
        for anahtar in icerik["anahtarlar"]:
            anahtar_kucuk = turkce_lower(anahtar)
            
            # Kelime cümlenin içinde geçiyor mu? (Örn: "su" kelimesi "su akıtıyor" içinde var mı?)
            if anahtar_kucuk in user_msg:
                await update.message.reply_text(f"🔍 Tespit: {ariza.replace('_', ' ').title()}\n\n💡 Çözüm: {icerik['cozum']}")
                found = True
                break
        if found: break # Bir tane bulduysak döngüden çık
    
    if not found:
        await update.message.reply_text("Bunu anlayamadım. Lütfen 'basınç', 'su', 'sıcaklık' gibi kelimeler kullanın.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, yanitla))
    app.run_polling()

if __name__ == "__main__":
    main()
