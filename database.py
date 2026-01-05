import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd

def get_engine():
    db_url = st.secrets["connections"]["postgresql"]["url"]
    return create_engine(db_url)

def init_db():
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS observers (
                "#" SERIAL PRIMARY KEY,
                "الاسم" TEXT, "الايميل" TEXT, "حالة المراقب" TEXT,
                "الجوال" TEXT, "جهة العمل" TEXT, "المنطقة" TEXT, "المدينة" TEXT
            );
        '''))
        conn.commit()

def اضافة_حملة(بيانات):
    engine = get_engine()
    with engine.connect() as conn:
        # تأكدي أن الأسماء هنا تطابق جدول Neon تماماً
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
            # تحويل القائمة لـ tuple ليعمل استعلام IN بشكل صحيح
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
