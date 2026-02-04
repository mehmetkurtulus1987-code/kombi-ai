import os
import json
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "8506165438"  # BURAYA @userinfobot'tan aldığın ID'yi yaz!

def veri_yukle():
    with open("ariza_tablosu.json", "r", encoding="utf-8") as f:
        return json.load(f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    # Ana menüye 'Bakım Randevusu Al 📅' butonu ekledik
    markalar = [
        ["Maktek Epsilon", "Dizayn Doru"],
        ["Daikin", "Vaillant"],
        ["Baymak", "Bakım Randevusu Al 📅"]
    ]
    reply_markup = ReplyKeyboardMarkup(markalar, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("🛠️ **Kombi Destek ve Randevu Sistemi**\n\nLütfen işlem seçin:", reply_markup=reply_markup, parse_mode="Markdown")

async def mesaj_isleyici(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_id = update.effective_user.id
    data = veri_yukle()

    # --- RANDEVU SÜRECİ ---
    if user_text == "Bakım Randevusu Al 📅":
        context.user_data["durum"] = "İSİM_BEKLIYOR"
        await update.message.reply_text("🗓️ Randevu için lütfen **Adınızı ve Soyadınızı** yazın:", reply_markup=ReplyKeyboardRemove())
        return

    if context.user_data.get("durum") == "İSİM_BEKLIYOR":
        context.user_data["ad_soyad"] = user_text
        context.user_data["durum"] = "TEL_BEKLIYOR"
        await update.message.reply_text(f"Teşekkürler {user_text}. Lütfen size ulaşabileceğimiz **Telefon Numaranızı** yazın:")
        return

    if context.user_data.get("durum") == "TEL_BEKLIYOR":
        context.user_data["telefon"] = user_text
        context.user_data["durum"] = "NOT_BEKLIYOR"
        await update.message.reply_text("Son olarak, kombi markasını ve varsa özel notunuzu yazın:")
        return

    if context.user_data.get("durum") == "NOT_BEKLIYOR":
        # Tüm bilgileri topladık, SANA gönderiyoruz
        ad = context.user_data.get("ad_soyad")
        tel = context.user_data.get("telefon")
        not_bilgisi = user_text
        
        bildirim = (
            f"🔔 **YENİ RANDEVU TALEBİ**\n\n"
            f"👤 Müşteri: {ad}\n"
            f"📞 Telefon: {tel}\n"
            f"📝 Not: {not_bilgisi}\n"
            f"🆔 Kullanıcı ID: {user_id}"
        )
        
        # Sana mesaj gönderir
        await context.bot.send_message(chat_id=ADMIN_ID, text=bildirim, parse_mode="Markdown")
        
        # Müşteriye onay verir
        await update.message.reply_text("✅ Talebiniz alındı! En kısa sürede size geri dönüş yapacağız. /start ile ana menüye dönebilirsiniz.")
        context.user_data.clear()
        return

    # --- ARIZA SORGULAMA SÜRECİ ---
    if user_text in data:
        context.user_data["secili_marka"] = user_text
        await update.message.reply_text(f"✅ **{user_text}** seçildi. Sorunuzu yazın:", reply_markup=ReplyKeyboardRemove())
        return

    marka = context.user_data.get("secili_marka")
    if marka:
        user_msg = user_text.lower()
        for ariza_id, icerik in data[marka].items():
            if any(anahtar.lower() in user_msg for anahtar in icerik["anahtarlar"]):
                teshis = icerik.get("teshis", "Arıza")
                await update.message.reply_text(f"🔍 **{marka} - {teshis}**\n\n💡 **Çözüm:** {icerik['cozum']}", parse_mode="Markdown")
                
                # BİLGİ GELMESİ: Arıza sorgulandığında sana bildirim gider
                await context.bot.send_message(
                    chat_id=ADMIN_ID, 
                    text=f"⚠️ **Arıza Sorgusu Yapıldı**\nMarka: {marka}\nSorgu: {user_text}\nTeşhis: {teshis}",
                    parse_mode="Markdown"
                )
                return
        await update.message.reply_text("Anlayamadım, lütfen daha net yazın veya /start ile marka seçin.")
    else:
        await update.message.reply_text("Lütfen önce bir marka seçin veya Randevu butonuna basın.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mesaj_isleyici))
    app.run_polling()

if __name__ == "__main__":
    main()
