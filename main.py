import os
import json
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Logları Railway panelinden görebilmek için aktif ediyoruz
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")

def veri_yukle():
    try:
        with open("ariza_tablosu.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"JSON okuma hatası: {e}")
        return {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Kullanıcının eski seçimini sıfırla
    context.user_data.clear()
    
    # Butonları tam olarak senin markalarınla oluşturuyoruz
    klavye = [
        ["Maktek Epsilon", "Maktek Rubby"],
        ["Dizayn Doru", "Bosch Condense 2000W"]
    ]
    
    reply_markup = ReplyKeyboardMarkup(klavye, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        "🛠️ **Kombi Destek Sistemine Hoş Geldiniz**\n\nLütfen kombinizin markasını seçin:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def mesaj_isleyici(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    data = veri_yukle()
    
    # 1. DURUM: Kullanıcı marka butonuna mı bastı? (JSON anahtarlarını kontrol et)
    # Boşlukları alt tireye çevirmeden, doğrudan JSON anahtarlarıyla kıyaslıyoruz
    marka_listesi = list(data.keys())
    
    # Kullanıcının bastığı buton JSON'da bir ana başlık mı?
    # (JSON'daki başlıkların "Maktek Epsilon" şeklinde boşluklu olduğunu varsayıyoruz)
    if user_text in marka_listesi:
        context.user_data["secili_marka"] = user_text
        await update.message.reply_text(
            f"✅ **{user_text}** seçildi. Şimdi sorunuzu veya hata kodunu yazabilirsiniz.",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown"
        )
        return

    # 2. DURUM: Marka seçiliyse arıza ara
    marka = context.user_data.get("secili_marka")
    if not marka:
        await update.message.reply_text("Lütfen önce bir marka seçin. Menü için /start yazabilirsiniz.")
        return

    # Arama işlemi
    user_msg = user_text.lower()
    found = False
    
    for ariza_id, icerik in data[marka].items():
        for anahtar in icerik["anahtarlar"]:
            if anahtar.lower() in user_msg:
                await update.message.reply_text(f"🔍 **{marka} Teşhis:**\n\n{icerik['cozum']}\n\n_Sıfırlamak için /start yazın._", parse_mode="Markdown")
                found = True
                break
        if found: break
        
    if not found:
        await update.message.reply_text("Bunu anlayamadım. Lütfen farklı kelimelerle deneyin veya /start ile marka değiştirin.")

def main():
    if not BOT_TOKEN: return
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mesaj_isleyici))
    app.run_polling()

if __name__ == "__main__":
    main()
