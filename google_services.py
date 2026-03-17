import gspread
import json
import os
import base64
from oauth2client.service_account import ServiceAccountCredentials
from config import MASTER_SS_ID, SERVICE_ACCOUNT_FILE

# 1. إعداد الصلاحيات
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

creds_json = os.getenv("GOOGLE_SHEETS_CREDS")

try:
    if creds_json:
        # محاولة معرفة هل النص Base64 أم JSON عادي
        try:
            # إذا كان Base64 سنقوم بفك تشفيره
            decoded_creds = base64.b64decode(creds_json).decode('utf-8')
            creds_dict = json.loads(decoded_creds)
            print("✅ تم فك تشفير البيانات باستخدام Base64")
        except Exception:
            # إذا فشل، نتعامل معه كـ JSON عادي (للدعم المزدوج)
            creds_dict = json.loads(creds_json)
            print("✅ يتم استخدام JSON عادي من متغيرات البيئة")

        # معالجة رموز السطر الجديد لضمان عمل المفتاح الخاص
        if "private_key" in creds_dict:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
        # الحل الاحتياطي للمطور محلياً
        creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
        print("⚠️ يتم استخدام ملف service_account.json المحلي")

except Exception as e:
    print(f"❌ خطأ فادح في معالجة بيانات الاعتماد: {e}")
    raise

# 3. تخويل الاتصال
client = gspread.authorize(creds)

def get_ss():
    """فتح السبريدشيت باستخدام الـ ID الثابت"""
    try:
        return client.open_by_key(MASTER_SS_ID)
    except Exception as e:
        print(f"❌ فشل فتح ورقة العمل: {e}")
        raise

# تعريف الجداول
try:
    ss = get_ss()
    SHEET_CATS = ss.worksheet("الأقسام")
    SHEET_COURSES = ss.worksheet("الدورات")
    SHEET_REGS = ss.worksheet("التسجيلات")
    SHEET_PROMO_CODES = ss.worksheet("أكواد_الخصم")
except Exception as e:
    print(f"⚠️ تحذير: لم يتم العثور على بعض أوراق العمل: {e}")
