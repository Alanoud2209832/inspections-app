import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_engine():
    """إنشاء محرك الاتصال بقاعدة البيانات"""
    try:
        db_url = st.secrets["connections"]["postgresql"]["url"]
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        engine = create_engine(db_url, pool_pre_ping=True)
        return engine
    except Exception as e:
        st.error(f"خطأ في الوصول إلى بيانات الاتصال: {e}")
        return None

def test_connection():
    """اختبار الاتصال بالقاعدة"""
    engine = get_engine()
    if engine:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                return "✅ تم الاتصال بنجاح!"
        except Exception as e:
            return f"❌ فشل الاتصال: {e}"

def init_db():
    """تهيئة الجداول عند تشغيل التطبيق لأول مرة"""
    engine = get_engine()
    if engine is None: return
    with engine.connect() as conn:
        # إنشاء جدول الحملات
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS campaigns (
                "م" SERIAL PRIMARY KEY,
                "اليوم" TEXT,
                "التاريخ" DATE,
                "المنطقة" TEXT,
                "المدينة" TEXT,
                "اسم التجمع" TEXT,
                "قائد الفريق" TEXT,
                "المراقبين المشاركين" TEXT,
                "عدد المنشآت بناءً على المسح الميدا" INTEGER,
                "مأموري الضبط من وزارة التجارة" TEXT,
                "موقع التجمع على الخرائط" TEXT,
                "تاريخ الإضافة" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        '''))
        
        # إنشاء جدول المراقبين
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS observers (
                "#" SERIAL PRIMARY KEY,
                "الاسم" TEXT,
                "الايميل" TEXT,
                "حالة المراقب" TEXT,
                "الجوال" TEXT,
                "جهة العمل" TEXT,
                "المنطقة" TEXT,
                "المدينة" TEXT
            );
        '''))

        # تحديث الأعمدة إذا كانت ناقصة
        try:
            conn.execute(text('ALTER TABLE observers ADD COLUMN IF NOT EXISTS "الجوال" TEXT;'))
            conn.execute(text('ALTER TABLE observers ADD COLUMN IF NOT EXISTS "المدينة" TEXT;'))
        except:
            pass
            
        conn.commit()

def اضافة_حملة(بيانات):
    """إضافة حملة جديدة إلى القاعدة"""
    engine = get_engine()
    if engine is None: return
    try:
        with engine.connect() as conn:
            استعلام = text('''
                INSERT INTO campaigns 
                ("اليوم", "التاريخ", "المنطقة", "المدينة", "اسم التجمع", "قائد الفريق", "المراقبين المشاركين",
                 "عدد المنشآت بناءً على المسح الميدا", "مأموري الضبط من وزارة التجارة", "موقع التجمع على الخرائط")
                VALUES 
                (:day, :date, :region, :city, :group_name, :leader, :participants, :survey_count, :inspectors, :map_link)
            ''')
            conn.execute(استعلام, بيانات)
            conn.commit()
    except Exception as e:
        st.error(f"خطأ في تنفيذ الاستعلام: {e}")

def جلب_الحملات():
    """جلب كافة الحملات المسجلة"""
    engine = get_engine()
    try:
        with engine.connect() as conn:
            return pd.read_sql('SELECT * FROM campaigns ORDER BY "م" DESC', conn)
    except:
        return pd.DataFrame()

def جلب_المراقبين():
    """جلب قائمة المراقبين"""
    engine = get_engine()
    try:
        with engine.connect() as conn:
            return pd.read_sql('SELECT * FROM observers ORDER BY "#" ASC', conn)
    except:
        return pd.DataFrame()

def اضافة_مراقب(بيانات):
    """إضافة مراقب جديد"""
    engine = get_engine()
    if engine is None: return
    with engine.connect() as conn:
        استعلام = text('''
            INSERT INTO observers ("الاسم", "الايميل", "حالة المراقب", "الجوال", "جهة العمل", "المنطقة", "المدينة")
            VALUES (:name, :email, :status, :phone, :work, :region, :city)
        ''')
        conn.execute(استعلام, بيانات)
        conn.commit()

def جلب_مراقبين_بالجهة(المنطقة, الجهات):
    """تصفية المراقبين حسب المنطقة والجهة"""
    if not الجهات: return []
    engine = get_engine()
    try:
        with engine.connect() as conn:
            استعلام = text('''
                SELECT "الاسم" FROM observers 
                WHERE "المنطقة" = :reg AND "جهة العمل" IN :works
            ''')
            result = conn.execute(استعلام, {"reg": المنطقة, "works": tuple(الجهات)})
            return [row[0] for row in result]
    except:
        return []

def تحقق_دخول_المراقب(ايميل):
    """التحقق من وجود البريد الإلكتروني للمراقب عند تسجيل الدخول"""
    engine = get_engine()
    try:
        with engine.connect() as conn:
            استعلام = text('SELECT "الاسم", "الايميل" FROM observers WHERE LOWER("الايميل") = LOWER(:email) LIMIT 1')
            res = conn.execute(استعلام, {"email": ايميل.strip()}).fetchone()
            return res if res else None
    except:
        return None

def جلب_بريد_المراقب_بالاسم(اسم):
    """جلب إيميل المراقب باستخدام اسمه (لإرسال التكليفات)"""
    engine = get_engine()
    try:
        with engine.connect() as conn:
            استعلام = text('SELECT "الاسم", "الايميل" FROM observers WHERE "الاسم" = :name LIMIT 1')
            res = conn.execute(استعلام, {"name": اسم}).fetchone()
            return res
    except:
        return None

def جلب_حملات_المراقب(اسم_المراقب):
    """جلب الحملات الخاصة بمراقب معين"""
    engine = get_engine()
    try:
        with engine.connect() as conn:
            استعلام = text('''
                SELECT * FROM campaigns 
                WHERE "قائد الفريق" = :name OR "المراقبين المشاركين" LIKE :name_like
                ORDER BY "م" DESC
            ''')
            return pd.read_sql(استعلام, conn, params={"name": اسم_المراقب, "name_like": f'%{اسم_المراقب}%'})
    except:
        return pd.DataFrame()

def ارسل_بريد_تكليف(ايميل_المراقب, اسم_المراقب, تفاصيل_الحملة, هل_هو_قائد=False):
    """إرسال إيميل تكليف مخصص (للقائد أو للمراقب)"""
    try:
        smtp_user = st.secrets["email"]["smtp_user"]
        smtp_password = st.secrets["email"]["smtp_password"]
        
        # تخصيص المسمى الوظيفي في الرسالة
        المسمى = "(قائد الفريق)" if هل_هو_قائد else "(مراقب مشارك)"
        
        subject = f"🔔 تكليف بمهمة رقابية: {تفاصيل_الحملة['group_name']}"
        
        body = f"""
        السلام عليكم ورحمة الله وبركاته،
        
        أهلاً {اسم_المراقب}،
        
        نود إحاطتك بأنه تم تكليفك بمهام {المسمى} للحملة الرقابية التالية:
        
        📍 المدينة: {تفاصيل_الحملة['city']}
        🏢 اسم التجمع: {تفاصيل_الحملة['group_name']}
        📅 التاريخ: {تفاصيل_الحملة['date']}
        🗓️ اليوم: {تفاصيل_الحملة['day']}
        🔗 رابط الموقع على الخرائط: {تفاصيل_الحملة['map_link']}
        
        يرجى الاطلاع والاستعداد للمهمة.
        
        مع تحيات،
        إدارة النظام الرقابي
        """
        
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = ايميل_المراقب
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, ايميل_المراقب, msg.as_string())
        server.quit()
        return True
    except:
        return False
