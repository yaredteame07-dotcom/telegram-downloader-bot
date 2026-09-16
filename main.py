import os
import asyncio
import time
import requests
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# Fake HTTP Server for Render Free Tier
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# Render ከእንቅልፉ እንዳይተኛ በየ 10 ደቂቃው ራሱን Ping እንዲያደርግ
def keep_alive():
    time.sleep(30)
    render_url = os.environ.get("RENDER_EXTERNAL_URL")
    if render_url:
        while True:
            try:
                requests.get(render_url)
            except Exception:
                pass
            time.sleep(600)  # በየ 10 ደቂቃው

TOKEN = "8770860759:AAGrHcAom54k2SdEoZIsF9XrrxsmNSevQRE"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ሰላም! የ TikTok ወይም የ YouTube ቪዲዮ ሊንክ ላክልኝ።")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not ("tiktok.com" in url or "youtube.com" in url or "youtu.be" in url):
        return

    status_msg = await update.message.reply_text("⏳ ሚዲያው እየወረደ ነው... እባክህ ትንሽ ይታገሱ።")
    
    # Render RAM እና Format ስህተት እንዳይፈጥር የተስተካከለ ማዋቀሪያ
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': 'downloaded_video.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'concurrent_fragment_downloads': 1
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        await status_msg.edit_text("📤 ቪዲዮው ወርዷል! አሁን ወደ አንተ እየተላከ ነው...")
        
        with open(filename, 'rb') as video_file:
            await update.message.reply_video(video=video_file)

        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        await status_msg.edit_text(f"❌ ስህተት አጋጥሟል፦ {str(e)}")

def main():
    # HTTP Server እና Keep Alive በ Background ማስነሳት
    Thread(target=run_flask).start()
    Thread(target=keep_alive, daemon=True).start()

    # Telegram Bot ማስነሳት
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    print("🤖 ቦቱ ሥራ ጀምሯል...")
    application.run_polling()

if __name__ == "__main__":
    main()
