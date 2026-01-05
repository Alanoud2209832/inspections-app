
import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd

def get_engine():
    db_url = st.secrets["connections"]["postgresql"]["url"]
    
    # تصحيح الرابط إذا كان يبدأ بـ postgres:// ليصبح postgresql://
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    return create_engine(db_url, pool_pre_ping=True)

def init_db():
    engine = get_engine()
    with engine.connect() as conn:
        # 1. إنشاء جدول الحملات
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
                "عدد المنشآت بناءً على المسح الميداني" INTEGER,
                "مأموري الضبط من وزارة التجارة" TEXT,
                "موقع التجمع على الخرائط" TEXT,
                "تاريخ الإضافة" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        '''))
        
        # 2. إنشاء جدول المراقبين
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
        conn.commit()

def اضافة_حملة(بيانات):
    engine = get_engine()
    with engine.connect() as conn:
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
            # تحويل القائمة إلى tuple للبحث بـ IN
            استعلام = text('''
                SELECT "الاسم" FROM observers 
                WHERE "المنطقة" = :reg AND "جهة العمل" IN :works
                ORDER BY "الاسم" ASC
            ''')
            result = conn.execute(استعلام, {"reg": المنطقة, "works": tuple(الجهات)})
            return [row[0] for row in result]
    except Exception as e:
        return []

def جلب_الحملات():
    engine = get_engine()
    try:
        with engine.connect() as conn:
            return pd.read_sql('SELECT * FROM campaigns ORDER BY "م" DESC', conn)
    except:
        return pd.DataFrame()

def اضافة_مراقب(بيانات):
    engine = get_engine()
    with engine.connect() as conn:
        # تأكدي من وجود حقل "الجوال" هنا
        استعلام = text('''
            INSERT INTO observers ("الاسم", "الايميل", "حالة المراقب", "الجوال", "جهة العمل", "المنطقة", "المدينة")
            VALUES (:name, :email, :status, :phone, :work, :region, :city)
        ''')
        conn.execute(استعلام, بيانات)
        conn.commit()

# دالة جلب الحملات (تأكدي أنها هكذا لتعمل الإحصائيات)
def جلب_الحملات():
    engine = get_engine()
    try:
        with engine.connect() as conn:
            df = pd.read_sql('SELECT * FROM campaigns', conn)
            # تحويل التاريخ إلى صيغة يفهمها الباندا للإحصائيات
            if not df.empty and 'التاريخ' in df.columns:
                df['التاريخ'] = pd.to_datetime(df['التاريخ'])
            return df
    except:
        return pd.DataFrame()

def تحقق_دخول_المراقب(ايميل):
    engine = get_engine()
    try:
        with engine.connect() as conn:
            استعلام = text('SELECT "الاسم" FROM observers WHERE LOWER("الايميل") = LOWER(:email) LIMIT 1')
            result = conn.execute(استعلام, {"email": ايميل.strip()}).fetchone()
            return result[0] if result else None
    except:
        return None

def جلب_حملات_المراقب(اسم_المراقب):
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
