import os
import asyncio
import time
import requests
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    time.sleep(30)
    render_url = os.environ.get("RENDER_EXTERNAL_URL")
    if render_url:
        while True:
            try:
                requests.get(render_url)
            except Exception:
                pass
            time.sleep(600)

TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ሰላም! የ TikTok ወይም የ YouTube ቪዲዮ ሊንክ ላክልኝ።")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not ("tiktok.com" in url or "youtube.com" in url or "youtu.be" in url):
        return

    status_msg = await update.message.reply_text("⏳ ሚዲያው እየወረደ ነው... እባክህ ትንሽ ይታገሱ።")
    
    # አጫጭር vt.tiktok.com ሊንኮች ወደ ዋናው ሊንክ እንዲቀየሩ ማድረግ
    if "vt.tiktok.com" in url or "vm.tiktok.com" in url:
        try:
            res = requests.head(url, allow_redirects=True, timeout=10)
            url = res.url
        except Exception:
            pass

    # TikTok እና YouTube እገዳዎችን የሚያልፍ ማዋቀሪያ
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': 'downloaded_video.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'concurrent_fragment_downloads': 1,
        'extractor_args': {
            'tiktok': {
                'app_version': '30.0.0',
                'manifest_app_version': '30.0.0',
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
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
    Thread(target=run_flask).start()
    Thread(target=keep_alive, daemon=True).start()

    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    print("🤖 ቦቱ ሥራ ጀምሯል...")
    application.run_polling()

if __name__ == "__main__":
    main()
