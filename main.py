import os
import json
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Railway'den Token'ı alıyoruz
BOT_TOKEN = os.getenv("BOT_TOKEN")

def veri_yukle():
    # GitHub'daki JSON dosyanın adıyla aynı olmalı
    with open("arizalar.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Türkçe karakter uyumlu küçük harf dönüştürücü
def turkce_lower(metin):
    metin = metin.replace('İ', 'i').replace('I', 'ı').replace('Ğ', 'ğ').replace('Ü', 'ü').replace('Ş', 'ş').replace('Ö', 'ö').replace('Ç', 'ç')
    return metin.lower()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Markaları buton olarak hazırlıyoruz
    markalar = [
        ["Maktek Epsilon", "Maktek Rubby"],
        ["Dizayn Doru", "Bosch Condense 2000W"],
        ["Vaillant", "Daikin"]
    ]
    
    reply_markup = ReplyKeyboardMarkup(markalar, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        "🛠️ **Kombi Arıza Teşhis Sistemine Hoş Geldiniz**\n\nLütfen kombinizin markasını seçin:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def mesaj_isleyici(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    data = veri_yukle()
    
    # Boşlukları alt tireye çeviriyoruz (JSON anahtarlarıyla eşleşmesi için)
    # Örn: "Maktek Epsilon" -> "Maktek_Epsilon"
    formatli_marka = user_text.replace(" ", "_")

    # 1. DURUM: Kullanıcı marka butonuna mı bastı?
    if formatli_marka in data:
        context.user_data["secili_marka"] = formatli_marka
        await update.message.reply_text(
            f"✅ **{user_text}** seçildi.\n\nŞimdi hata kodunu (E01, F1 vb.) veya sorunu (su akıtıyor, bar yüksek vb.) yazabilirsiniz.",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown"
        )
        return

    # 2. DURUM: Marka seçiliyse arıza ara
    marka_key = context.user_data.get("secili_marka")
    
    if not marka_key:
        await update.message.reply_text("⚠️ Lütfen önce bir marka seçin. Menü için /start yazabilirsiniz.")
        return

    user_msg_lower = turkce_lower(user_text)
    found = False
    
    # Seçilen markanın altındaki arızaları tara
    marka_arizalari = data[marka_key]
    
    for ariza_id, icerik in marka_arizalari.items():
        for anahtar in icerik["anahtarlar"]:
            if turkce_lower(anahtar) in user_msg_lower:
                await update.message.reply_text(
                    f"🔍 **Teşhis:** {ariza_id.replace('_', ' ').title()}\n\n💡 **Çözüm:** {icerik['cozum']}\n\n"
                    f"🔄 _Başka bir marka seçmek için /start yazın._",
                    parse_mode="Markdown"
                )
                found = True
                break
        if found: break
        
    if not found:
        await update.message.reply_text(
            f"😕 Üzgünüm, **{marka_key.replace('_', ' ')}** için bu sorunu tanıyamadım.\n"
            "Lütfen hata kodunu veya anahtar kelimeyi (basınç, su akıtma vb. yada kombi ekranındaki hata kodunu giriniz ) tekrar kontrol edin.",
            parse_mode="Markdown"
        )

def main():
    if not BOT_TOKEN:
        print("HATA: BOT_TOKEN eksik!")
        return

    app = Application.builder
