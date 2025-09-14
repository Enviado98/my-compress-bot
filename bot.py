import logging
import os
import time
from collections import deque
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext
from config import TELEGRAM_TOKEN, DEFAULT_VIDEO_QUALITY
from video_processor import compress_video, extract_audio
import threading

logging.basicConfig(level=logging.INFO)

# Cola de tareas y flag de ocupado
task_queue = deque()
is_processing = False

# Diccionario para guardar videos y configuraciones de cada chat
user_data = {}
cancel_flags = {}

# ---- Funciones de bot ----
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "¡Hola! Soy tu bot de compresión y extracción de audio de videos.\n"
        "Envíame un video para empezar."
    )

def handle_video(update: Update, context: CallbackContext):
    global is_processing

    file = update.message.video or update.message.document
    if not file:
        update.message.reply_text("No se detectó un video válido.")
        return

    file_id = file.file_id
    new_file = context.bot.get_file(file_id)
    input_path = f"temp_{file.file_name}" if hasattr(file, "file_name") else "temp_video.mp4"
    new_file.download(input_path)

    chat_id = update.message.chat_id
    user_data[chat_id] = {"input_path": input_path, "quality": DEFAULT_VIDEO_QUALITY}

    if is_processing:
        task_queue.append(chat_id)
        update.message.reply_text(f"🤖 Bot ocupado. Tu tarea ha sido añadida a la cola. Posición en cola: {len(task_queue)}")
        return

    show_main_menu(update, context)

def show_main_menu(update, context):
    chat_id = update.message.chat_id
    keyboard = [
        [InlineKeyboardButton("Comprimir video", callback_data="compress")],
        [InlineKeyboardButton("Extraer audio", callback_data="extract_audio")],
        [InlineKeyboardButton("Elegir calidad", callback_data="choose_quality")],
        [InlineKeyboardButton("Cancelar tarea", callback_data="cancel_task")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Selecciona una opción:", reply_markup=reply_markup)

def handle_buttons(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat_id
    query.answer()

    if chat_id not in user_data:
        query.edit_message_text("Primero envíame un video.")
        return

    data = query.data
    input_path = user_data[chat_id]["input_path"]
    quality = user_data[chat_id].get("quality", DEFAULT_VIDEO_QUALITY)

    if data == "compress":
        add_task(chat_id, "compress", input_path, quality, context)
        query.edit_message_text("✅ Tu video se ha añadido a la cola de compresión.")
    elif data == "extract_audio":
        add_task(chat_id, "extract_audio", input_path, quality, context)
        query.edit_message_text("✅ Tu video se ha añadido a la cola para extraer audio.")
    elif data == "choose_quality":
        keyboard = [
            [InlineKeyboardButton("144p", callback_data="quality_144p")],
            [InlineKeyboardButton("240p", callback_data="quality_240p")],
            [InlineKeyboardButton("480p", callback_data="quality_480p")],
            [InlineKeyboardButton("720p", callback_data="quality_720p")],
            [InlineKeyboardButton("1080p", callback_data="quality_1080p")]
        ]
        query.edit_message_text("Selecciona la calidad:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data.startswith("quality_"):
        quality = data.split("_")[1]
        user_data[chat_id]["quality"] = quality
        query.edit_message_text(f"Calidad establecida a {quality}.")
        show_main_menu(query, context)
    elif data == "cancel_task":
        cancel_flags[chat_id] = True
        query.edit_message_text("❌ Tu tarea ha sido marcada para cancelar.")

# ---- Cola y procesamiento ----
def add_task(chat_id, task_type, input_path, quality, context):
    task_queue.append({"chat_id": chat_id, "type": task_type, "input_path": input_path, "quality": quality})
    if not is_processing:
        threading.Thread(target=process_task_queue, args=(context,)).start()

def process_task_queue(context: CallbackContext):
    global is_processing
    is_processing = True

    while task_queue:
        task = task_queue.popleft()
        chat_id = task["chat_id"]
        input_path = task["input_path"]
        task_type = task["type"]
        quality = task.get("quality", DEFAULT_VIDEO_QUALITY)

        cancel_flags[chat_id] = False
        msg = context.bot.send_message(chat_id, text=f"Procesando tu video: 0%")

        steps = [25, 50, 75, 100]
        for i, pct in enumerate(steps):
            if cancel_flags.get(chat_id):
                context.bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=f"❌ Tarea cancelada al {pct-25}%")
                partial_path = f"partial_{input_path}" if os.path.exists(input_path) else None
                if partial_path:
                    with open(partial_path, "rb") as f:
                        context.bot.send_video(chat_id, f)
                break

            if i == 1 and task_type == "compress":
                output_path = f"compressed_{input_path}"
                compress_video(input_path, output_path, quality=quality)
            elif i == 1 and task_type == "extract_audio":
                output_path = f"audio_{input_path}.mp3"
                extract_audio(input_path, output_path)

            context.bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=f"Procesando tu video: {pct}%")
            time.sleep(1)  # Simulación de tiempo de procesamiento

        else:
            context.bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text="✅ Proceso completado!")

            if task_type == "compress":
                with open(output_path, "rb") as f:
                    context.bot.send_video(chat_id, f)
            elif task_type == "extract_audio":
                with open(output_path, "rb") as f:
                    context.bot.send_audio(chat_id, f)

        # Limpiar archivos temporales
        try:
            os.remove(input_path)
            if 'output_path' in locals() and os.path.exists(output_path):
                os.remove(output_path)
        except Exception:
            pass

    is_processing = False

# ---- Función principal ----
def main():
    updater = Updater(TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(filters.VIDEO | filters.Document.FileExtension("mp4"), handle_video))
    dispatcher.add_handler(CallbackQueryHandler(handle_buttons))

    logging.info("Bot interactivo iniciado...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
