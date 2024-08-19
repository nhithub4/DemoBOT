from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

# دالة لتثبيت الرسالة
async def pin_message(update: Update, context: CallbackContext) -> None:
    # تحقق مما إذا كانت الرسالة التي تم الرد عليها موجودة
    if update.message.reply_to_message:
        try:
            # قم بتثبيت الرسالة
            await update.message.reply_to_message.pin()
            # رد على المستخدم بتأكيد التثبيت
            await update.message.reply_text("تم تثبيت الرسالة بنجاح.")
        except Exception as e:
            # في حال حدوث خطأ، أبلغ المستخدم
            await update.message.reply_text(f"حدث خطأ أثناء محاولة تثبيت الرسالة: {str(e)}")
    else:
        # إذا لم تكن هناك رسالة يتم الرد عليها، أبلغ المستخدم
        await update.message.reply_text("يرجى الرد على الرسالة التي ترغب في تثبيتها.")

# إضافة معالجات أوامر التثبيت
def add_pin_handlers(application):
    # قم بإضافة معالج الأمر /pin
    pin_handler = CommandHandler("pin", pin_message)
    application.add_handler(pin_handler)
