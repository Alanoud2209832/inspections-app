import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd

def get_engine():
    db_url = st.secrets["connections"]["postgresql"]["url"]
    return create_engine(db_url)

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
                "قائد الفريق" TEXT,
                "المراقبين المشاركين" TEXT,
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

def add_campaign(data):
    engine = get_engine()
    with engine.connect() as conn:
        # هنا نتأكد أن أسماء الأعمدة (بين علامات التنصيص) تطابق ما في Neon
        # وأن المتغيرات (بعد النقطتين :) تطابق ما نرسله من app.py
        query = text('''
            INSERT INTO campaigns 
            ("اليوم والتاريخ", "المنطقة", "المدينة", "اسم التجمع", "قائد الفريق", "المراقبين المشاركين",
             "عدد المنشآت بناءً على المسح الميداني", "مأموري الضبط من وزارة التجارة", "موقع التجمع على الخرائط")
            VALUES 
            (:day_date, :region, :city, :group_name, :leader, :participants, :survey_count, :inspectors, :map_link)
        ''')
        conn.execute(query, data)
        conn.commit()
        

def get_campaigns():
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql('SELECT * FROM campaigns ORDER BY "م" DESC', conn)

def get_campaigns_for_observer(observer_name):
    engine = get_engine()
    with engine.connect() as conn:
        query = text('''
            SELECT * FROM campaigns 
            WHERE "قائد الفريق" = :name 
            OR "المراقبين المشاركين" LIKE :name_like
            ORDER BY "م" DESC
        ''')
        return pd.read_sql(query, conn, params={"name": observer_name, "name_like": f'%{observer_name}%'})

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

def get_observers_by_region(region_name):
    engine = get_engine()
    try:
        with engine.connect() as conn:
            query = text('SELECT "الاسم" FROM observers WHERE "المنطقة" = :reg ORDER BY "الاسم" ASC')
            result = conn.execute(query, {"reg": region_name})
            return [row[0] for row in result]
    except:
        return []

def check_observer_login(email):
    engine = get_engine()
    with engine.connect() as conn:
        query = text('SELECT "الاسم" FROM observers WHERE LOWER("الايميل") = LOWER(:email) LIMIT 1')
        result = conn.execute(query, {"email": email.strip()}).fetchone()
        return result[0] if result else None
        
