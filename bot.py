import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from video_processor import compress_video, extract_audio
from collections import deque
import threading

# Configuración de logging
logging.basicConfig(level=logging.INFO)

# Leer variables de entorno
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

DEFAULT_VIDEO_QUALITY = "720p"

# Cola de tareas y flag de ocupado
task_queue = deque()
is_processing = False

# Diccionario para guardar videos y configuraciones de cada chat
user_data = {}

# ---- Funciones del bot ----

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

    if is_processing:
        task_queue.append(chat_id)
        await update.message.reply_text(
            f"🤖 Bot ocupado. Tu tarea ha sido añadida a la cola. Posición en cola: {len(task_queue)}"
        )
        return

    await show_main_menu(update, context)

async def show_main_menu(update, context):
    chat_id = update.message.chat_id
    keyboard = [
        [InlineKeyboardButton("Comprimir video", callback_data="compress")],
        [InlineKeyboardButton("Extraer audio", callback_data="extract_audio")],
        [InlineKeyboardButton("Elegir calidad", callback_data="choose_quality")],
        [InlineKeyboardButton("Cancelar tarea", callback_data="cancel_task")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Selecciona una opción:", reply_markup=reply_markup)

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat_id
    await query.answer()

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
            [InlineKeyboardButton("144p", callback_data="quality_144p")],
            [InlineKeyboardButton("480p", callback_data="quality_480p")],
            [InlineKeyboardButton("720p", callback_data="quality_720p")],
            [InlineKeyboardButton("1080p", callback_data="quality_1080p")]
        ]
        await query.edit_message_text("Selecciona la calidad:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data.startswith("quality_"):
        quality = data.split("_")[1]
        user_data[chat_id]["quality"] = quality
        await query.edit_message_text(f"Calidad establecida a {quality}.")
        await show_main_menu(query, context)
    elif data == "cancel_task":
        cancel_task(chat_id, context)
        await query.edit_message_text("❌ Tu tarea ha sido cancelada.")

# ---- Cola y procesamiento ----

def add_task(chat_id, task_type, input_path, quality, context):
    task_queue.append({"chat_id": chat_id, "type": task_type, "input_path": input_path, "quality": quality})
    if not is_processing:
        threading.Thread(target=lambda: threading_run(context)).start()

def cancel_task(chat_id, context):
    global task_queue
    task_queue = deque(task for task in task_queue if task["chat_id"] != chat_id)
    # Aquí podrías devolver el archivo parcialmente procesado si deseas

def threading_run(context):
    import asyncio
    asyncio.run(process_task_queue(context))

async def process_task_queue(context: ContextTypes.DEFAULT_TYPE):
    global is_processing
    is_processing = True

    while task_queue:
        task = task_queue.popleft()
        chat_id = task["chat_id"]
        input_path = task["input_path"]
        task_type = task["type"]
        quality = task.get("quality", DEFAULT_VIDEO_QUALITY)

        msg = await context.bot.send_message(chat_id, text="Procesando tu video: 0%")

        # Progreso simulado en 25% por pasos
        progress_steps = [0, 25, 50, 75, 100]
        for percent in progress_steps:
            await context.bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=f"Procesando tu video: {percent}%")
            import time
            time.sleep(1)  # simula tiempo de procesamiento

        try:
            if task_type == "compress":
                output_path = f"compressed_{input_path}"
                compress_video(input_path, output_path, quality=quality)
                await context.bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text="✅ Video comprimido listo!")
                with open(output_path, "rb") as f:
                    await context.bot.send_video(chat_id, f)
            elif task_type == "extract_audio":
                output_path = f"audio_{input_path}.mp3"
                extract_audio(input_path, output_path)
                await context.bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text="✅ Audio extraído listo!")
                with open(output_path, "rb") as f:
                    await context.bot.send_audio(chat_id, f)
        except Exception as e:
            await context.bot.send_message(chat_id, text=f"❌ Error procesando tu tarea: {e}")

        # Limpiar archivos temporales
        try:
            os.remove(input_path)
            os.remove(output_path)
        except Exception:
            pass

    is_processing = False

# ---- Función principal ----

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.FileExtension("mp4"), handle_video))
    app.add_handler(CallbackQueryHandler(handle_buttons))

    logging.info("Bot interactivo iniciado...")
    app.run_polling()

if __name__ == "__main__":
    main()
