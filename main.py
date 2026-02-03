import os
import json
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

def soru_akisi_yukle():
    with open("soru_akisi.json", "r", encoding="utf-8") as f:
        return json.load(f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = soru_akisi_yukle()
    # Tüm ana kategorileri (basinc, sicak_su, ses_yapiyor vs.) listele
    context.user_data["kategoriler"] = list(data.keys())
    context.user_data["kategori_index"] = 0
    
    await soru_sor(update, context)

async def soru_sor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = soru_akisi_yukle()
    kategoriler = context.user_data["kategoriler"]
    idx = context.user_data["kategori_index"]

    # Eğer tüm kategoriler bittiyse
    if idx >= len(kategoriler):
        await update.message.reply_text("Tüm teşhis adımları tamamlandı. Sorun tespit edilemediyse lütfen servisi arayın.")
        context.user_data.clear()
        return

    mevcut_kat = kategoriler[idx]
    ilk_soru = data[mevcut_kat]["ilk_soru"]
    context.user_data["mevcut_kategori"] = mevcut_kat
    context.user_data["mevcut_soru"] = ilk_soru

    reply_keyboard = [["Evet", "Hayır"]]
    await update.message.reply_text(
        f"Kategori: {mevcut_kat.upper()}\n\n{ilk_soru}",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )

async def yanitla(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answer = update.message.text
    if user_answer not in ["Evet", "Hayır"]:
        await update.message.reply_text("Lütfen butonları kullanın.")
        return

    data = soru_akisi_yukle()
    kat_adi = context.user_data.get("mevcut_kategori")
    soru_adi = context.user_data.get("mevcut_soru")
    
    adim = data[kat_adi]["sorular"].get(soru_adi, {}).get(user_answer)

    if not adim:
        await update.message.reply_text("Bir hata oluştu, baştan başlıyoruz.")
        return

    # EĞER BİR SONRAKİ SORU VARSA
    if "sonraki_soru" in adim:
        next_q = adim["sonraki_soru"]
        context.user_data["mevcut_soru"] = next_q
        await update.message.reply_text(
            next_q,
            reply_markup=ReplyKeyboardMarkup([["Evet", "Hayır"]], one_time_keyboard=True, resize_keyboard=True)
        )
    
    # EĞER "HAYIR" DEDİYSE VEYA "BİTİR" GELDİYSE BİR SONRAKİ KATEGORİYE GEÇ
    elif adim.get("bitir") or user_answer == "Hayır":
        await update.message.reply_text(f"{kat_adi} kontrolü tamamlandı, diğer ihtimale geçiliyor...")
        context.user_data["kategori_index"] += 1
        await soru_sor(update, context)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, yanitla))
    app.run_polling()

if __name__ == "__main__":
    main()
