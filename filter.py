# This filter.py
import logging
import re
from telegram import Update, ChatMember
from telegram.ext import CallbackContext, MessageHandler, filters

# إعدادات تسجيل الأحداث
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# قائمة الكلمات التي يجب تصفيتها
FORBIDDEN_WORDS = [
    "967", "بحوث", "يحل", "+966", "عمل", "لتواصل", "للتواصل", "التواصل",
    "تعقيب", "خدمات", "واجبات", "النحو", "عرض خاص", "عرض", "+20", "فريق متخصص",
    "للحجز", "لطلب", "واجــبات*", "فوري", "سجل تجاري", "cv", "تكليف", "طلبة",
    "سعوده", "سعودة", "مسيار", "المسيار", "اتواصل واتساب",
    "إعلانات تجارية", "تواصل مباشر", "طلب عروض", "وظائف شاغرة", "توظيف", "تسويق",
    "مبيعات", "استفسار", "حجز", "معلومات حول", "إعلان", "إعلانات", "عرض ترويجي",
    "اتصال", "للاستفسار", "تواصل معنا", "فرص عمل", "مقابلات", "تسجيل", "سيرة ذاتية",
    "رعاية", "تأمين", "مؤسسة", "أعمال", "مشاريع", "اتصال بنا", "إعلانات الشركات",
    "عروض خاصة", "عروض ترويجية", "بحث عمل", "وظيفة شاغرة", "فرصة عمل", "إعلانات توظيف",
    "تقديم طلب", "استفسار عن", "معلومات حول", "بدون إذن",
    "اسقاط", "سكليف", "اجازة", "تطبيق صحتي", "كرت تشغيل",
    "خطابه", "الخطــابه", "whatsapp.com" 
]

def normalize_arabic_text(text):
    # الخطوة 1: إزالة الأحرف غير الضرورية وتطبيع المسافات
    text = re.sub(r'[ــ*]', '', text)  # إزالة الأحرف غير الضرورية مثل التمديد أو النجوم
    text = re.sub(r'\s+', ' ', text).strip()  # إزالة المسافات الزائدة

    # الخطوة 2: استبدال 'ة' بـ 'ه' ومعالجة تطبيع "ال"
    normalization_map = {
        'ة': 'ه',  # استبدال 'ة' بـ 'ه'
        'ال': '',  # إزالة بادئة "ال"
    }
    text = ''.join(normalization_map.get(char, char) for char in text)
    text = re.sub(r'\bال', '', text)  # إزالة بادئة "ال" في بداية الكلمات

    # الخطوة 3: تطبيع الأحرف المكررة
    text = re.sub(r'(.)\1+', r'\1', text)  # تقليص الأحرف المكررة إلى حرف واحد

    # الخطوة 4: تطبيع اختلافات التحية
    text = re.sub(r'س+ل+ا+م+م* ع+ل+ي+ك+م*', 'السلام عليكم', text)

    # الخطوة 5: توحيد الأرقام بإزالة المسافات
    text = re.sub(r'(\d)\s+(\d)', r'\1\2', text)  # إزالة المسافات بين الأرقام

    return text

def contains_forbidden_content(text):
    # تطبيع النص
    normalized_text = normalize_arabic_text(text)

    # تطبيع الكلمات المحظورة
    normalized_forbidden_words = [normalize_arabic_text(word) for word in FORBIDDEN_WORDS]

    # التحقق من وجود كلمات محظورة
    for word in normalized_forbidden_words:
        if re.search(rf'\b{re.escape(word)}\b', normalized_text):
            return True

    # التحقق من وجود كلمات "تكاليف" و"برزنتيشن" في نفس الجملة
    if re.search(r'\bتكاليف\b.*\bبرزنتيشن\b|\bبرزنتيشن\b.*\bتكاليف\b', normalized_text):
        return True

    # التحقق من وجود كلمات "مشروع" و"تكاليف" في نفس الجملة
    if re.search(r'\bمشروع\b.*\bتكاليف\b|\bتكاليف\b.*\bمشروع\b', normalized_text):
        return True

    # التحقق من وجود روابط، أرقام هواتف، أو إشارات
    if re.search(r'http[s]?://|www\.', normalized_text):  # التحقق من وجود روابط
        return True
    #if re.search(r'\+?\d{9,}', normalized_text):  # التحقق من وجود أرقام هواتف
       # return True
    if 't.me/' in normalized_text:  # التحقق من روابط تليجرام
        return True
    if re.search(r'@\w+', normalized_text):  # التحقق من وجود إشارات
        return True

    return False

async def filter_messages(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    chat = update.message.chat

    # تحقق مما إذا كانت الرسالة قد أُرسلت باسم المجموعة أو القناة
    if chat.type in ['group', 'supergroup', 'channel']:
        if update.message.from_user.is_bot:  # تحقق مما إذا كان المرسل هو بوت
            return

    # الحصول على حالة العضو في الدردشة
    chat_member = await context.bot.get_chat_member(chat.id, user.id)
    if chat_member.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
        # المستخدم هو مسؤول أو مالك، يسمح بالرسالة
        return

    message_text = update.message.text
    if contains_forbidden_content(message_text):
        try:
            await update.message.delete()
            await update.message.reply_text("تم حذف الرسالة لاحتوائها على محتوى غير مسموح به.")
        except Exception as e:
            logger.error(f"Error deleting message: {e}")

# وظيفة لإضافة معالج الرسائل
def add_filters(application):
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filter_messages))
