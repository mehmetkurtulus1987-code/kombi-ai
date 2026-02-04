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
    user_text = update.message.text.strip() # Boşlukları temizle
    data = veri_yukle()
    
    # 1. DURUM: Marka Seçimi Kontrolü
    # JSON'daki markaları ve kullanıcının yazdığını karşılaştırırken küçük harfe çevirip bakıyoruz
    secilen_marka_anahtari = None
    for marka_adi in data.keys():
        if marka_adi.lower() == user_text.lower():
            secilen_marka_anahtari = marka_adi
            break

    if secilen_marka_anahtari:
        context.user_data["secili_marka"] = secilen_marka_anahtari
        await update.message.reply_text(
            f"✅ **{secilen_marka_anahtari}** seçildi. Şimdi sorununuzu yazın.",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown"
        )
        return

    # 2. DURUM: Arıza Arama
    marka = context.user_data.get("secili_marka")
    if not marka:
        # Eğer marka hafızada yoksa tekrar seçim yaptır
        await update.message.reply_text("⚠️ Önce marka seçmelisiniz. /start yazarak menüyü açın.")
        return

    # Arıza tarama mantığı
    user_msg = user_text.lower()
    found = False
    for ariza_id, icerik in data[marka].items():
        if any(anahtar.lower() in user_msg for anahtar in icerik["anahtarlar"]):
            # JSON'daki "teshis" alanını alıyoruz, yoksa eski sistemdeki gibi ariza_id'yi kullanıyoruz
            teshis_basligi = icerik.get("teshis", ariza_id.replace("_", " ").title())
            cozum_metni = icerik.get("cozum", "Çözüm bulunamadı.")

            response = (
                f"🔍 **{marka} - {teshis_basligi}**\n\n"
                f"💡 **Çözüm:** {cozum_metni}\n\n"
                f"🔄 _Başka bir işlem için /start yazabilirsiniz._"
            )
            
            await update.message.reply_text(response, parse_mode="Markdown")
            found = True
            break
            
    if not found:
        await update.message.reply_text("Bunu anlayamadım. Lütfen 'basınç', 'E01' gibi net kelimeler yazın.")

def main():
    if not BOT_TOKEN: return
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mesaj_isleyici))
    app.run_polling()

if __name__ == "__main__":
    main()
