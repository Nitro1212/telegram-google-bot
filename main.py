import os
import logging
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# === Настройки
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
GOOGLE_SHEET_NAME = "Посты Telegram"
GOOGLE_SHEET_TAB = "Лист1"

# === Авторизация в Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
gc = gspread.authorize(credentials)

# === Логгинг
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Команда /post
async def post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        sheet = gc.open(GOOGLE_SHEET_NAME).worksheet(GOOGLE_SHEET_TAB)
        data = sheet.get_all_records()

        for i, row in enumerate(data):
            if str(row.get("опубликован", "")).strip().lower() != "да":
                текст = row.get("текст", "").strip()
                фото = row.get("фото", "").strip()

                if not текст:
                    await update.message.reply_text("⚠️ Текст поста пустой.")
                    return

                if фото:
                    await context.bot.send_photo(chat_id=CHANNEL_ID, photo=фото, caption=текст)
                else:
                    await context.bot.send_message(chat_id=CHANNEL_ID, text=текст)

                sheet.update_cell(i + 2, 3, "да")  # строка i+2 (с учётом заголовка), колонка 3
                await update.message.reply_text("✅ Пост опубликован.")
                logger.info("Пост отправлен и отмечен как 'да'")
                return

        await update.message.reply_text("🔍 Нет новых постов для публикации.")
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await update.message.reply_text(f"❌ Ошибка при публикации:\n{e}")

# === Запуск
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("post", post))
    app.run_polling()

if __name__ == '__main__':
    main()
