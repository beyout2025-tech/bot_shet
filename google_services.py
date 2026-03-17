import gspread
import json
import os
from oauth2client.service_account import ServiceAccountCredentials
from config import MASTER_SS_ID

# 1. إعداد الصلاحيات
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# 2. جلب البيانات من متغيرات البيئة (Railway) بأسلوب معالج للأخطاء
creds_json = os.getenv("GOOGLE_SHEETS_CREDS")

try:
    if creds_json:
        # تحويل النص إلى قاموس JSON
        creds_dict = json.loads(creds_json)
        
        # ✅ معالجة ذكية: إصلاح مشكلة "JWT Signature" الناتجة عن تلف رموز السطر الجديد \n
        if "private_key" in creds_dict and "\\n" in creds_dict["private_key"]:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
        # الحل الاحتياطي (للمطور محلياً)
        from config import SERVICE_ACCOUNT_FILE
        creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
except Exception as e:
    # طباعة الخطأ بوضوح في السجلات لمعرفته
    print(f"❌ خطأ في معالجة بيانات الاعتماد: {e}")
    raise

# 3. تخويل الاتصال
client = gspread.authorize(creds)

def get_ss():
    """فتح السبريدشيت باستخدام الـ ID الثابت"""
    return client.open_by_key(MASTER_SS_ID)

# --- تعريف أوراق العمل (تم التأكد من صحة الكلمات العربية) ---
# ملاحظة: الكلمات أدناه مكتوبة بترميز UTF-8 الصحيح
SHEET_CATS = get_ss().worksheet("الأقسام")
SHEET_PROMO_CODES = get_ss().worksheet("أكواد_الخصم")
SHEET_COUPONS = get_ss().worksheet("الكوبونات")
SHEET_REGS = get_ss().worksheet("قاعدة_بيانات_الطلاب")
SHEET_USERS = get_ss().worksheet("مستخدمي_تيلجرام")
SHEET_COURSES = get_ss().worksheet("الدورات_التدريبية")
