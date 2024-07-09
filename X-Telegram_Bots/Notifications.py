from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes


Token: Final = "6852420818:AAFTPeZhSb2i_-GGUzXrsgMMGdjncAZTt1I"
Bot_Username: Final = "@BinanceNotification117Bot"

#Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Starting Push Notifications for Binance Bot V1.0")

#Responses
def handle_response(text: str) -> str:
    processed: str = text.lower()
    if "hello" in processed:
        return "Hey There"
    
    return "I do not understand"

async def handle_message(update: Update, context:  ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    response: str = handle_response(text)
    await update.message.reply_text(response)

    

async def error(update: Update, context:  ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')




def run():
    print("Starting")
    app = Application.builder().token(Token).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))

    #Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)
    
    print("2")
    app.run_polling(poll_interval=3)


run()