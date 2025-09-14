import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from video_processor import compress_video, extract_audio
from collections import deque
import threading

# Configuración desde variables de entorno
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN", None)  # Opcional si quieres usar bot
DEFAULT_VIDEO_QUALITY = os.getenv("DEFAULT_VIDEO_QUALITY", "720p")

# Inicializar cliente Pyrogram
app = Client("userbot_session", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Cola de tareas y estado
task_queue = deque()
is_processing = False
user_data = {}  # Guardar datos de cada chat

# ---- Funciones ----

def get_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Comprimir video", callback_data="compress")],
        [InlineKeyboardButton("Extraer audio", callback_data="extract_audio")],
        [InlineKeyboardButton("Elegir calidad", callback_data="choose_quality")],
        [InlineKeyboardButton("Cancelar tarea", callback_data="cancel_task")]
    ])

def get_quality_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("144p", callback_data="quality_144p"),
         InlineKeyboardButton("240p", callback_data="quality_240p")],
        [InlineKeyboardButton("360p", callback_data="quality_360p"),
         InlineKeyboardButton("480p", callback_data="quality_480p")],
        [InlineKeyboardButton("720p", callback_data="quality_720p"),
         InlineKeyboardButton("1080p", callback_data="quality_1080p")]
    ])

async def send_main_menu(chat_id):
    await app.send_message(chat_id, "Selecciona una opción:", reply_markup=get_main_keyboard())

# ---- Manejo de videos ----

@app.on_message(filters.video | filters.document)
async def handle_video(client, message: Message):
    chat_id = message.chat.id
    file = message.video or message.document
    if not file:
        await message.reply_text("No se detectó un video válido.")
        return

    input_path = f"temp_{file.file_name}" if hasattr(file, "file_name") else "temp_video.mp4"
    await file.download(file_name=input_path)
    user_data[chat_id] = {"input_path": input_path, "quality": DEFAULT_VIDEO_QUALITY}

    global is_processing
    if is_processing:
        task_queue.append(chat_id)
        await message.reply_text(f"🤖 Bot ocupado. Tu tarea se añadió a la cola. Posición en cola: {len(task_queue)}")
        return

    await send_main_menu(chat_id)

# ---- Manejo de botones ----

@app.on_callback_query()
async def handle_buttons(client, callback_query):
    chat_id = callback_query.message.chat.id
    data = callback_query.data

    if chat_id not in user_data:
        await callback_query.answer("Primero envíame un video.", show_alert=True)
        return

    if data == "compress":
        add_task(chat_id, "compress")
        await callback_query.edit_message_text("✅ Video añadido a la cola de compresión.")
    elif data == "extract_audio":
        add_task(chat_id, "extract_audio")
        await callback_query.edit_message_text("✅ Video añadido a la cola de extracción de audio.")
    elif data == "choose_quality":
        await callback_query.edit_message_text("Selecciona la calidad:", reply_markup=get_quality_keyboard())
    elif data.startswith("quality_"):
        quality = data.split("_")[1]
        user_data[chat_id]["quality"] = quality
        await callback_query.edit_message_text(f"Calidad establecida a {quality}.")
        await send_main_menu(chat_id)
    elif data == "cancel_task":
        cancel_task(chat_id)
        await callback_query.edit_message_text("❌ Tu tarea ha sido cancelada.")

# ---- Cola de tareas ----

def add_task(chat_id, task_type):
    task_queue.append({"chat_id": chat_id, "type": task_type})
    if not is_processing:
        threading.Thread(target=process_queue_thread).start()

def cancel_task(chat_id):
    global task_queue
    task_queue = deque([t for t in task_queue if t["chat_id"] != chat_id])

def process_queue_thread():
    asyncio.run(process_task_queue())

async def process_task_queue():
    global is_processing
    is_processing = True

    while task_queue:
        task = task_queue.popleft()
        chat_id = task["chat_id"]
        task_type = task["type"]
        input_path = user_data[chat_id]["input_path"]
        quality = user_data[chat_id].get("quality", DEFAULT_VIDEO_QUALITY)

        msg = await app.send_message(chat_id, "Procesando tu video: 0%")

        # Simular progreso
        if task_type == "compress":
            output_path = f"compressed_{input_path}"
            for percent in [25, 50, 75]:
                await asyncio.sleep(1)
                await app.edit_message_text(chat_id, msg.message_id, f"Procesando tu video: {percent}%")
            compress_video(input_path, output_path, quality=quality)
            await app.edit_message_text(chat_id, msg.message_id, "✅ Video comprimido listo!")
            await app.send_video(chat_id, output_path)
        elif task_type == "extract_audio":
            output_path = f"audio_{input_path}.mp3"
            for percent in [25, 50, 75]:
                await asyncio.sleep(1)
                await app.edit_message_text(chat_id, msg.message_id, f"Procesando tu video: {percent}%")
            extract_audio(input_path, output_path)
            await app.edit_message_text(chat_id, msg.message_id, "✅ Audio extraído listo!")
            await app.send_audio(chat_id, output_path)

        # Limpiar archivos
        try:
            os.remove(input_path)
            os.remove(output_path)
        except:
            pass

    is_processing = False

# ---- Ejecutar ----

if __name__ == "__main__":
    print("Userbot iniciado...")
    app.run()
