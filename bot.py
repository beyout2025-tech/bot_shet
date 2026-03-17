import logging
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters
)
from config import *
from utils.helpers import load_db
from handlers.start import start, show_main_menu
from handlers.registration import (
    start_registration, get_name, get_gender, get_age, 
    get_country, get_city, get_phone, get_email, cancel
)
from handlers.admin import (
    show_dev_panel, show_dev_stats, show_dev_users, 
    add_admin_start, add_admin, remove_admin_start, remove_admin,
    broadcast_start, send_broadcast, show_manage_categories_menu,
    add_category_start, add_category, delete_category_start, 
    confirm_delete_category, execute_delete_category,
    show_manage_courses_menu, add_course_start, add_course_name,
    add_course_desc, add_course_price, add_course_cat,
    delete_course_start, confirm_delete_course, move_course_start,
    move_course_select_category, move_course, accept_registration,
    send_accept_message, reject_registration, send_reject_message,
    handle_receipt, download_backup, upload_backup_start, 
    receive_backup_file, add_promo_start, get_promo_name, get_promo_percent
)

# إعداد الـ logging العام للنظام لتتبع الأخطاء
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main() -> None:
    # إنشاء التطبيق باستخدام التوكن من ملف الإعدادات
    application = Application.builder().token(BOT_TOKEN).build()

    # 1. ConversationHandler لنظام تسجيل الطلاب
    user_reg_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_registration, pattern=r"^register_\d+$")],
        states={
            GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            GET_GENDER: [CallbackQueryHandler(get_gender, pattern=r"^gender_")],
            GET_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            GET_COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_country)],
            GET_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
            GET_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            GET_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # 2. ConversationHandler لنظام قبول ورفض التسجيلات
    admin_msg_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(accept_registration, pattern=r"^accept_\d+_\d+$"),
            CallbackQueryHandler(reject_registration, pattern=r"^reject_\d+_\d+$"),
        ],
        states={
            GET_ACCEPT_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, send_accept_message)],
            GET_REJECT_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, send_reject_message)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # 3. ConversationHandler لنظام إدارة المشرفين
    admin_user_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(add_admin_start, pattern="^dev_add_admin$"),
            CallbackQueryHandler(remove_admin_start, pattern="^dev_remove_admin$"),
        ],
        states={
            GET_ADMIN_ID_TO_ADD: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_admin)],
            GET_ADMIN_ID_TO_REMOVE: [MessageHandler(filters.TEXT & ~filters.COMMAND, remove_admin)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # 4. ConversationHandler لنظام الرسائل الجماعية
    admin_broadcast_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(broadcast_start, pattern="^dev_broadcast$")],
        states={
            GET_BROADCAST_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, send_broadcast)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    # 5. ConversationHandler لنظام إضافة الدورات التدريبية
    admin_add_course_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(add_course_start, pattern="^dev_add_course$")],
        states={
            ADD_COURSE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_course_name)],
            ADD_COURSE_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_course_desc)],
            ADD_COURSE_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_course_price)],
            ADD_COURSE_CAT: [CallbackQueryHandler(add_course_cat, pattern=r"^select_cat_")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # 6. ConversationHandler لنظام إدارة الأقسام
    admin_category_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(add_category_start, pattern="^dev_add_cat$"),
            CallbackQueryHandler(delete_category_start, pattern="^dev_delete_cat$")
        ],
        states={
            ADD_CATEGORY_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_category)],
            DELETE_CATEGORY_CONFIRM: [CallbackQueryHandler(confirm_delete_category, pattern=r"^del_cat_confirm_")],
            CONFIRM_FINAL_DELETE: [ 
                CallbackQueryHandler(execute_delete_category, pattern=r"^(delete_cat_only|delete_cat_with_courses)$")
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # 7. ConversationHandler لنظام النسخ الاحتياطي
    admin_backup_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(upload_backup_start, pattern="^backup_upload$")],
        states={
            GET_BACKUP_FILE: [MessageHandler(filters.Document.ALL, receive_backup_file)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # 8. ConversationHandler لنظام الأكواد الترويجية
    admin_promo_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(add_promo_start, pattern="^dev_add_promo$")],
        states={
            GET_PROMO_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_promo_name)],
            GET_PROMO_PERCENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_promo_percent)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # --- إضافة الـ Handlers إلى التطبيق ---
    application.add_handler(CommandHandler("start", start))

    # إضافة كافة الـ ConversationHandlers المبرمجة
    application.add_handler(user_reg_handler)
    application.add_handler(admin_msg_handler)
    application.add_handler(admin_user_handler)
    application.add_handler(admin_broadcast_handler)
    application.add_handler(admin_add_course_handler)
    application.add_handler(admin_category_handler)
    application.add_handler(admin_promo_handler)
    application.add_handler(admin_backup_handler)

    # معالجة استلام الإيصالات (يجب أن يكون بعد الـ ConversationHandlers)
    application.add_handler(MessageHandler(
        (filters.PHOTO | filters.Document.ALL | filters.TEXT) & ~filters.COMMAND, 
        handle_receipt
    ))

    # معالجة طلبات الـ CallbackQueries العامة للتنقل
    application.add_handler(CallbackQueryHandler(download_backup, pattern="^backup_download$"))
    application.add_handler(CallbackQueryHandler(show_manage_courses_menu, pattern="^dev_courses$"))
    application.add_handler(CallbackQueryHandler(show_manage_categories_menu, pattern="^dev_categories$"))
    application.add_handler(CallbackQueryHandler(show_dev_panel, pattern="^dev_panel$"))
    application.add_handler(CallbackQueryHandler(show_dev_stats, pattern="^dev_stats$"))
    application.add_handler(CallbackQueryHandler(show_dev_users, pattern="^dev_users$"))
    application.add_handler(CallbackQueryHandler(show_main_menu, pattern="^main_menu$"))
    
    # تشغيل البوت
    print("🚀 بوت أكاديمية كن أنت يعمل بنجاح...")
    application.run_polling()

if __name__ == "__main__":
    main()
