import os
import json
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

def veri_yukle():
    with open("arizalar.json", "r", encoding="utf-8") as f:
        return json.load(f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = veri_yukle()
    markalar = list(data.keys()) # JSON'daki marka isimlerini al (Dizayn, Eca vb.)
    
    # Markaları buton olarak göster
    reply_keyboard = [markalar[i:i+2] for i in range(0, len(markalar), 2)]
    
    await update.message.reply_text(
        "🛠️ Lütfen kombinizin markasını seçin:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )

async def mesaj_isleyici(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    data = veri_yukle()
    
    # 1. Adım: Kullanıcı marka mı seçti?
    if user_text in data:
        context.user_data["secili_marka"] = user_text
        await update.message.reply_text(
            f"✅ {user_text} markası seçildi. Şimdi yaşadığınız sorunu veya hata kodunu yazın:",
            reply_markup=ReplyKeyboardRemove()
        )
        return

    # 2. Adım: Marka seçiliyse arıza ara
    marka = context.user_data.get("secili_marka")
    if not marka:
        await update.message.reply_text("Lütfen önce bir marka seçin. /start komutu ile başlayabilirsiniz.")
        return

    # Sadece seçili markanın altındaki hataları tara
    user_msg = user_text.lower()
    found = False
    for hata_kodu, icerik in data[marka].items():
        if any(anahtar in user_msg for anahtar in icerik["anahtarlar"]):
            await update.message.reply_text(f"🔍 {marka} Teşhis:\n\n{icerik['cozum']}")
            found = True
            break
            
    if not found:
        await update.message.reply_text(f"Üzgünüm, {marka} için bu hatayı bulamadım. Lütfen kodu tekrar kontrol edin.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mesaj_isleyici))
    app.run_polling()

if __name__ == "__main__":
    main()
