import gspread
import json
import os
from oauth2client.service_account import ServiceAccountCredentials
from config import MASTER_SS_ID

# 1. إعداد الصلاحيات
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# 2. جلب البيانات من Railway بأسلوب معالج للأخطاء
creds_json = os.getenv("GOOGLE_SHEETS_CREDS")

try:
    if creds_json:
        # تحويل النص إلى قاموس JSON
        creds_dict = json.loads(creds_json)
        
        # ✅ إصلاح مشكلة "JWT Signature" (استبدال الرموز التالفة بأسطر حقيقية)
        if "private_key" in creds_dict:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
        # للعمل المحلي فقط
        from config import SERVICE_ACCOUNT_FILE
        creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
except Exception as e:
    print(f"❌ خطأ في معالجة مفتاح جوجل: {e}")
    raise

# 3. تخويل الاتصال
client = gspread.authorize(creds)

def get_ss():
    """فتح السبريدشيت باستخدام الـ ID الثابت لضمان الاستقرار"""
    return client.open_by_key(MASTER_SS_ID)

# --- تعريف أوراق العمل بدقة (مع ضمان الترميز العربي الصحيح) ---
try:
    ss = get_ss()
    # استخدام الأسماء كما وردت في ملف التأسيس
    SHEET_CATS = ss.worksheet("الأقسام")
    SHEET_PROMO_CODES = ss.worksheet("أكواد_الخصم")
    SHEET_REGS = ss.worksheet("قاعدة_بيانات_الطلاب")
    SHEET_USERS = ss.worksheet("مستخدمي_تيلجرام")
    SHEET_COURSES = ss.worksheet("الدورات_التدريبية")
    # إذا كنت تستخدم الكوبونات أضفها هنا:
    # SHEET_COUPONS = ss.worksheet("الكوبونات")
except Exception as e:
    print(f"❌ فشل الوصول إلى أوراق العمل: {e}")
    raise
