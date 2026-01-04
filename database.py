import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd

def get_engine():
    db_url = st.secrets["connections"]["postgresql"]["url"]
    return create_engine(db_url)

def init_db():
    # هذه الوظيفة ستحاول إنشاء الجداول إذا لم تكن موجودة
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text('CREATE TABLE IF NOT EXISTS observers ("#" SERIAL PRIMARY KEY, "الاسم" TEXT);'))
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

# هذه الوظيفة هي المسؤولة عن إظهار القائمة في "إضافة حملة"
def get_observers_names():
    engine = get_engine()
    try:
        with engine.connect() as conn:
            df = pd.read_sql('SELECT "الاسم" FROM observers ORDER BY "الاسم" ASC', conn)
            return df["الاسم"].tolist()
    except:
        return []
