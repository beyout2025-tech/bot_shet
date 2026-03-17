import logging
import re
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from config import (
    GET_NAME, GET_GENDER, GET_AGE, GET_COUNTRY, 
    GET_CITY, GET_PHONE, GET_EMAIL
)
from utils.helpers import load_db, save_db
from google_services import SHEET_REGS

# دالة تبدأ عملية التسجيل
async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    course_id = int(query.data.split("_")[1])
    context.user_data["registration_data"] = {"course_id": course_id}
    
    await query.edit_message_text("الرجاء إدخال **اسمك الثلاثي** الكامل:")
    return GET_NAME

# دالة للحصول على الاسم
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    name = update.message.text
    if "registration_data" not in context.user_data:
        context.user_data["registration_data"] = {}
        
    context.user_data["registration_data"]["name"] = name
    
    keyboard = [
        [
            InlineKeyboardButton("ذكر", callback_data="gender_male"),
            InlineKeyboardButton("أنثى", callback_data="gender_female"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(f"أهلاً بك {name}، الرجاء تحديد **الجنس**:", reply_markup=reply_markup, parse_mode='Markdown')
    return GET_GENDER

# دالة للحصول على الجنس
async def get_gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    gender = "ذكر" if query.data == "gender_male" else "أنثى"
    context.user_data["registration_data"]["gender"] = gender
    
    await query.edit_message_text("الرجاء إدخال **عمرك** بالأرقام:")
    return GET_AGE

# دالة للحصول على العمر
async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    age = update.message.text
    if not age.isdigit():
        await update.message.reply_text("الرجاء إدخال رقم صحيح للعمر.")
        return GET_AGE
    
    context.user_data["registration_data"]["age"] = int(age)
    await update.message.reply_text("الرجاء إدخال **اسم البلد**:")
    return GET_COUNTRY

# دالة للحصول على البلد
async def get_country(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    country = update.message.text
    context.user_data["registration_data"]["country"] = country
    await update.message.reply_text("الرجاء إدخال **اسم المدينة**:")
    return GET_CITY

# دالة للحصول على المدينة
async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    city = update.message.text
    context.user_data["registration_data"]["city"] = city
    await update.message.reply_text("الرجاء إدخال **رقم هاتفك (للتواصل عبر الواتساب)**:")
    return GET_PHONE

# دالة للحصول على رقم الهاتف
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    phone = update.message.text
    context.user_data["registration_data"]["phone"] = phone
    await update.message.reply_text("الرجاء إدخال **بريدك الإلكتروني**:")
    return GET_EMAIL

# دالة للحصول على البريد الإلكتروني وإنهاء عملية التسجيل والربط مع الشيت
async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    email = update.message.text
    user = update.effective_user
    
    if "registration_data" not in context.user_data:
        await update.message.reply_text("⚠️ عذراً، حدث خطأ في الجلسة. يرجى البدء مجدداً عبر /start")
        return ConversationHandler.END
        
    context.user_data["registration_data"]["email"] = email
    registration_data = context.user_data.pop("registration_data")
    registration_data["user_id"] = user.id
    registration_data["status"] = "pending"

    # 1. الحفظ المحلي (JSON)
    db = load_db()
    db["registrations"].append(registration_data)
    save_db(db)
    
    # 2. الحفظ في جوجل شيت (الالتزام بـ 39 عموداً بناءً على مصفوفة التأسيس)
    try:
        course = next((c for c in db["courses"] if c["id"] == registration_data['course_id']), None)
        course_name = course['name'] if course else 'دورة غير معروفة'
        
        # جلب العناوين الفعلية من الصف الأول في الشيت
        headers = SHEET_REGS.row_values(1)
        # إنشاء صف فارغ بطول الرؤوس (الـ 39 عموداً)
        row = [""] * len(headers)

        def set_value(col, val):
            if col in headers:
                row[headers.index(col)] = val

        # --- تعبئة البيانات مطابقة تماماً لمصفوفة Cols الخاصة بك ---
        set_value("طابع_زمني", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        set_value("معرف_الطالب", f"STU-{user.id}")
        set_value("ID_المستخدم_تيليجرام", str(user.id))
        set_value("الاسم_بالعربي", registration_data["name"])
        set_value("العمر", str(registration_data.get("age", "")))
        set_value("البلد", registration_data.get("country", ""))
        set_value("المدينة", registration_data.get("city", "غير محدد"))
        set_value("رقم_الهاتف", str(registration_data["phone"]))
        set_value("البريد_الإلكتروني", registration_data["email"])
        set_value("الحالة", "قيد الانتظار")
        set_value("معرف_الدورة", str(registration_data["course_id"]))
        set_value("اسم_الدورة", course_name)
        set_value("الجنس", registration_data.get("gender", ""))
        set_value("رابط_Telegram", f"https://t.me/{user.username}" if user.username else "")
        set_value("حالة_الحظر", "لا")
        
        # إضافة الصف الكامل للشيت
        SHEET_REGS.append_row(row)
        
    except Exception as e:
        logging.error(f"Error saving to Google Sheets: {e}")

    # 3. الرد النهائي للمستخدم
    await update.message.reply_text(
        "✅ تم استلام طلبك بنجاح! سيتم مراجعته من قبل الإدارة وسيتم إرسال إشعار لك فوراً.",
        reply_markup=ReplyKeyboardRemove()
    )
    
    # 4. إشعار المديرين بطلب جديد
    admin_ids = db.get("admins", [])
    if admin_ids:
        message_to_admin = (
            f"**🔔 طلب تسجيل جديد**\n\n"
            f"**الدورة:** {course_name}\n"
            f"**الاسم:** {registration_data['name']}\n"
            f"**الهاتف:** {registration_data['phone']}\n"
            f"**الايدي:** `{user.id}`"
        )
        admin_kb = [[
            InlineKeyboardButton("✅ قبول", callback_data=f"accept_{user.id}_{registration_data['course_id']}"),
            InlineKeyboardButton("❌ رفض", callback_data=f"reject_{user.id}_{registration_data['course_id']}")
        ]]
        for admin_id in admin_ids:
            try:
                await context.bot.send_message(
                    chat_id=admin_id, 
                    text=message_to_admin, 
                    reply_markup=InlineKeyboardMarkup(admin_kb), 
                    parse_mode='Markdown'
                )
            except: 
                continue
            
    return ConversationHandler.END

# دالة للإلغاء
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('تم إلغاء العملية.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
