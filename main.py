import os
import json
import logging
import urllib.parse
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Loglama ayarları
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "1079504201" 

def veri_yukle():
    try:
        with open("ariza_tablosu.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"JSON yükleme hatası: {e}")
        return {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
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
        await update.message.reply_text("📝 Varsa adresinizi veya eklemek istediğiniz notu yazın:")
        return

    if context.user_data.get("durum") == "NOT_BEKLIYOR":
        ad = context.user_data.get("ad_soyad")
        tel = context.user_data.get("telefon")
        not_bilgisi = user_text
        marka = context.user_data.get("secili_marka", "Belirtilmedi")
        bulunan_teshis = context.user_data.get("bulunan_teshis", "Genel Arıza / Bakım")
        
        # 1. Telegram Admin Bildirimi
        bildirim = (
            f"🔔 **YENİ RANDEVU TALEBİ**\n\n"
            f"👤 Müşteri: {ad}\n"
            f"📞 Tel: {tel}\n"
            f"🏢 Marka: {marka}\n"
            f"🛠️ Arıza: {bulunan_teshis}\n"
            f"📝 Not: {not_bilgisi}"
        )
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=bildirim, parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Bildirim gönderilemedi: {e}")

        # 2. WhatsApp Mesajı Oluşturma
        ws_mesaj = (
            f"📌Randevu Talebi!!!\n"
            f"👤Müşteri: {ad}\n"
            f"📲Telefon: {tel}\n"
            f"📝Cihaz: {marka}\n"
            f"🛠️Arıza: {bulunan_teshis}\n"
            f"📍Not: {not_bilgisi}"
        )
        encoded_mesaj = urllib.parse.quote(ws_mesaj)
        whatsapp_url = f"https://wa.me/905060357883?text={encoded_mesaj}"
        
        kb = [[InlineKeyboardButton("WhatsApp ile Onayla ✅", url=whatsapp_url)]]
        await update.message.reply_text(
            "✅ Bilgileriniz alındı. Talebinizi WhatsApp üzerinden onaylatmak için butona tıklayın:",
            reply_markup=InlineKeyboardMarkup(kb)
        )
        # Sadece durum bilgisini temizle, markayı/teşhisi yeni aramalar için sıfırla
        context.user_data.clear()
        return

    # --- ARIZA SORGULAMA SÜRECİ ---
    if user_text in data:
        context.user_data["secili_marka"] = user_text
        await update.message.reply_text(f"✅ **{user_text}** seçildi. Sorunu veya hata kodunu yazın:", reply_markup=ReplyKeyboardRemove())
        return

    marka = context.user_data.get("secili_marka")
    if marka:
        user_msg = user_text.lower()
        found = False
        for ariza_id, icerik in data[marka].items():
            if any(anahtar.lower() in user_msg for anahtar in icerik["anahtarlar"]):
                teshis = icerik.get("teshis", "Bilinmeyen Arıza")
                
                # ÖNEMLİ: Bulunan teşhisi hafızaya alıyoruz ki randevu alınırsa kullanılsın
                context.user_data["bulunan_teshis"] = teshis
                
                rm = ReplyKeyboardMarkup([["Bakım Randevusu Al 📅"], ["/start"]], resize_keyboard=True)
                response = (
                    f"🔍 **{marka} - {teshis}**\n\n"
                    f"💡 **Çözüm:** {icerik['cozum']}\n\n"
                    f"🛠️ Sorun çözülmediyse yukarıdaki butondan randevu alabilirsiniz."
                )
                await update.message.reply_text(response, reply_markup=rm, parse_mode="Markdown")
                
                # Admin bildirimi
                await context.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=f"⚠️ **Sorgulama:** {marka}\nTeşhis: {teshis}\nKullanıcı: {user_id}"
                )
                found = True
                break
        
        if not found:
            await update.message.reply_text(
                "Arıza kodunu anlayamadım. Lütfen net yazın (Örn: E01) veya bakım randevusu oluşturun.",
                reply_markup=ReplyKeyboardMarkup([["Bakım Randevusu Al 📅"], ["/start"]], resize_keyboard=True)
            )
    else:
        await update.message.reply_text("Lütfen önce bir marka seçin veya /start yazın.")

def main():
    if not BOT_TOKEN: return
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mesaj_isleyici))
    app.run_polling()

if __name__ == "__main__":
    main()
