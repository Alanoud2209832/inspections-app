import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd

# وظيفة الاتصال بمحرك قاعدة البيانات
def get_engine():
    db_url = st.secrets["connections"]["postgresql"]["url"]
    return create_engine(db_url)

# تهيئة الجداول (تُنفذ تلقائياً)
def init_db():
    engine = get_engine()
    with engine.connect() as conn:
        # جدول الحملات
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS campaigns (
                "م" SERIAL PRIMARY KEY,
                "اليوم والتاريخ" TEXT,
                "المنطقة" TEXT,
                "المدينة" TEXT,
                "اسم التجمع" TEXT,
                "عدد المنشآت بناءً على المسح الميداني" INTEGER,
                "مأموري الضبط من وزارة التجارة" TEXT,
                "موقع التجمع على الخرائط" TEXT,
                "تاريخ الإضافة" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        '''))
        # جدول المراقبين
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

# وظائف جدول الحملات
def add_campaign(data):
    engine = get_engine()
    with engine.connect() as conn:
        query = text('''
            INSERT INTO campaigns 
            ("اليوم والتاريخ", "المنطقة", "المدينة", "اسم التجمع", 
             "عدد المنشآت بناءً على المسح الميداني", "مأموري الضبط من وزارة التجارة", 
             "موقع التجمع على الخرائط")
            VALUES (:day_date, :region, :city, :group_name, :survey_count, :inspectors, :map_link)
        ''')
        conn.execute(query, data)
        conn.commit()

def get_campaigns():
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql("SELECT * FROM campaigns ORDER BY م DESC", conn)

# وظائف جدول المراقبين
def get_observers():
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql("SELECT * FROM observers ORDER BY # ASC", conn)
