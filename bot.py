import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
)
from config import TELEGRAM_TOKEN, DEFAULT_VIDEO_QUALITY
from video_processor import compress_video, extract_audio
from collections import deque
import threading
import os

logging.basicConfig(level=logging.INFO)

# Cola de tareas y flag de ocupado
task_queue = deque()
is_processing = False

# Diccionario para guardar videos y configuraciones de cada chat
user_data = {}

# ---- Funciones de bot ----

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "¡Hola! Soy tu bot de compresión y extracción de audio de videos.\n"
        "Envíame un video para empezar."
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_processing

    file = update.message.video or update.message.document
    if not file:
        await update.message.reply_text("No se detectó un video válido.")
        return

    file_id = file.file_id
    new_file = await context.bot.get_file(file_id)
    input_path = f"temp_{file.file_name}" if hasattr(file, "file_name") else "temp_video.mp4"
    await new_file.download_to_drive(input_path)

    chat_id = update.message.chat_id
    user_data[chat_id] = {"input_path": input_path, "quality": DEFAULT_VIDEO_QUALITY}

    # Comprobamos si el bot está ocupado
    if is_processing:
        task_queue.append(chat_id)
        await update.message.reply_text(f"🤖 Bot ocupado. Tu tarea ha sido añadida a la cola. Posición en cola: {len(task_queue)}")
        return

    # Mostrar menú interactivo
    await show_main_menu(update, context)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    keyboard = [
        [InlineKeyboardButton("Comprimir video", callback_data="compress")],
        [InlineKeyboardButton("Extraer audio", callback_data="extract_audio")],
        [InlineKeyboardButton("Elegir calidad", callback_data="choose_quality")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Selecciona una opción:", reply_markup=reply_markup)

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id

    if chat_id not in user_data:
        await query.edit_message_text("Primero envíame un video.")
        return

    data = query.data
    input_path = user_data[chat_id]["input_path"]
    quality = user_data[chat_id].get("quality", DEFAULT_VIDEO_QUALITY)

    if data == "compress":
        add_task(chat_id, "compress", input_path, quality, context)
        await query.edit_message_text("✅ Tu video se ha añadido a la cola de compresión.")
    elif data == "extract_audio":
        add_task(chat_id, "extract_audio", input_path, quality, context)
        await query.edit_message_text("✅ Tu video se ha añadido a la cola para extraer audio.")
    elif data == "choose_quality":
        keyboard = [
            [InlineKeyboardButton("480p", callback_data="quality_480p")],
            [InlineKeyboardButton("720p", callback_data="quality_720p")],
            [InlineKeyboardButton("1080p", callback_data="quality_1080p")]
        ]
        await query.edit_message_text("Selecciona la calidad:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data.startswith("quality_"):
        quality = data.split("_")[1]
        user_data[chat_id]["quality"] = quality
        await query.edit_message_text(f"Calidad establecida a {quality}.")
        await show_main_menu(update, context)

# ---- Cola y procesamiento ----

def add_task(chat_id, task_type, input_path, quality, context):
    task_queue.append({"chat_id": chat_id, "type": task_type, "input_path": input_path, "quality": quality})
    if not is_processing:
        threading.Thread(target=process_task_queue, args=(context,)).start()

def process_task_queue(context):
    global is_processing
    import asyncio
    is_processing = True

    while task_queue:
        task = task_queue.popleft()
        chat_id = task["chat_id"]
        input_path = task["input_path"]
        task_type = task["type"]
        quality = task.get("quality", DEFAULT_VIDEO_QUALITY)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        msg = loop.run_until_complete(context.bot.send_message(chat_id, text=f"Procesando tu video: 0%"))

        # Progreso simulado (MoviePy no da callback real)
        if task_type == "compress":
            output_path = f"compressed_{input_path}"
            compress_video(input_path, output_path, quality=quality)
            loop.run_until_complete(context.bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text="✅ Video comprimido listo!"))
            with open(output_path, "rb") as f:
                loop.run_until_complete(context.bot.send_video(chat_id, f))
        elif task_type == "extract_audio":
            output_path = f"audio_{input_path}.mp3"
            extract_audio(input_path, output_path)
            loop.run_until_complete(context.bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text="✅ Audio extraído listo!"))
            with open(output_path, "rb") as f:
                loop.run_until_complete(context.bot.send_audio(chat_id, f))

        # Limpiar archivos temporales
        try:
            os.remove(input_path)
            os.remove(output_path)
        except Exception:
            pass

    is_processing = False

# ---- Función principal ----

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.FileExtension("mp4"), handle_video))
    app.add_handler(CallbackQueryHandler(handle_buttons))

    logging.info("Bot interactivo iniciado...")
    app.run_polling()

if __name__ == "__main__":
    main()
