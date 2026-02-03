import os
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Railway Variables kısmından token'ı çekiyoruz
BOT_TOKEN = os.getenv("BOT_TOKEN")

# JSON dosyasını yükleme fonksiyonu
def soru_akisi_yukle():
    with open("soru_akisi.json", "r", encoding="utf-8") as f:
        return json.load(f)

# /start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Kombi teşhis botu hazır! Lütfen arızayı belirtin veya bir soru sorun.")

# Gelen mesajlara yanıt verme (Teşhis Mantığı)
async def yanitla(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.lower() # Kullanıcının yazdığı
    akistan_gelen_veri = soru_akisi_yukle() # JSON verisini oku
    
    # BASİT BİR MANTIK: JSON içinde anahtar kelime arama
    found_reply = "Üzgünüm, bu arıza hakkında bilgim yok. Lütfen teknik servise danışın."
    
    for anahtar, cevap in akistan_gelen_veri.items():
        if anahtar.lower() in user_text:
            found_reply = cevap
            break
            
    await update.message.reply_text(found_reply)

# Botu ayağa kaldıran ana kısım
def main():
    if not BOT_TOKEN:
        print("HATA: BOT_TOKEN bulunamadı! Railway variables kısmını kontrol edin.")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    # Handler'ları (işleyicileri) ekliyoruz
    app.add_handler(CommandHandler("start", start))
    # Mesajları dinleyen ve 'yanitla' fonksiyonuna gönderen kısım:
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, yanitla))

    print("Bot çalışıyor...")
    app.run_polling()

if __name__ == "__main__":
    main()
