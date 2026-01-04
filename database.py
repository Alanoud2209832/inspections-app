import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd

def get_engine():
    db_url = st.secrets["connections"]["postgresql"]["url"]
    return create_engine(db_url)

def init_db():
    engine = get_engine()
    with engine.connect() as conn:
        # إنشاء جدول الحملات مع عمود قائد الفريق
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS campaigns (
                "م" SERIAL PRIMARY KEY,
                "اليوم والتاريخ" TEXT,
                "المنطقة" TEXT,
                "المدينة" TEXT,
                "اسم التجمع" TEXT,
                "قائد الفريق" TEXT,
                "عدد المنشآت بناءً على المسح الميداني" INTEGER,
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
        conn.commit()

def add_campaign(data):
    engine = get_engine()
    with engine.connect() as conn:
        query = text('''
            INSERT INTO campaigns 
            ("اليوم والتاريخ", "المنطقة", "المدينة", "اسم التجمع", "قائد الفريق",
             "عدد المنشآت بناءً على المسح الميداني", "مأموري الضبط من وزارة التجارة", "موقع التجمع على الخرائط")
            VALUES (:day_date, :region, :city, :group_name, :leader, :survey_count, :inspectors, :map_link)
        ''')
        conn.execute(query, data)
        conn.commit()

def get_campaigns():
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql('SELECT * FROM campaigns ORDER BY "م" DESC', conn)

def add_observer(data):
    engine = get_engine()
    with engine.connect() as conn:
        query = text('''
            INSERT INTO observers ("الاسم", "الايميل", "حالة المراقب", "الجوال", "جهة العمل", "المنطقة", "المدينة")
            VALUES (:name, :email, :status, :phone, :work, :region, :city)
        ''')
        conn.execute(query, data)
        conn.commit()

def get_observers():
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql('SELECT * FROM observers ORDER BY "#" ASC', conn)

def get_observers_names():
    engine = get_engine()
    # استخدام سياق الاتصال المباشر لضمان جلب أحدث البيانات
    try:
        with engine.connect() as conn:
            result = conn.execute(text('SELECT "الاسم" FROM observers ORDER BY "الاسم" ASC'))
            names = [row[0] for row in result]
            return names
    except Exception as e:
        st.error(f"خطأ في جلب الأسماء: {e}")
        return []
