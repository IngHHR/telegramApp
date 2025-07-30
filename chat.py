import os
import asyncio
import nest_asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
from utils import (
    save_reminder,
    init_db,
    add_task,
    list_tasks,
    add_note,
    add_expense,
    get_due_reminders,
    mark_reminder_sent,
)

# Cargar token desde .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Inicializar base de datos
init_db()

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text("Hola Harold! Soy tu asistente personal en Telegram.")
    await update.message.reply_text(f"Tu chat ID es: {chat_id}")

# Comando /tarea
async def task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ' '.join(context.args)
    if text:
        add_task(text)
        await update.message.reply_text(f"Tarea agregada: {text}")
    else:
        await update.message.reply_text("Por favor escribe una tarea después de /tarea")

# Comando /tareas
async def show_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tasks = list_tasks()
    if not tasks:
        await update.message.reply_text("No tienes tareas pendientes.")
    else:
        msg = "\n".join(f"{id}. {text}" for id, text in tasks)
        await update.message.reply_text(f"Tareas:\n{msg}")

# Comando /nota
async def note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ' '.join(context.args)
    if text:
        add_note(text)
        await update.message.reply_text("Nota guardada.")
    else:
        await update.message.reply_text("Por favor escribe una nota después de /nota")

# Comando /gasto
async def gasto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = float(context.args[0].replace("$", "").replace(",", ""))
        category = context.args[1]
        note = ' '.join(context.args[2:])
        add_expense(amount, category, note)
        await update.message.reply_text("Gasto registrado correctamente.")
    except Exception:
        await update.message.reply_text("Usa el formato: /gasto 120 comida almuerzo con Juan")

# Comando /recordatorio
async def add_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = context.args
        if len(data) < 3:
            await update.message.reply_text("Usa el formato: /recordatorio YYYY-MM-DD HH:MM mensaje")
            return

        date_str = data[0]
        time_str = data[1]
        message = " ".join(data[2:])
        reminder_time = f"{date_str} {time_str}"

        chat_id = update.effective_chat.id
        save_reminder(reminder_time, message, chat_id)
        await update.message.reply_text("✅ Recordatorio guardado correctamente.")
    except Exception as e:
        await update.message.reply_text(f"Error al guardar el recordatorio: {e}")

# Tarea en segundo plano para enviar recordatorios
async def check_reminders(application):
    while True:
        reminders = get_due_reminders()
        for reminder_id, message, chat_id in reminders:
            try:
                await application.bot.send_message(
                    chat_id=chat_id,
                    text=f"⏰ Recordatorio: {message}"
                )
                mark_reminder_sent(reminder_id)
            except Exception as e:
                print(f"❌ Error al enviar recordatorio: {e}")
        await asyncio.sleep(60)

# Inicializar bot
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# Registrar comandos
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("tarea", task))
app.add_handler(CommandHandler("tareas", show_tasks))
app.add_handler(CommandHandler("nota", note))
app.add_handler(CommandHandler("gasto", gasto))
app.add_handler(CommandHandler("recordatorio", add_reminder))

print("✅ Bot corriendo...")
import nest_asyncio

if __name__ == "__main__":
    nest_asyncio.apply()

    async def run_bot():
        # Iniciar la tarea de recordatorios en paralelo
        asyncio.create_task(check_reminders(app))
        # Iniciar el bot
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        print("✅ Bot escuchando comandos...")
        # Mantener en ejecución
        await asyncio.Event().wait()

    asyncio.run(run_bot())

