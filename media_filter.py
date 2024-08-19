from telegram import Update
from telegram.ext import CallbackContext, MessageHandler, filters

async def filter_media(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    if update.message.photo:
        await update.message.reply_text(f"تمت مشاركة صورة من قِبل {user.full_name}.")
        await update.message.delete()
    elif update.message.video:
        await update.message.reply_text(f"تمت مشاركة فيديو من قِبل {user.full_name}.")
        await update.message.delete()
    elif update.message.audio:
        await update.message.reply_text(f"تمت مشاركة صوت من قِبل {user.full_name}.")
        await update.message.delete()
    elif update.message.document:
        await update.message.reply_text(f"تمت مشاركة مستند من قِبل {user.full_name}.")
        await update.message.delete()

def add_media_filter(application):
    media_filter = MessageHandler(
        filters.PHOTO | filters.VIDEO | filters.AUDIO | filters.Document(), 
        filter_media
    )
    application.add_handler(media_filter)
