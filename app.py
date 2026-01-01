import streamlit as st
from database import init_db, add_campaign, get_campaigns # استدعاء الوظائف من الملف الآخر

# إعداد الصفحة
st.set_page_config(page_title="نظام الرقابة - Neon DB", layout="wide")

# تهيئة قاعدة البيانات عند تشغيل التطبيق
init_db()

# القائمة الجانبية
st.sidebar.title("🛠️ لوحة التحكم")
menu = ["📊 الإحصائيات", "➕ إضافة حملة", "📋 سجل البيانات"]
choice = st.sidebar.radio("القائمة", menu)

if choice == "📊 الإحصائيات":
    st.title("📈 ملخص العمليات")
    df = get_campaigns()
    st.metric("إجمالي الحملات", len(df))
    st.dataframe(df.head(5), use_container_width=True)

elif choice == "➕ إضافة حملة":
    st.title("📝 إدخال جديد")
    with st.form("neon_form", clear_on_submit=True):
        # ... (نفس مدخلات الفورم السابقة) ...
        day_date = st.text_input("اليوم والتاريخ")
        region = st.selectbox("المنطقة", ["الرياض", "مكة المكرمة", "الشرقية"])
        city = st.text_input("المدينة")
        group_name = st.text_input("اسم التجمع")
        survey_count = st.number_input("عدد المنشآت", min_value=0)
        inspectors = st.text_area("مأموري الضبط")
        map_link = st.text_input("رابط الخريطة")
        
        if st.form_submit_button("حفظ 💾"):
            data = {
                "day_date": day_date, "region": region, "city": city,
                "group_name": group_name, "survey_count": survey_count,
                "inspectors": inspectors, "map_link": map_link
            }
            add_campaign(data) # استدعاء وظيفة الحفظ
            st.success("تم الحفظ بنجاح!")

elif choice == "📋 سجل البيانات":
    st.title("🗂️ عرض سجلات Neon")
    df = get_campaigns() # استدعاء وظيفة الجلب
    st.dataframe(df, use_container_width=True)
