import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext
from config import TELEGRAM_TOKEN, DEFAULT_VIDEO_QUALITY
from video_processor import compress_video, extract_audio

logging.basicConfig(level=logging.INFO)

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "¡Hola! Soy tu bot de compresión de video.\n"
        "Envíame un video para comprimirlo o extraer audio."
    )

def handle_video(update: Update, context: CallbackContext):
    file = update.message.video or update.message.document
    if not file:
        update.message.reply_text("No se detectó un video válido.")
        return

    file_id = file.file_id
    new_file = context.bot.get_file(file_id)
    input_path = f"temp_{file.file_name}" if hasattr(file, "file_name") else "temp_video.mp4"
    new_file.download(input_path)

    update.message.reply_text("Procesando video...")

    # Comprimir video
    output_path = f"compressed_{input_path}"
    compress_video(input_path, output_path, quality=DEFAULT_VIDEO_QUALITY)

    # Responder con el video comprimido
    update.message.reply_text("Aquí está tu video comprimido:")
    with open(output_path, "rb") as f:
        update.message.reply_video(f)

def main():
    updater = Updater(TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(filters.VIDEO | filters.Document.FileExtension("mp4"), handle_video))

    logging.info("Bot iniciado. Esperando videos...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
