import os

# --- إعدادات الربط الأساسية ---
# توكن البوت (يتم جلبه من متغيرات النظام)
BOT_TOKEN = os.getenv("BOT_TOKEN")

# معرف المطور الرئيسي
DEV_ID = 873158772

# معرف السبريدشيت (MASTER_SS_ID)
MASTER_SS_ID = "1M9osk6OpItLJKmylYz0bUlmjF99WWE_zj2Zk7LAaOkU"

# اسم ملف قاعدة البيانات المحلية
DB_FILE = "db.json"

# اسم ملف مفتاح الخدمة الخاص بجوجل
SERVICE_ACCOUNT_FILE = "service_account.json"

# --- تعريف حالات المحادثة (Conversation States) ---

# حالات تسجيل الطلاب (0-6)
(
    GET_NAME,
    GET_GENDER,
    GET_AGE,
    GET_COUNTRY,
    GET_CITY,
    GET_PHONE,
    GET_EMAIL,
) = range(7)

# حالات المديرين والمطور (7-30)
(
    GET_ACCEPT_MESSAGE,
    GET_REJECT_MESSAGE,
    GET_BROADCAST_MESSAGE,
    GET_ADMIN_ID_TO_ADD,
    GET_ADMIN_ID_TO_REMOVE,
    ADD_COURSE_NAME,
    ADD_COURSE_DESC,
    ADD_COURSE_PRICE,
    ADD_COURSE_CAT,
    EDIT_COURSE_SELECT_COURSE,
    EDIT_COURSE_SELECT_FIELD,
    EDIT_COURSE_NEW_VALUE,
    ADD_CATEGORY_NAME,
    DELETE_CATEGORY_CONFIRM,
    DELETE_COURSE_CONFIRM,
    CONFIRM_DELETE_COURSE,      # تم التأكد من وجودها لتوافق ملف الأدمن
    EDIT_COURSE_CAT,
    MOVE_COURSE_SELECT_COURSE,
    MOVE_COURSE_SELECT_CAT,
    GET_BACKUP_FILE,
    GET_PROMO_NAME,
    GET_PROMO_PERCENT,
    CONFIRM_FINAL_DELETE,
) = range(7, 29)
