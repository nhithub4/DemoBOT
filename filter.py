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
    "تعقيب", "خدمات", "النحو", "عرض خاص", "عرض", "+20", "فريق متخصص",
    "للحجز", "لطلب", "فوري", "سجل تجاري", "cv", "تكليف", "طلبة",
    "سعوده", "سعودة", "مسيار", "المسيار", "اتواصل واتساب",
    "إعلانات تجارية", "تواصل مباشر", "طلب عروض", "وظائف شاغرة", "توظيف", "تسويق",
    "مبيعات", "استفسار", "حجز", "معلومات حول", "إعلان", "إعلانات", "عرض ترويجي",
    "اتصال", "للاستفسار", "تواصل معنا", "فرص عمل", "مقابلات", "سيرة ذاتية",
    "رعاية", "تأمين", "مؤسسة", "أعمال", "مشاريع", "اتصال بنا", "إعلانات الشركات",
    "عروض خاصة", "خدمات طلابية", "عروض ترويجية", "بحث عمل", "وظيفة شاغرة", "فرصة عمل", "إعلانات توظيف",
    "تقديم طلب", "استفسار عن", "معلومات حول", "بدون إذن",
    "اسقاط", "سكليف", "اجازة", "تطبيق صحتي", "كرت تشغيل",
    "خطابه", "الخطــابه", "whatsapp.com", "+967", "967", "قروض بن التنمية", "بنك التنمية", "سنرد", "وسنرد"
]

def normalize_arabic_text(text):
    # الخطوة 1: إزالة الأحرف غير الضرورية وتطبيع المسافات
    text = re.sub(r'[ـ*]', '', text)  # إزالة الأحرف غير الضرورية مثل التمديد أو النجوم
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

    # التحقق من وجود كلمات معينة في نفس الجملة
    forbidden_combinations = [
        (r'\bتكاليف\b', r'\bبرزنتيشن\b'),
        (r'\bعروض\b', r'\bمضمون\b'),
        (r'\bبوربوينت\b', r'\bواجبات\b'),
        (r'\bباوربوينت\b', r'\bواجبات\b'),
        (r'\bبوربوينت\b', r'\bمشاريع\b'),
        (r'\bباوربوينت\b', r'\bمشاريع\b'),
        (r'\bحل\b', r'\bخرائط مفاهيم\b'),
        (r'\bمشروع\b', r'\bتكاليف\b'),
        (r'\bحل\b', r'\bمضمون\b'),
        (r'\b967', None),  # التحقق من الأرقام المحظورة
    ]
    
    for pattern1, pattern2 in forbidden_combinations:
        if pattern2:
            if re.search(f'{pattern1}.*{pattern2}|{pattern2}.*{pattern1}', normalized_text):
                return True
        else:
            if re.search(pattern1, normalized_text):
                return True

    # التحقق من وجود روابط أو إشارات أو أرقام هواتف
    if re.search(r'http[s]?://|www\.|t\.me/|@\w+|wa\.me/\d+', normalized_text):
        return True

    return False

async def filter_messages(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    chat = update.message.chat

    # تحقق مما إذا كانت الرسالة قد أُرسلت في مجموعة فقط
    if chat.type not in ['group', 'supergroup']:
        return

    # تحقق مما إذا كان المرسل هو بوت
    if user.is_bot:
        return

    # الحصول على حالة العضو في الدردشة
    try:
        chat_member = await context.bot.get_chat_member(chat.id, user.id)
    except Exception as e:
        logger.error(f"Error fetching chat member: {e}")
        return

    # تجاهل الرسائل من المسؤولين والمالكين
    if chat_member.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
        return

    # التحقق من وجود محتوى محظور
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
