import os
import sys
import asyncio
import threading
from flask import Flask

# --- ULTIMATE PYTHON 3.14+ MOCK PATCH ENGINE ---
# Create an explicit event loop for the main thread immediately
try:
    _loop = asyncio.get_event_loop()
except RuntimeError:
    _loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_loop)

# Create a fake mock class to replace pyrogram.sync without throwing errors
class MockSyncModule:
    def __getattr__(self, name):
        # Dynamically return a dummy function or object for anything Pyrogram asks for
        return lambda *args, **kwargs: None

# Inject our fake module directly into Python's memory cache before Pyrogram runs
sys.modules["pyrogram.sync"] = MockSyncModule()
# -----------------------------------------------

# Now Pyrogram will import safely, thinking its sync utilities are fully loaded
from pyrogram import Client, filters
from pyrogram.types import Message
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
    blocking the Pyrogram polling engine.
    """
    port = int(os.environ.get("PORT", 8080))
    web_server.run(host="0.0.0.0", port=port)

# Pulling the token directly from your environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_FALLBACK")

# Initializing the Pyrogram client
app = Client("bypass_bot_session", bot_token=BOT_TOKEN)

@app.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    await message.reply_text(
        "Hello!\n\nSend me any supported link shortener or landing link. "
        "I will parse the intermediate steps dynamically and return your final destination paths."
    )

@app.on_message(filters.text & filters.private & ~filters.command(["start"]))
async def message_handler(client: Client, message: Message):
    url = message.text.strip()
    
    if not url.startswith(("http://", "https://")):
        await message.reply_text("Please provide a valid URL starting with http:// or https://")
        return
        
    status_message = await message.reply_text("⚡ **Processing link...** Please wait.")
    
    result = await route_and_bypass(url)
    
    if "Error:" in result or "failed" in result.lower():
        await status_message.edit_text(f"❌ **Operation Failed**\n\n`{result}`")
    else:
        await status_message.edit_text(
            f"🎯 **Bypass Complete!**\n\n**Destination:**\n{result}",
            disable_web_page_preview=True
        )

async def main():
    """
    Main asynchronous entry point using Pyrogram's pure async context manager.
    """
    print("Starting Pyrogram client asynchronously...")
    async with app:
        print("Bot is successfully polling for updates! 🚀")
        while True:
            await asyncio.sleep(3600)

if __name__ == "__main__":
    print("Starting Flask web server thread...")
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    try:
        _loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Bot stopped by user.")
