import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- КОНФИГ ---
import os
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = -1001522210802   # ID канала колледжа (отрицательное число)
GROUP_ID = -1003653782560     # ID твоей группы
# -----------------

# Храним последнее сообщение с аудиторником (как объект)
last_auditorium = None

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот активен. Используй /auditorium для получения последнего аудиторника.")

async def auditorium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет последнее сохранённое сообщение с аудиторником."""
    global last_auditorium
    if last_auditorium is None:
        await update.message.reply_text("Пока нет ни одного сообщения с аудиторником.")
        return
    # Пересылаем сохранённое сообщение (копируем)
    await last_auditorium.copy(chat_id=update.effective_chat.id)
    # Или можно просто переслать, но copy безопаснее для медиа
    # await context.bot.forward_message(chat_id=update.effective_chat.id, from_chat_id=CHANNEL_ID, message_id=last_auditorium.message_id)

async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает новые сообщения из канала."""
    global last_auditorium
    # Проверяем, что сообщение именно из нашего канала
    if update.channel_post and update.channel_post.chat_id == CHANNEL_ID:
        # Проверяем, что сообщение не служебное (например, не удаление)
        if update.channel_post.text or update.channel_post.caption or update.channel_post.photo or update.channel_post.document:
            # Сохраняем последнее сообщение (можно хранить только текст, но лучше весь объект)
            last_auditorium = update.channel_post
            # Пересылаем в группу
            try:
                # Копируем сообщение в группу (без указания автора)
                await update.channel_post.copy(chat_id=GROUP_ID)
                # Можно добавить подпись
                # await context.bot.send_message(chat_id=GROUP_ID, text="Новый аудиторник!")
            except Exception as e:
                logging.error(f"Не удалось переслать в группу: {e}")

def main():
    application = Application.builder().token(TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("auditorium", auditorium))

    # Обработчик всех сообщений из канала (channel_post)
    application.add_handler(MessageHandler(filters.ALL, handle_channel_post))

    # Запуск поллинга
    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()