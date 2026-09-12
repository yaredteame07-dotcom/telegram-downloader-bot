import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

TOKEN = "8770860759:AAEB8trinXchKw7FdXSotDMu0Sd-Y8DaVwc"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ሰላም! 🎬 የቪዲዮ እና ፎቶ ማውረጃ ቦት ነኝ።\nእባክዎ የ TikTok ወይም የ YouTube ሊንክ ይላኩልኝ!")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_url = update.message.text.strip()
    url = raw_url.split('?')[0]
    
    if not url.startswith("http"):
        await update.message.reply_text("⚠️ እባክዎ ትክክለኛ ሊንክ ያስገቡ!")
        return

    status_msg = await update.message.reply_text("⏳ ሚዲያው እየወረደ ነው... እባክዎ ትንሽ ይታገሱ።")

    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloaded_media.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    try:
        loop = asyncio.get_event_loop()
        def run_ydl():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        await loop.run_in_executor(None, run_ydl)

        downloaded_files = [f for f in os.listdir('.') if f.startswith("downloaded_media.")]

        if downloaded_files:
            await status_msg.edit_text("📤 ፋይሉ ወደ ቴሌግራም እየተጫነ ነው...")
            for downloaded_file in downloaded_files:
                ext = downloaded_file.split('.')[-1].lower()
                with open(downloaded_file, 'rb') as media_file:
                    if ext in ['mp4', 'mkv', 'webm', 'mov']:
                        await update.message.reply_video(video=media_file, caption="✅ ቪዲዮው ተዘጋጅቷል!")
                    elif ext in ['jpg', 'jpeg', 'png', 'webp']:
                        await update.message.reply_photo(photo=media_file, caption="✅ ፎቶው ተዘጋጅቷል!")
                    else:
                        await update.message.reply_document(document=media_file, caption="✅ ፋይሉ ተዘጋጅቷል!")
                os.remove(downloaded_file)
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ ፋይሉን ማውረድ አልተቻለም።")

    except Exception as e:
        await status_msg.edit_text(f"❌ ስህተት አጋጥሟል፦ {str(e)}")
        for f in os.listdir('.'):
            if f.startswith("downloaded_media."):
                os.remove(f)

if __name__ == '__main__':
    app = ApplicationBuilder()\
        .token(TOKEN)\
        .connect_timeout(60.0)\
        .read_timeout(60.0)\
        .write_timeout(60.0)\
        .get_updates_read_timeout(60.0)\
        .build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    print("🤖 ቦቱ ስራ ጀምሯል...")
    app.run_polling()
