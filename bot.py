import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from config import TELEGRAM_TOKEN

logging.basicConfig(level=logging.INFO)

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "¡Hola! Soy tu bot de compresión de video.\n"
        "Puedes enviarme un video y lo procesaré."
    )

def main():
    updater = Updater(TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))

    logging.info("Bot iniciado. Esperando mensajes...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
