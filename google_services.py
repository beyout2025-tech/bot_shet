import gspread
import json
import os
from oauth2client.service_account import ServiceAccountCredentials
from config import MASTER_SS_ID

# إعداد الصلاحيات
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# جلب البيانات من متغيرات البيئة في Railway
creds_json = os.getenv("GOOGLE_SHEETS_CREDS")

try:
    if creds_json:
        creds_dict = json.loads(creds_json)
        # ✅ السطر السحري: إصلاح مشكلة التوقيع (JWT) التي تسبب الانهيار
        if "private_key" in creds_dict:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
        # للعمل المحلي فقط
        from config import SERVICE_ACCOUNT_FILE
        creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
except Exception as e:
    print(f"❌ خطأ في مفتاح جوجل: {e}")
    raise

client = gspread.authorize(creds)

def get_ss():
    return client.open_by_key(MASTER_SS_ID)

# --- تعريف أوراق العمل (تأكد من كتابة الأسماء العربية بدقة) ---
try:
    SHEET_CATS = get_ss().worksheet("الأقسام")
    SHEET_PROMO_CODES = get_ss().worksheet("أكواد_الخصم")
    SHEET_REGS = get_ss().worksheet("قاعدة_بيانات_الطلاب")
    SHEET_USERS = get_ss().worksheet("مستخدمي_تيلجرام")
    SHEET_COURSES = get_ss().worksheet("الدورات_التدريبية")
except Exception as e:
    print(f"❌ لم يتم العثور على أوراق العمل: {e}")
    raise
