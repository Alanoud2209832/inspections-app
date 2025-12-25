import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. إعدادات الصفحة الأساسية
st.set_page_config(page_title="نظام الرقابة الذكي", layout="wide", page_icon="🚀")

# 2. إنشاء الاتصال بجداول جوجل (يستخدم Secrets تلقائياً)
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. روابط ملفات Google Sheets الخاصة بكِ
URL_OBSERVERS = "https://docs.google.com/spreadsheets/d/1xpp9MmUSjBg4EgGXeRIGwQghtMxAYuW2lFL8YSRZJRg/edit?usp=sharing"
URL_CAMPAIGNS = "https://docs.google.com/spreadsheets/d/1aApLVf9PPIcClcelziEzUqwWXFrc8a4pZgfqesQoQBw/edit?usp=sharing"

# 4. وظائف جلب البيانات
@st.cache_data(ttl=60)
def get_observers_data():
    return conn.read(spreadsheet=URL_OBSERVERS)

@st.cache_data(ttl=60)
def get_campaigns_data():
    return conn.read(spreadsheet=URL_CAMPAIGNS)

# 5. القائمة الجانبية (Sidebar)
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3203/3203071.png", width=100)
st.sidebar.title("نظام الرقابة الذكي")
menu = ["📊 لوحة التحكم", "➕ إنشاء حملة جديدة", "📅 سجل الحملات", "👥 دليل المراقبين"]
choice = st.sidebar.radio("القائمة الرئيسية", menu)

st.sidebar.divider()
if st.sidebar.button("تحديث البيانات 🔄"):
    st.cache_data.clear()
    st.rerun()

# --- الصفحات ---

# الصفحة الأولى: لوحة التحكم
if choice == "📊 لوحة التحكم":
    st.title("📈 لوحة مؤشرات النظام")
    col1, col2, col3 = st.columns(3)
    
    try:
        obs_df = get_observers_data()
        camp_df = get_campaigns_data()
        
        col1.metric("عدد المراقبين", len(obs_df))
        col2.metric("الحملات المجدولة", len(camp_df))
        col3.metric("الحالة التشغيلية", "نشط")
        
        st.divider()
        st.subheader("آخر 5 حملات تم إنشاؤها")
        st.table(camp_df.tail(5))
    except:
        st.info("بانتظار مزامنة البيانات من Google Sheets...")

# الصفحة الثانية: نموذج إنشاء حملة (الفورم)
elif choice == "➕ إنشاء حملة جديدة":
    st.title("📝 تخطيط حملة رقابية جديدة")
    st.write("يرجى تعبئة الحقول أدناه لجدولة الحملة وتوثيق أهدافها.")

    with st.form("new_campaign_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            camp_name = st.text_input("اسم الحملة", placeholder="مثال: جولة تفتيش المنشآت")
            camp_date = st.date_input("تاريخ الحملة", datetime.now())
            location = st.text_input("الموقع الجغرافي (الحي/المدينة)")
        
        with col2:
            participants = st.multiselect("الجهات المشاركة", ["وزارة التجارة", "البلدية", "الشرطة", "الموارد البشرية", "الغذاء والدواء"])
            scope = st.selectbox("نطاق الحملة", ["نطاق ضيق (مبنى/منشأة)", "بلدية فرعية/حي", "منطقة كاملة"])
            camp_time = st.time_input("وقت الانطلاق")

        objectives = st.text_area("الأهداف الرقابية المستهدفة", placeholder="اكتب بالتفصيل ما تهدف إليه هذه الحملة...")
        
        submit_button = st.form_submit_button("حفظ الحملة في قاعدة البيانات 💾")
        
        if submit_button:
            if camp_name and objectives:
                try:
                    # قراءة البيانات الحالية
                    existing_data = get_campaigns_data()
                    
                    # تجهيز السطر الجديد
                    new_row = pd.DataFrame([{
                        "اسم التجمع": camp_name,
                        "التاريخ": str(camp_date),
                        "الوقت": str(camp_time),
                        "الموقع": location,
                        "الجهات المشاركة": ", ".join(participants),
                        "النطاق الجغرافي": scope,
                        "الأهداف": objectives
                    }])
                    
                    # دمج السطر الجديد مع البيانات القديمة
                    updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                    
                    # تحديث ملف Google Sheets
                    conn.update(spreadsheet=URL_CAMPAIGNS, data=updated_df)
                    
                    st.success(f"✅ تم حفظ حملة '{camp_name}' بنجاح في Google Sheets!")
                    st.balloons()
                    st.cache_data.clear()
                except Exception as e:
                    st.error(f"حدث خطأ أثناء الحفظ: {e}")
            else:
                st.warning("⚠️ فضلاً، تأكد من إدخال اسم الحملة والأهداف الرقابية.")

# الصفحة الثالثة: سجل الحملات
elif choice == "📅 سجل الحملات":
    st.title("📋 سجل الحملات التاريخي")
    try:
        df = get_campaigns_data()
        search_query = st.text_input("🔍 بحث في السجل (بالاسم، الموقع، أو التاريخ)")
        if search_query:
            df = df[df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]
        st.dataframe(df, use_container_width=True)
    except:
        st.error("لا يمكن الوصول لبيانات سجل الحملات حالياً.")

# الصفحة الرابعة: دليل المراقبين
elif choice == "👥 دليل المراقبين":
    st.title("👨‍✈️ قاعدة بيانات المراقبين والجهات")
    try:
        df = get_observers_data()
        search_obs = st.text_input("🔍 بحث عن مراقب (بالاسم، المدينة، أو رقم الجوال)")
        if search_obs:
            df = df[df.apply(lambda row: row.astype(str).str.contains(search_obs, case=False).any(), axis=1)]
        st.dataframe(df, use_container_width=True)
    except:
        st.error("لا يمكن الوصول لبيانات المراقبين حالياً.")
