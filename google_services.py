import gspread
import json
import os
from oauth2client.service_account import ServiceAccountCredentials
from config import MASTER_SS_ID

# 1. إعداد الصلاحيات للوصول إلى Drive و Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# 2. جلب محتوى المفتاح من متغيرات البيئة في Railway
# سنبحث عن متغير سنسميه GOOGLE_SHEETS_CREDS
creds_json = os.getenv("GOOGLE_SHEETS_CREDS")

if creds_json:
    # إذا وجدنا المتغير، نقوم بتحويل النص إلى قاموس (Dictionary)
    creds_info = json.loads(creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
else:
    # حل احتياطي للمطور (إذا كنت تعمل على جهازك الكمبيوتر)
    # تأكد من تسمية المتغير في config.py بـ credentials.json
    from config import SERVICE_ACCOUNT_FILE
    creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)

# 3. تخويل العميل
client = gspread.authorize(creds)

def get_ss():
    """فتح السبريدشيت باستخدام الـ ID الثابت لضمان الاستقرار"""
    return client.open_by_key(MASTER_SS_ID)

# --- تعريف أوراق العمل (Worksheets) المباشرة بناءً على ملف التأسيس ---

# ورقة الأقسام
SHEET_CATS = get_ss().worksheet("الأقسام")

# ورقة أكواد الخصم
SHEET_PROMO_CODES = get_ss().worksheet("أكواد_الخصم")

# ورقة الكوبونات
SHEET_COUPONS = get_ss().worksheet("الكوبونات")

# ورقة قاعدة بيانات الطلاب
SHEET_REGS = get_ss().worksheet("قاعدة_بيانات_الطلاب")

# ورقة مستخدمي تيلجرام
SHEET_USERS = get_ss().worksheet("مستخدمي_تيلجرام")

# ورقة الدورات التدريبية
SHEET_COURSES = get_ss().worksheet("الدورات_التدريبية")
