from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from config import DEV_ID
from utils.helpers import load_db, save_db

# دالة لعرض القائمة الرئيسية
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = load_db()
    user_id = update.effective_user.id
    
    keyboard = [
        [InlineKeyboardButton("📚 استعراض الاقسام", callback_data="show_categories")],
        # الزر الخاص بزيادة الثقة والتواصل المباشر
        [InlineKeyboardButton("💬 التواصل مع الإدارة", url="https://t.me/Al_Mushakibot")]
    ]
    
    # إضافة زر لوحة المطور إذا كان المستخدم مسؤولاً
    if user_id in db["admins"]:
        keyboard.append([InlineKeyboardButton("🔧 لوحة المطور", callback_data="dev_panel")])
        
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # رسالة ترحيبية باسم المؤسسة لتعزيز العلامة التجارية
    welcome_text = (
        "🎓 **مؤسسة كن أنت للتدريب والتأهيل**\n"
        "مرحباً بك! نحن هنا لمساعدتك في رحلة تطوير مهاراتك.\n\n"
        "اختر من القائمة الرئيسية:"
    )
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text=welcome_text, 
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            text=welcome_text, 
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

# دالة أمر /start مع إشعار دخول مفصل للمديرين
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = user.id
    db = load_db()
    
    # إرسال إشعار للمدير عند دخول مستخدم جديد فقط
    is_new_user = user_id not in db["users"]
    if is_new_user:
        db["users"].append(user_id)
        save_db(db)
        
        # تجهيز البيانات للإشعار
        total_users = len(db["users"])
        user_name = f"{user.first_name} {user.last_name or ''}".strip()
        username = f"@{user.username}" if user.username else "لا يوجد"
        
        # القالب المخصص للإشعار
        message_to_admin = (
            f"تم دخول شخص جديد إلى البوت الخاص بك 👾\n"
            f"            -----------------------\n"
            f"• معلومات العضو الجديد .\n\n"
            f"• الاسم : {user_name}\n"
            f"• معرف : {username}\n"
            f"• الايدي : `{user_id}`\n"
            f"            -----------------------\n"
            f"• عدد الأعضاء الكلي : {total_users}"
        )
        
        # إرسال الإشعار لجميع المديرين المسجلين
        for admin_id in db["admins"]:
            try:
                # التأكد من عدم إرسال إشعار للمدير عن نفسه
                if admin_id != user_id:
                    await context.bot.send_message(
                        chat_id=admin_id,
                        text=message_to_admin,
                        parse_mode='Markdown'
                    )
            except Exception:
                continue
    
    await update.message.reply_text("أهلاً بك في بوت الدورات التدريبية!")
    await show_main_menu(update, context)
