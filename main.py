import os
import json
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

def soru_akisi_yukle():
    with open("soru_akisi.json", "r", encoding="utf-8") as f:
        return json.load(f)

# /start komutu - Teşhisi başlatır
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = soru_akisi_yukle()
    # İlk ana kategoriyi (örneğin: basinc) ve onun ilk sorusunu alıyoruz
    ilk_soru = data["basinc"]["ilk_soru"]
    
    # Kullanıcının hangi aşamada olduğunu kaydetmek için context.user_data kullanıyoruz
    context.user_data["mevcut_soru"] = ilk_soru
    
    # Klavye butonları (Evet/Hayır)
    reply_keyboard = [["Evet", "Hayır"]]
    
    await update.message.reply_text(
        f"Kombi Teşhis Başladı!\n\n{ilk_soru}",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )

async def yanitla(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answer = update.message.text # "Evet" veya "Hayır"
    current_question = context.user_data.get("mevcut_soru")
    
    if not current_question:
        await update.message.reply_text("Lütfen /start yazarak teşhisi başlatın.")
        return

    data = soru_akisi_yukle()
    soru_havuzu = data["basinc"]["sorular"]

    # Mevcut sorunun cevabına göre bir sonraki adımı bul
    if current_question in soru_havuzu and user_answer in soru_havuzu[current_question]:
        adim = soru_havuzu[current_question][user_answer]
        
        if adim.get("bitir"):
            await update.message.reply_text("Teşhis tamamlandı. Sorun tespit edildi veya süreç bitti.")
            context.user_data.clear() # Durumu temizle
        else:
            next_question = adim.get("sonraki_soru")
            context.user_data["mevcut_soru"] = next_question
            reply_keyboard = [["Evet", "Hayır"]]
            await update.message.reply_text(
                next_question,
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
            )
    else:
        await update.message.reply_text("Lütfen sadece 'Evet' veya 'Hayır' butonlarını kullanın.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, yanitla))
    app.run_polling()

if __name__ == "__main__":
    main()
