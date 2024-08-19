import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
from info import BOT_TOKEN
from commands import ban, restrict, unrestrict
from replies import reply_to_salam, reply_to_yabot, reply_to_bot, reply_to_name
from reveal import reveal
from pin import add_pin_handlers
from filter import add_filters

# إعدادات تسجيل الأحداث
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# أمر الترحيب عند استخدام /start
async def start(update: Update, context: CallbackContext) -> None:
    welcome_message = (
        "مرحبًا، أنا بوت متطور مصمم لإدارة مجموعات التليجرام.\n\n"
        "ما أقدمه:\n\n"
        "منع الإعلانات بجميع أشكالها:\n"
        "• ضمن الرسائل النصية 📄\n"
        "• ضمن الروابط 📎\n\n"
        "الحماية من:\n"
        "• الإرهاب والتطرف\n"
        "• المحتوى الإباحي 🔞\n"
        "• الحسابات الوهمية (البوتات) عبر الحظر أو التقييد\n\n"
        "وأيضًا العديد من المزايا الأخرى التي تسهم في حماية وتسريع إدارة مجموعتك.\n\n"
        "للاستفسار والتفعيل، تواصل معي عبر: @Y305F"
    )
    keyboard = [
        [InlineKeyboardButton("المطور", url='https://t.me/Y305F')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

# تابع تشغيل البوت
if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # إضافة معالجات الأوامر
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex(r'^(طرد|حظر)$'), ban))
    application.add_handler(MessageHandler(filters.Regex(r'^(قيد)$'), restrict))
    application.add_handler(MessageHandler(filters.Regex(r'^(إلغاء القيد)$'), unrestrict))
    
    # إضافة معالجات للردود من replies.py
    application.add_handler(MessageHandler(filters.Regex(r'السلام عليكم'), reply_to_salam))
    application.add_handler(MessageHandler(filters.Regex(r'يابوت'), reply_to_yabot))
    application.add_handler(MessageHandler(filters.Regex(r'بوت'), reply_to_bot))
    application.add_handler(MessageHandler(filters.Regex(r'لاتزودها'), reply_to_name))

    # إضافة معالج للأمر /كشف
    application.add_handler(MessageHandler(filters.Regex(r'^(كشف)$'), reveal))

    # إضافة معالجات لتثبيت الرسائل
    add_pin_handlers(application)

    # إضافة فلتر الرسائل من filter.py
    add_filters(application)

    # إضافة فلتر للوسائط من media_filter.py
    add_media_filter(application)

    # بدء تشغيل البوت
    application.run_polling()
