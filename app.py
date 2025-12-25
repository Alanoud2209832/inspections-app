import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام الرقابة الذكي", layout="wide", page_icon="🚀")

# 2. إنشاء الاتصال (سيبحث تلقائياً عن [connections.gsheets] في Secrets)
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. روابط الملفات (استخدمي روابط المتصفح العادية هنا)
URL_OBSERVERS = "https://docs.google.com/spreadsheets/d/1xpp9MmUSjBg4EgGXeRIGwQghtMxAYuW2lFL8YSRZJRg/edit?usp=sharing"
URL_CAMPAIGNS = "https://docs.google.com/spreadsheets/d/1aApLVf9PPIcClcelziEzUqwWXFrc8a4pZgfqesQoQBw/edit?usp=sharing"

# 4. وظائف جلب البيانات مع التحديث التلقائي
@st.cache_data(ttl=10) # تحديث كل 10 ثوانٍ لضمان رؤية البيانات الجديدة فوراً
def get_data(url):
    return conn.read(spreadsheet=url)

# 5. القائمة الجانبية
st.sidebar.title("نظام الرقابة الذكي")
menu = ["📊 لوحة التحكم", "➕ إنشاء حملة جديدة", "📅 سجل الحملات", "👥 دليل المراقبين"]
choice = st.sidebar.radio("القائمة الرئيسية", menu)

# --- محتوى الصفحات ---

if choice == "📊 لوحة التحكم":
    st.title("📈 ملخص النظام")
    try:
        obs_df = get_data(URL_OBSERVERS)
        camp_df = get_data(URL_CAMPAIGNS)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("عدد المراقبين", len(obs_df))
        c2.metric("الحملات المسجلة", len(camp_df))
        c3.metric("حالة الربط", "متصل ✅")
    except Exception as e:
        st.error(f"تأكد من إعدادات Secrets وصلاحيات الملف: {e}")

elif choice == "➕ إنشاء حملة جديدة":
    st.title("📝 نموذج جدولة حملة")
    
    with st.form("add_campaign_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("اسم الحملة")
            date = st.date_input("التاريخ", datetime.now())
            loc = st.text_input("الموقع")
        with col2:
            time = st.time_input("الوقت")
            parts = st.multiselect("الجهات", ["التجارة", "البلدية", "الشرطة"])
            scope = st.selectbox("النطاق", ["حي", "مدينة", "منطقة"])
            
        goals = st.text_area("الأهداف الرقابية")
        
        if st.form_submit_button("حفظ الحملة 💾"):
            if name and goals:
                # جلب البيانات الحالية
                current_df = conn.read(spreadsheet=URL_CAMPAIGNS)
                # إضافة السطر الجديد
                new_row = pd.DataFrame([{
                    "اسم التجمع": name, "التاريخ": str(date), "الوقت": str(time),
                    "الموقع": loc, "الجهات المشاركة": ", ".join(parts),
                    "النطاق": scope, "الأهداف": goals
                }])
                updated_df = pd.concat([current_df, new_row], ignore_index=True)
                # الحفظ الفعلي
                conn.update(spreadsheet=URL_CAMPAIGNS, data=updated_df)
                st.success("تم الحفظ بنجاح!")
                st.balloons()
                st.cache_data.clear()
            else:
                st.warning("أكمل البيانات المطلوبة")

elif choice == "📅 سجل الحملات":
    st.title("📋 سجل العمليات")
    st.dataframe(get_data(URL_CAMPAIGNS), use_container_width=True)

elif choice == "👥 دليل المراقبين":
    st.title("👨‍✈️ بيانات المراقبين")
    st.dataframe(get_data(URL_OBSERVERS), use_container_width=True)
