import os
import asyncio
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from bypasser import route_and_bypass

# Initialize Flask App for hosting compatibility
web_server = Flask(__name__)

@web_server.route('/')
def health_check():
    """
    Health check endpoint for cloud platforms like Render to monitor 
    application uptime.
    """
    return "Bot is alive and running!", 200

def run_flask():
    """
    Runs the Flask web server on a separate thread to prevent 
    blocking the Telegram polling engine.
    """
    port = int(os.environ.get("PORT", 8080))
    web_server.run(host="0.0.0.0", port=port)

# Retrieve the bot token from environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_FALLBACK")

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /start command.
    """
    await update.message.reply_text(
        "Hello!\n\nSend me any supported link shortener or landing link. "
        "I will parse the intermediate steps dynamically and return your final destination paths."
    )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Processes incoming text messages containing URLs.
    """
    # Guard clause in case message text is empty
    if not update.message or not update.message.text:
        return

    url = update.message.text.strip()
    
    if not url.startswith(("http://", "https://")):
        await update.message.reply_text("Please provide a valid URL starting with http:// or https://")
        return
        
    status_message = await update.message.reply_text("⚡ **Processing link...** Please wait.")
    
    # Process the link through our modular architecture
    result = await route_and_bypass(url)
    
    if "Error:" in result or "failed" in result.lower():
        await status_message.edit_text(f"❌ **Operation Failed**\n\n{result}")
    else:
        # python-telegram-bot uses disable_web_page_preview inside LinkPreviewOptions
        await status_message.edit_text(
            f"🎯 **Bypass Complete!**\n\n**Destination:**\n{result}",
            disable_web_page_preview=True
        )

def main():
    """
    Main entry point initializing the Application engine.
    """
    print("Starting Flask web server thread...")
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    print("Initializing python-telegram-bot application...")
    # Build the application wrapper using the token
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    print("Bot is successfully polling for updates natively! 🚀")
    # Starts the polling loop natively and safely handles the asyncio event loop setup
    application.run_polling()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Bot stopped by user.")
