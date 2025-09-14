import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import API_ID, API_HASH, SESSION_NAME, DEFAULT_VIDEO_QUALITY
from video_processor import compress_video, extract_audio
from collections import deque
import os

logging.basicConfig(level=logging.INFO)

# Cola de tareas y flag de ocupado
task_queue = deque()
is_processing = False

# Diccionario para guardar videos y configuraciones de cada chat
user_data = {}

# ---- Funciones ----
async def start_handler(client, message):
    await message.reply_text(
        "¡Hola! Soy tu userbot de compresión y extracción de audio de videos.\n"
        "Envíame un video para empezar."
    )

async def handle_video(client, message):
    global is_processing

    file = message.video or message.document
    if not file:
        await message.reply_text("No se detectó un video válido.")
        return

    input_path = f"temp_{file.file_name}" if hasattr(file, "file_name") else "temp_video.mp4"
    await file.download(input_path)

    chat_id = message.chat.id
    user_data[chat_id] = {"input_path": input_path, "quality": DEFAULT_VIDEO_QUALITY}

    # Comprobamos si el bot está ocupado
    if is_processing:
        task_queue.append(chat_id)
        await message.reply_text(f"🤖 Bot ocupado. Tu tarea ha sido añadida a la cola. Posición en cola: {len(task_queue)}")
        return

    # Mostrar menú interactivo
    await show_main_menu(client, message)

async def show_main_menu(client, message):
    chat_id = message.chat.id
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Comprimir video", callback_data="compress")],
        [InlineKeyboardButton("Extraer audio", callback_data="extract_audio")],
        [InlineKeyboardButton("Elegir calidad", callback_data="choose_quality")],
        [InlineKeyboardButton("Cancelar tarea", callback_data="cancel_task")]
    ])
    await message.reply_text("Selecciona una opción:", reply_markup=keyboard)

# ---- Manejo de botones ----
async def handle_buttons(client, callback_query):
    chat_id = callback_query.message.chat.id
    data = callback_query.data

    if chat_id not in user_data:
        await callback_query.message.edit_text("Primero envíame un video.")
        return

    input_path = user_data[chat_id]["input_path"]
    quality = user_data[chat_id].get("quality", DEFAULT_VIDEO_QUALITY)

    if data == "compress":
        add_task(chat_id, "compress", input_path, quality, callback_query.message)
        await callback_query.message.edit_text("✅ Tu video se ha añadido a la cola de compresión.")
    elif data == "extract_audio":
        add_task(chat_id, "extract_audio", input_path, quality, callback_query.message)
        await callback_query.message.edit_text("✅ Tu video se ha añadido a la cola para extraer audio.")
    elif data.startswith("quality_"):
        quality = data.split("_")[1]
        user_data[chat_id]["quality"] = quality
        await callback_query.message.edit_text(f"Calidad establecida a {quality}.")
        await show_main_menu(client, callback_query.message)
    elif data == "choose_quality":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("144p", callback_data="quality_144p")],
            [InlineKeyboardButton("240p", callback_data="quality_240p")],
            [InlineKeyboardButton("360p", callback_data="quality_360p")],
            [InlineKeyboardButton("480p", callback_data="quality_480p")],
            [InlineKeyboardButton("720p", callback_data="quality_720p")],
            [InlineKeyboardButton("1080p", callback_data="quality_1080p")]
        ])
        await callback_query.message.edit_text("Selecciona la calidad:", reply_markup=keyboard)
    elif data == "cancel_task":
        # Aquí agregaremos la lógica de cancelar tarea después
        await callback_query.message.edit_text("⚠️ Tu tarea será cancelada pronto (funcionalidad pendiente).")

# ---- Cola de tareas ----
def add_task(chat_id, task_type, input_path, quality, message):
    task_queue.append({"chat_id": chat_id, "type": task_type, "input_path": input_path, "quality": quality, "message": message})
    global is_processing
    if not is_processing:
        asyncio.create_task(process_task_queue())

async def process_task_queue():
    global is_processing
    is_processing = True

    while task_queue:
        task = task_queue.popleft()
        chat_id = task["chat_id"]
        input_path = task["input_path"]
        task_type = task["type"]
        quality = task.get("quality", DEFAULT_VIDEO_QUALITY)
        message = task["message"]

        msg = await message.reply_text("Procesando tu video: 0%")

        # Progreso simulado (MoviePy no da callback real)
        steps = [0, 25, 50, 75, 100]
        for percent in steps:
            await asyncio.sleep(1)  # Simula progreso
            await msg.edit_text(f"Procesando tu video: {percent}%")

        if task_type == "compress":
            output_path = f"compressed_{input_path}"
            compress_video(input_path, output_path, quality=quality)
            await msg.edit_text("✅ Video comprimido listo!")
            await message.reply_video(output_path)
        elif task_type == "extract_audio":
            output_path = f"audio_{input_path}.mp3"
            extract_audio(input_path, output_path)
            await msg.edit_text("✅ Audio extraído listo!")
            await message.reply_audio(output_path)

        try:
            os.remove(input_path)
            os.remove(output_path)
        except Exception:
            pass

    is_processing = False

# ---- MAIN ----
app = Client(SESSION_NAME, api_id=API_ID, api_hash=API_HASH)

app.add_handler(filters.command("start"), start_handler)
app.add_handler(filters.video | filters.document, handle_video)
app.add_handler(filters.callback_query, handle_buttons)

if __name__ == "__main__":
    app.run()
