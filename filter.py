import logging
import re
from telegram import Update
from telegram.ext import CallbackContext, MessageHandler, filters

# إعدادات تسجيل الأحداث
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# قائمة الكلمات التي يجب تصفيتها
FORBIDDEN_WORDS = [
    # قائمة الكلمات المحظورة كما هي
]

def normalize_arabic_text(text):
    # تطبيع النص كما هو
    text = re.sub(r'[ــ*]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    normalization_map = {
        'ة': 'ه',
        'ال': '',
    }
    text = ''.join(normalization_map.get(char, char) for char in text)
    text = re.sub(r'\bال', '', text)
    text = re.sub(r'(.)\1+', r'\1', text)
    text = re.sub(r'س+ل+ا+م+م* ع+ل+ي+ك+م*', 'السلام عليكم', text)
    text = re.sub(r'(\d)\s+(\d)', r'\1\2', text)
    return text

def contains_forbidden_content(text):
    normalized_text = normalize_arabic_text(text)
    normalized_forbidden_words = [normalize_arabic_text(word) for word in FORBIDDEN_WORDS]
    for word in normalized_forbidden_words:
        if re.search(rf'\b{re.escape(word)}\b', normalized_text):
            return True
    if re.search(r'http[s]?://|www\.', normalized_text):
        return True
    if re.search(r'\+?\d{9,}', normalized_text):
        return True
    if 't.me/' in normalized_text:
        return True
    if re.search(r'@\w+', normalized_text):
        return True
    return False

async def filter_messages(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    chat = update.message.chat
    if chat.type in ['group', 'supergroup', 'channel']:
        if contains_forbidden_content(update.message.text):
            try:
                await update.message.delete()
                await update.message.reply_text(
                    f"تم حذف رسالة تحتوي على محتوى محظور من قِبل {user.full_name}."
                )
            except Exception as e:
                logger.error(f"خطأ في حذف الرسالة: {e}")

def add_filters(application) -> None:
    # إضافة معالج الرسائل
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filter_messages))
