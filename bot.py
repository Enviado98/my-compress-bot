import os
import asyncio
import tempfile
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from video_processor import compress_video, extract_audio
from config import BOT_TOKEN, DEFAULT_VIDEO_QUALITY

# Diccionario para guardar videos y configuraciones por chat
user_data = {}
# Cola de tareas
task_queue = asyncio.Queue()
# Flag de procesamiento
is_processing = False

app = Client("userbot_session", bot_token=BOT_TOKEN)

# --- Funciones del bot ---

@app.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    await message.reply(
        "¡Hola! Soy tu UserBot de compresión y extracción de audio de videos.\n"
        "Envíame un video para comenzar."
    )

@app.on_message(filters.video | filters.document)
async def handle_video(client: Client, message: Message):
    global user_data

    file = message.video or message.document
    if not file:
        await message.reply("No se detectó un video válido.")
        return

    # Guardar en archivo temporal
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4", dir="/tmp")
    await client.download_media(file, file_name=tmp_file.name)

    chat_id = message.chat.id
    user_data[chat_id] = {"input_path": tmp_file.name, "quality": DEFAULT_VIDEO_QUALITY}

    # Mostrar menú
    await show_main_menu(message)

async def show_main_menu(message: Message):
    chat_id = message.chat.id
    keyboard = [
        [InlineKeyboardButton("Comprimir video", callback_data="compress")],
        [InlineKeyboardButton("Extraer audio", callback_data="extract_audio")],
        [InlineKeyboardButton("Elegir calidad", callback_data="choose_quality")],
        [InlineKeyboardButton("Cancelar tarea", callback_data="cancel_task")]
    ]
    await message.reply("Selecciona una opción:", reply_markup=InlineKeyboardMarkup(keyboard))

@app.on_callback_query()
async def handle_buttons(client, query):
    chat_id = query.message.chat.id
    data = query.data

    if chat_id not in user_data:
        await query.answer("Primero envíame un video.")
        return

    input_path = user_data[chat_id]["input_path"]
    quality = user_data[chat_id].get("quality", DEFAULT_VIDEO_QUALITY)

    if data == "compress":
        await add_task(chat_id, "compress", input_path, quality, query.message)
        await query.message.edit_text("✅ Tu video se ha añadido a la cola de compresión.")
    elif data == "extract_audio":
        await add_task(chat_id, "extract_audio", input_path, quality, query.message)
        await query.message.edit_text("✅ Tu video se ha añadido a la cola para extraer audio.")
    elif data == "choose_quality":
        keyboard = [
            [InlineKeyboardButton("144p", callback_data="quality_144p")],
            [InlineKeyboardButton("480p", callback_data="quality_480p")],
            [InlineKeyboardButton("720p", callback_data="quality_720p")],
            [InlineKeyboardButton("1080p", callback_data="quality_1080p")]
        ]
        await query.message.edit_text("Selecciona la calidad:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data.startswith("quality_"):
        quality = data.split("_")[1]
        user_data[chat_id]["quality"] = quality
        await query.message.edit_text(f"Calidad establecida a {quality}.")
        await show_main_menu(query.message)
    elif data == "cancel_task":
        await cancel_task(chat_id)
        await query.message.edit_text("❌ Tu tarea ha sido cancelada.")

# --- Cola de tareas con asyncio ---

async def add_task(chat_id, task_type, input_path, quality, message):
    await task_queue.put({"chat_id": chat_id, "type": task_type, "input_path": input_path, "quality": quality, "message": message})
    asyncio.create_task(process_task_queue())

async def cancel_task(chat_id):
    global task_queue
    # Reconstituye la cola sin las tareas canceladas
    new_queue = asyncio.Queue()
    while not task_queue.empty():
        task = await task_queue.get()
        if task["chat_id"] != chat_id:
            await new_queue.put(task)
    task_queue = new_queue

async def process_task_queue():
    global is_processing
    if is_processing:
        return
    is_processing = True

    while not task_queue.empty():
        task = await task_queue.get()
        chat_id = task["chat_id"]
        task_type = task["type"]
        input_path = task["input_path"]
        quality = task["quality"]
        message = task["message"]

        msg = await message.reply("Procesando tu video: 0%")
        # Simula progreso
        for p in [25, 50, 75, 100]:
            await asyncio.sleep(1)
            await msg.edit_text(f"Procesando tu video: {p}%")

        try:
            if task_type == "compress":
                output_path = os.path.join("/tmp", f"compressed_{os.path.basename(input_path)}")
                compress_video(input_path, output_path, quality)
                await msg.edit_text("✅ Video comprimido listo!")
                await message.reply_video(output_path)
            elif task_type == "extract_audio":
                output_path = os.path.join("/tmp", f"audio_{os.path.basename(input_path)}.mp3")
                extract_audio(input_path, output_path)
                await msg.edit_text("✅ Audio extraído listo!")
                await message.reply_audio(output_path)
        except Exception as e:
            await message.reply(f"❌ Error procesando tu tarea: {e}")

        # Limpiar archivos temporales
        try:
            os.remove(input_path)
            os.remove(output_path)
        except Exception:
            pass

    is_processing = False

# --- Ejecutar UserBot ---
if __name__ == "__main__":
    app.run()
