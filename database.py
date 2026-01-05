import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd

def get_engine():
    db_url = st.secrets["connections"]["postgresql"]["url"]
    return create_engine(db_url)

def init_db():
    engine = get_engine()
    with engine.connect() as conn:
        # إنشاء جدول الحملات بالهيكل الأساسي إذا لم يكن موجوداً
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS campaigns (
                "م" SERIAL PRIMARY KEY,
                "المنطقة" TEXT,
                "المدينة" TEXT,
                "اسم التجمع" TEXT,
                "قائد الفريق" TEXT
            );
        '''))
        
        # --- كود الإصلاح التلقائي للأعمدة الناقصة ---
        columns_to_add = {
            "اليوم": "TEXT",
            "التاريخ": "DATE",
            "المراقبين المشاركين": "TEXT",
            "عدد المنشآت بناءً على المسح الميداني": "INTEGER",
            "مأموري الضبط من وزارة التجارة": "TEXT",
            "موقع التجمع على الخرائط": "TEXT"
        }
        
        for col, dtype in columns_to_add.items():
            try:
                # محاولة إضافة العمود، إذا كان موجوداً سيفشل الأمر بصمت (هذا ما نريده)
                conn.execute(text(f'ALTER TABLE campaigns ADD COLUMN "{col}" {dtype};'))
            except Exception:
                pass # العمود موجود مسبقاً، لا نفعل شيئاً
        
        # إنشاء جدول المراقبين
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS observers (
                "#" SERIAL PRIMARY KEY,
                "الاسم" TEXT, "الايميل" TEXT, "جهة العمل" TEXT, "المنطقة" TEXT
            );
        '''))
        conn.commit()

def اضافة_حملة(بيانات):
    engine = get_engine()
    with engine.connect() as conn:
        # هنا التأكد من مطابقة أسماء الأعمدة العربية مع قيم بايثون
        استعلام = text('''
            INSERT INTO campaigns 
            ("اليوم", "التاريخ", "المنطقة", "المدينة", "اسم التجمع", "قائد الفريق", "المراقبين المشاركين",
             "عدد المنشآت بناءً على المسح الميداني", "مأموري الضبط من وزارة التجارة", "موقع التجمع على الخرائط")
            VALUES 
            (:day, :date, :region, :city, :group_name, :leader, :participants, :survey_count, :inspectors, :map_link)
        ''')
        conn.execute(استعلام, بيانات)
        conn.commit()

def جلب_مراقبين_بالجهة(المنطقة, الجهات):
    if not الجهات: return []
    engine = get_engine()
    try:
        with engine.connect() as conn:
            # تحويل القائمة لـ tuple ليعمل SQL IN بشكل صحيح
            استعلام = text('''
                SELECT "الاسم" FROM observers 
                WHERE "المنطقة" = :reg AND "جهة العمل" IN :works
            ''')
            result = conn.execute(استعلام, {"reg": المنطقة, "works": tuple(الجهات)})
            return [row[0] for row in result]
    except:
        return []

def جلب_الحملات():
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql('SELECT * FROM campaigns ORDER BY "م" DESC', conn)

def اضافة_مراقب(بيانات):
    engine = get_engine()
    with engine.connect() as conn:
        استعلام = text('''
            INSERT INTO observers ("الاسم", "الايميل", "حالة المراقب", "الجوال", "جهة العمل", "المنطقة", "المدينة")
            VALUES (:name, :email, :status, :phone, :work, :region, :city)
        ''')
        conn.execute(استعلام, بيانات)
        conn.commit()

def جلب_المراقبين():
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql('SELECT * FROM observers ORDER BY "#" ASC', conn)

def تحقق_دخول_المراقب(ايميل):
    engine = get_engine()
    with engine.connect() as conn:
        استعلام = text('SELECT "الاسم" FROM observers WHERE LOWER("الايميل") = LOWER(:email) LIMIT 1')
        النتيجة = conn.execute(استعلام, {"email": ايميل.strip()}).fetchone()
        return النتيجة[0] if النتيجة else None

def جلب_حملات_المراقب(اسم_المراقب):
    engine = get_engine()
    with engine.connect() as conn:
        استعلام = text('''
            SELECT * FROM campaigns 
            WHERE "قائد الفريق" = :name OR "المراقبين المشاركين" LIKE :name_like
            ORDER BY "م" DESC
        ''')
        return pd.read_sql(استعلام, conn, params={"name": اسم_المراقب, "name_like": f'%{اسم_المراقب}%'})
