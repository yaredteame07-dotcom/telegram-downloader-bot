import os
import asyncio
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# Fake HTTP Server for Render Free Tier
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

TOKEN = "7953259837:AAENJ_vVfXz80hS3tQp26TjUoM7S5z_1-u0"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ሰላም! የ TikTok ወይም የ YouTube ቪዲዮ ሊንክ ላክልኝ።")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not ("tiktok.com" in url or "youtube.com" in url or "youtu.be" in url):
        return

    status_msg = await update.message.reply_text("ቪዲዮው እየወረደ ነው... እባክህ ትንሽ ጠብቅ።")

    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloaded_video.%(ext)s',
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        await status_msg.edit_text("ቪዲዮው ወርዷል! አሁን ወደ አንተ እየተላከ ነው...")

        with open(filename, 'rb') as video_file:
            await update.message.reply_video(video=video_file)

        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        await status_msg.edit_text(f"ስህተት ተከሰተ፦ {str(e)}")

def main():
    # HTTP Server በ Background እንዲሰራ ማስነሳት
    Thread(target=run_flask).start()

    # Telegram Bot ማስነሳት
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    print("🤖 ቦቱ ሥራ ጀምሯል...")
    application.run_polling()

if __name__ == "__main__":
    main()
