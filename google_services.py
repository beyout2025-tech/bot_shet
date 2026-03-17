import httpx
import os
import logging

# إعدادات الاتصال بـ Google Apps Script
# تأكد من إضافة هذا المتغير في Railway وضع فيه رابط الـ Web App
APPS_SCRIPT_URL = os.getenv("APPS_SCRIPT_URL")
API_KEY = "KANANT-2026"  # نفس المفتاح الموجود في كود السكريبت لديك

def call_apps_script(sheet_name, action, values=None):
    """
    الدالة المركزية للتواصل مع Google Sheets عبر Apps Script
    """
    if not APPS_SCRIPT_URL:
        logging.error("❌ APPS_SCRIPT_URL is not set in Environment Variables")
        return None

    payload = {
        "api_key": API_KEY,
        "sheet_name": sheet_name,
        "action": action,
        "values": values if values else []
    }

    try:
        # جوجل سكريبت يقوم بعمل Redirect، لذا نستخدم follow_redirects=True
        with httpx.Client(follow_redirects=True, timeout=30.0) as client:
            response = client.post(APPS_SCRIPT_URL, json=payload)
            result = response.json()
            
            if result.get("status") == "success":
                return result.get("data") if action == "read" else True
            else:
                logging.error(f"❌ Apps Script Error: {result.get('message')}")
                return None
    except Exception as e:
        logging.error(f"❌ Connection Error: {e}")
        return None

# --- دوال بديلة للكائنات القديمة لتقليل التعديل في الملفات الأخرى ---

class SheetProxy:
    def __init__(self, name):
        self.name = name
    
    def append_row(self, values):
        return call_apps_script(self.name, "append", values)
    
    def get_all_values(self):
        return call_apps_script(self.name, "read")

# تعريف الأوراق ككائنات وهمية (Proxies) لكي لا نغير الكود في handlers
SHEET_CATS = SheetProxy("الأقسام")
SHEET_COURSES = SheetProxy("الدورات_التدريبية")
SHEET_REGS = SheetProxy("سجل_التسجيلات")
SHEET_PROMO_CODES = SheetProxy("أكواد_الخصم")
