import os
import logging
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
GOOGLE_SHEET_NAME = "Посты Telegram"
GOOGLE_SHEET_TAB = "Лист1"

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
gc = gspread.authorize(credentials)

async def post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        sheet = gc.open(GOOGLE_SHEET_NAME).worksheet(GOOGLE_SHEET_TAB)
        data = sheet.get_all_records()

        for i, row in enumerate(data):
            if str(row.get("опубликован", "")).lower() != "да":
                текст = row.get("текст", "").strip()
                фото = row.get("фото", "").strip()

                if фото:
                    await context.bot.send_photo(chat_id=CHANNEL_ID, photo=фото, caption=текст)
                else:
                    await context.bot.send_message(chat_id=CHANNEL_ID, text=текст)

                sheet.update_cell(i + 2, 3, "да")
                await update.message.reply_text("✅ Пост опубликован.")
                return

        await update.message.reply_text("⚠️ Все посты уже опубликованы.")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("post", post))
    app.run_polling()

if __name__ == '__main__':
    main()
