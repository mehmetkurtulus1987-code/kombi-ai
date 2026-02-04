import os
import json
import logging
import urllib.parse
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Loglama ayarları (Railway üzerinden hataları takip etmek için)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "1079504201"  # Senin verdiğin Admin ID

def veri_yukle():
    try:
        with open("ariza_tablosu.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"JSON yükleme hatası: {e}")
        return {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    # Ana menü
    markalar = [
        ["Maktek Epsilon", "Dizayn Doru"],
        ["Daikin", "Vaillant"],
        ["Baymak", "Bakım Randevusu Al 📅"]
    ]
    reply_markup = ReplyKeyboardMarkup(markalar, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "🛠️ **Kombi Destek ve Teknik Servis**\n\nLütfen cihazınızı seçin veya randevu oluşturun:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def mesaj_isleyici(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_id = update.effective_user.id
    data = veri_yukle()

    # --- RANDEVU SÜRECİ ---
    if user_text == "Bakım Randevusu Al 📅":
        context.user_data["durum"] = "İSİM_BEKLIYOR"
        await update.message.reply_text("🗓️ Randevu için **Adınızı ve Soyadınızı** yazın:", reply_markup=ReplyKeyboardRemove())
        return

    if context.user_data.get("durum") == "İSİM_BEKLIYOR":
        context.user_data["ad_soyad"] = user_text
        context.user_data["durum"] = "TEL_BEKLIYOR"
        await update.message.reply_text(f"Teşekkürler {user_text}. 📞 Lütfen **Telefon Numaranızı** yazın:")
        return

    if context.user_data.get("durum") == "TEL_BEKLIYOR":
        context.user_data["telefon"] = user_text
        context.user_data["durum"] = "NOT_BEKLIYOR"
        await update.message.reply_text("📝 Son olarak, varsa arıza kodunu veya adresinizi not olarak yazın:")
        return

    if context.user_data.get("durum") == "NOT_BEKLIYOR":
        ad = context.user_data.get("ad_soyad")
        tel = context.user_data.get("telefon")
        not_bilgisi = user_text
        marka = context.user_data.get("secili_marka", "Belirtilmedi")
        
        # 1. Telegram Admin Bildirimi (Sana gelir)
        bildirim = (
            f"🔔 **YENİ RANDEVU TALEBİ**\n\n"
            f"👤 Müşteri: {ad}\n"
            f"📞 Telefon: {tel}\n"
            f"🏢 Cihaz: {marka}\n"
            f"📝 Not: {not_bilgisi}\n"
            f"🆔 ID: {user_id}"
        )
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=bildirim, parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Bildirim gönderilemedi: {e}")

        # 2. WhatsApp Mesajı Oluşturma
        ws_mesaj = f"Randevu Talebi!!!\nMüşteri: {ad}\nTelefon: {tel}\nCihaz: {marka}\nArıza/Not: {not_bilgisi}"
        encoded_mesaj = urllib.parse.quote(ws_mesaj)
        whatsapp_url = f"https://wa.me/905060357883?text={encoded_mesaj}"
        
        # WhatsApp Onay Butonu
        kb = [[InlineKeyboardButton("WhatsApp ile Onayla ✅", url=whatsapp_url)]]
        reply_markup = InlineKeyboardMarkup(kb)

        await update.message.reply_text(
            "✅ Bilgileriniz sisteme kaydedildi.\n\nLütfen aşağıdaki butona tıklayarak talebinizi **WhatsApp üzerinden bize iletin** (Randevunuz bu şekilde onaylanacaktır):",
            reply_markup=reply_markup
        )
        context.user_data.clear()
        return

    # --- ARIZA SORGULAMA SÜRECİ ---
    if user_text in data:
        context.user_data["secili_marka"] = user_text
        await update.message.reply_text(f"✅ **{user_text}** seçildi. Sorunuzu veya hata kodunu yazın:", reply_markup=ReplyKeyboardRemove())
        return

    marka = context.user_data.get("secili_marka")
    if marka:
        user_msg = user_text.lower()
        found = False
        for ariza_id, icerik in data[marka].items():
            if any(anahtar.lower() in user_msg for anahtar in icerik["anahtarlar"]):
                teshis = icerik.get("teshis", "Arıza")
                
                # Çözüm mesajı ve altına Randevu Butonu teklifi
                rm = ReplyKeyboardMarkup([["Bakım Randevusu Al 📅"], ["/start"]], resize_keyboard=True)
                
                response = (
                    f"🔍 **{marka} - {teshis}**\n\n"
                    f"💡 **Çözüm:** {icerik['cozum']}\n\n"
                    f"💬 _Sorun çözülmedi mi? Aşağıdaki butondan hızlıca servis randevusu alabilirsiniz._"
                )
                await update.message.reply_text(response, reply_markup=rm, parse_mode="Markdown")
                
                # Sana bilgi mesajı gönderir
                await context.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=f"⚠️ **Arıza Sorgusu:** {marka}\n**Kullanıcı:** {user_id}\n**Sorgu:** {user_text}\n**Teşhis:** {teshis}",
                    parse_mode="Markdown"
                )
                found = True
                break
        
        if not found:
            # Arıza bulunamazsa da randevu teklif et
            await update.message.reply_text(
                "Arıza kodunu anlayamadım. Lütfen net bir şekilde (Örn: E05) yazın veya randevu oluşturun.",
                reply_markup=ReplyKeyboardMarkup([["Bakım Randevusu Al 📅"], ["/start"]], resize_keyboard=True)
            )
    else:
        await update.message.reply_text("Lütfen önce bir marka seçin veya /start yazın.")

def main():
    if not BOT_TOKEN:
        logging.error("BOT_TOKEN bulunamadı!")
        return
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mesaj_isleyici))
    app.run_polling()

if __name__ == "__main__":
    main()
