import streamlit as st
from database import init_db, add_campaign, get_campaigns, upload_old_data
import pandas as pd

# تهيئة الصفحة وقاعدة البيانات
st.set_page_config(page_title="نظام الرقابة - Neon DB", layout="wide")
init_db()

# القائمة الجانبية
st.sidebar.title("🛠️ لوحة التحكم")
menu = ["📊 الإحصائيات", "➕ إضافة حملة", "📋 السجل العام", "⚙️ إعدادات (نقل البيانات)"]
choice = st.sidebar.radio("القائمة", menu)

if choice == "📊 الإحصائيات":
    st.title("📈 ملخص العمليات")
    df = get_campaigns()
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("إجمالي الحملات في القاعدة", len(df))
        c2.metric("إجمالي المنشآت", int(df["عدد المنشآت بناءً على المسح الميداني"].sum()))
        c3.metric("المصدر", "قاعدة بيانات Neon ☁️")
        st.subheader("أحدث البيانات المضافة")
        st.dataframe(df.head(10), use_container_width=True)
    else:
        st.info("قاعدة البيانات فارغة حالياً.")

elif choice == "➕ إضافة حملة":
    st.title("📝 إدخال بيانات جديدة")
    with st.form("main_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            day_date = st.text_input("اليوم والتاريخ")
            region = st.selectbox("المنطقة", ["الرياض", "مكة المكرمة", "الشرقية", "عسير", "القصيم"])
            city = st.text_input("المدينة")
            group_name = st.text_input("اسم التجمع")
        with col2:
            survey_count = st.number_input("عدد المنشآت", min_value=0)
            inspectors = st.text_area("مأموري الضبط")
            map_link = st.text_input("رابط الخرائط")
        
        if st.form_submit_button("حفظ في قاعدة البيانات 💾"):
            data = {"day_date": day_date, "region": region, "city": city, 
                    "group_name": group_name, "survey_count": survey_count, 
                    "inspectors": inspectors, "map_link": map_link}
            add_campaign(data)
            st.success("تم الحفظ بنجاح في Neon!")

elif choice == "📋 السجل العام":
    st.title("🗂️ قاعدة بيانات الرقابة")
    df = get_campaigns()
    search = st.text_input("🔍 ابحث (بالمدينة، الاسم، أو المنطقة)...")
    if search:
        df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]
    st.dataframe(df, use_container_width=True)

elif choice == "⚙️ إعدادات (نقل البيانات)":
    st.title("⚙️ نقل البيانات القديمة")
    st.warning("استخدم هذه الخاصية لمرة واحدة فقط لنقل بيانات ملف الإكسل القديم إلى Neon.")
    uploaded_file = st.file_uploader("ارفع ملف الإكسل القديم (CSV أو Excel)", type=["csv", "xlsx"])
    if uploaded_file and st.button("بدأ عملية النقل للقاعدة 🚀"):
        old_df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)
        upload_old_data(old_df)
        st.success("تم نقل جميع البيانات القديمة إلى Neon بنجاح!")
