import gspread
import json
import os
from oauth2client.service_account import ServiceAccountCredentials
from config import MASTER_SS_ID

# 1. إعداد الصلاحيات
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# 2. جلب البيانات من Railway (أو ملف محلي إذا فشل)
creds_json = os.getenv("GOOGLE_SHEETS_CREDS")

try:
    if creds_json:
        # القراءة من متغيرات البيئة (الطريقة الآمنة لـ Railway)
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
        # القراءة من ملف (للتشغيل المحلي)
        from config import SERVICE_ACCOUNT_FILE
        creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
except json.JSONDecodeError:
    print("❌ خطأ: محتوى متغير GOOGLE_SHEETS_CREDS ليس JSON صحيحاً!")
    raise
except Exception as e:
    print(f"❌ خطأ غير متوقع: {e}")
    raise

# 3. تخويل الاتصال
client = gspread.authorize(creds)

def get_ss():
    return client.open_by_key(MASTER_SS_ID)

# --- تعريف أوراق العمل ---
SHEET_CATS = get_ss().worksheet("الأقسام")
SHEET_PROMO_CODES = get_ss().worksheet("أكواد_الخصم")
SHEET_COUPONS = get_ss().worksheet("الكوبونات")
SHEET_REGS = get_ss().worksheet("قاعدة_بيانات_الطلاب")
SHEET_USERS = get_ss().worksheet("مستخدمي_تيلجرام")
SHEET_COURSES = get_ss().worksheet("الدورات_التدريبية")
