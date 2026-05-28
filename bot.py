import os
from pyrogram import Client, filters
from pyrogram.types import Message
from bypasser import route_and_bypass

# Pulling the token directly from your environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_FALLBACK")

# Initializing the client cleanly. 
# Pyrogram will automatically search for 'API_ID' and 'API_HASH' in your environment.
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

if __name__ == "__main__":
    print("Initializing components and starting standard polling engine...")
    app.run()