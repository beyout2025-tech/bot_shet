import json
import os
import logging
from config import DB_FILE, DEV_ID

# إعداد logging لتتبع الأخطاء داخل الدوال المساعدة
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def load_db():
    """دالة لقراءة البيانات من ملف JSON مع التحقق من الهيكل"""
    # 1. التحقق من وجود الملف أو أنه فارغ
    if not os.path.exists(DB_FILE) or os.stat(DB_FILE).st_size == 0:
        data = {
            "users": [DEV_ID],
            "admins": [DEV_ID],
            "categories": [],
            "courses": [],
            "registrations": [], 
            "promo_codes": {} 
        }
        save_db(data)
        return data

    # 2. محاولة قراءة البيانات
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        logging.error(f"خطأ في قراءة ملف JSON: {e}")
        # في حال وجود خطأ في بنية الملف، ننشئ هيكل جديد لضمان عدم توقف البوت
        data = {
            "users": [DEV_ID], 
            "admins": [DEV_ID], 
            "categories": [], 
            "courses": [], 
            "registrations": [], 
            "promo_codes": {}
        }
        save_db(data)
        return data

    # 3. تحديث الهيكل إذا لزم الأمر (Logic Check) لضمان عدم نقص أي مفتاح أساسي
    needs_save = False

    if "promo_codes" not in data:
        data["promo_codes"] = {}
        needs_save = True

    if "registrations" not in data:
        data["registrations"] = []
        needs_save = True

    if DEV_ID not in data["admins"]:
        data["admins"].append(DEV_ID)
        needs_save = True
    
    # إذا حدث أي تغيير في الهيكل أثناء الفحص، احفظ فوراً
    if needs_save:
        save_db(data)
        
    return data

def save_db(data):
    """دالة لحفظ البيانات في ملف JSON"""
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logging.error(f"خطأ أثناء حفظ ملف JSON: {e}")
