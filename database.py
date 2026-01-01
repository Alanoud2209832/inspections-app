import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd

# إنشاء المحرك (Engine) باستخدام الرابط من Secrets
def get_engine():
    db_url = st.secrets["connections"]["postgresql"]["url"]
    return create_engine(db_url)

# وظيفة إنشاء الجدول (مهمة جداً لـ Neon)
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

# وظيفة لإضافة سطر جديد
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

# وظيفة لجلب البيانات من Neon وعرضها في الموقع
def get_campaigns():
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql("SELECT * FROM campaigns ORDER BY م DESC", conn)

# وظيفة لرفع البيانات القديمة من الإكسل إلى القاعدة (تستخدم لمرة واحدة)
def upload_old_data(df):
    engine = get_engine()
    # تنظيف البيانات لتطابق أسماء الأعمدة في القاعدة
    df_db = df.rename(columns={
        "اليوم والتاريخ": "day_date",
        "المنطقة": "region",
        "المدينة": "city",
        "اسم التجمع": "group_name",
        "عدد المنشآت بناءً على المسح الميداني": "survey_count",
        "مأموري الضبط من وزارة التجارة": "inspectors",
        "موقع التجمع على الخرائط": "map_link"
    })
    # استبقاء الأعمدة المطلوبة فقط
    cols = ["day_date", "region", "city", "group_name", "survey_count", "inspectors", "map_link"]
    df_db = df_db[cols]
    
    with engine.connect() as conn:
        for _, row in df_db.iterrows():
            add_campaign(row.to_dict())
