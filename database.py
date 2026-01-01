import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd

# إنشاء المحرك (Engine) باستخدام الرابط من Secrets
def get_engine():
    db_url = st.secrets["connections"]["postgresql"]["url"]
    return create_engine(db_url)

# وظيفة إنشاء الجدول
def init_db():
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS campaigns (
                م SERIAL PRIMARY KEY,
                "اليوم والتاريخ" TEXT,
                "المنطقة" TEXT,
                "المدينة" TEXT,
                "اسم التجمع" TEXT,
                "عدد المنشآت بناءً على المسح الميداني" INTEGER,
                "مأموري الضبط من وزارة التجارة" TEXT,
                "موقع التجمع على الخرائط" TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        '''))
        conn.commit()

# وظيفة إضافة بيانات
def add_campaign(data):
    engine = get_engine()
    with engine.connect() as conn:
        query = text('''
            INSERT INTO campaigns ("اليوم والتاريخ", "المنطقة", "المدينة", "اسم التجمع", 
                                "عدد المنشآت بناءً على المسح الميداني", "مأموري الضبط من وزارة التجارة", 
                                "موقع التجمع على الخرائط")
            VALUES (:day_date, :region, :city, :group_name, :survey_count, :inspectors, :map_link)
        ''')
        conn.execute(query, data)
        conn.commit()

# وظيفة جلب البيانات
def get_campaigns():
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql("SELECT * FROM campaigns ORDER BY م DESC", conn)
