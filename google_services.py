import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import MASTER_SS_ID, SERVICE_ACCOUNT_FILE

# إعداد الصلاحيات للوصول إلى Drive و Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# تهيئة الاتصال باستخدام ملف credentials.json (المسمى في config بـ SERVICE_ACCOUNT_FILE)
creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
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

# ورقة قاعدة بيانات الطلاب (المسؤولة عن 39 عموداً)
SHEET_REGS = get_ss().worksheet("قاعدة_بيانات_الطلاب")

# ورقة مستخدمي تيلجرام
SHEET_USERS = get_ss().worksheet("مستخدمي_تيلجرام")

# ورقة الدورات التدريبية
SHEET_COURSES = get_ss().worksheet("الدورات_التدريبية")
