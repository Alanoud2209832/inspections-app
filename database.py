import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_engine():
    db_url = st.secrets["connections"]["postgresql"]["url"]
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    return create_engine(db_url, pool_pre_ping=True)

def init_db():
    engine = get_engine()
    with engine.connect() as conn:
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
        استعلام = text('''
            INSERT INTO campaigns 
            ("اليوم", "التاريخ", "المنطقة", "المدينة", "اسم التجمع", "قائد الفريق", "المراقبين المشاركين",
             "عدد المنشآت بناءً على المسح الميدا", "مأموري الضبط من وزارة التجارة", "موقع التجمع على الخرائط")
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
    try:
        with engine.connect() as conn:
            return pd.read_sql('SELECT * FROM campaigns ORDER BY "م" DESC', conn)
    except:
        return pd.DataFrame()

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
    try:
        with engine.connect() as conn:
            return pd.read_sql('SELECT * FROM observers ORDER BY "#" ASC', conn)
    except:
        return pd.DataFrame()

def تحقق_دخول_المراقب(اسم_المراقب):
    engine = get_engine()
    try:
        with engine.connect() as conn:
            استعلام = text('SELECT "الاسم", "الايميل" FROM observers WHERE "الاسم" = :name LIMIT 1')
            res = conn.execute(استعلام, {"name": اسم_المراقب}).fetchone()
            return res if res else None
    except:
        return None

def ارسل_بريد_تكليف(ايميل_المراقب, اسم_المراقب, تفاصيل_الحملة):
    try:
        smtp_user = st.secrets["email"]["smtp_user"]
        smtp_password = st.secrets["email"]["smtp_password"]
        
        subject = f"تكليف بمهمة ميدانية: {تفاصيل_الحملة['group_name']}"
        body = f"""
        <div dir='rtl' style='text-align: right; font-family: Arial;'>
            <h2 style='color: #2c3e50;'>أهلاً بك يا {اسم_المراقب}</h2>
            <p>تم تكليفك رسمياً بمهمة رقابية جديدة، إليك التفاصيل:</p>
            <table border='1' style='border-collapse: collapse; width: 100%; text-align: right;'>
                <tr style='background-color: #f2f2f2;'><th>المجال</th><th>التفاصيل</th></tr>
                <tr><td>اسم التجمع</td><td>{تفاصيل_الحملة['group_name']}</td></tr>
                <tr><td>المدينة</td><td>{تفاصيل_الحملة['city']}</td></tr>
                <tr><td>التاريخ</td><td>{تفاصيل_الحملة['date']}</td></tr>
            </table>
            <p>يمكنك الوصول للموقع عبر الرابط: <a href='{تفاصيل_الحملة['map_link']}'>خرائط جوجل</a></p>
        </div>
        """
        
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = ايميل_المراقب
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, ايميل_المراقب, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"خطأ في إرسال البريد: {e}")
        return False
