import streamlit as st
from database import init_db, add_campaign, get_campaigns, get_observers
import pandas as pd

# إعدادات الصفحة
st.set_page_config(page_title="نظام الرقابة الذكي", layout="wide", page_icon="🛡️")

# تهيئة قاعدة البيانات عند تشغيل التطبيق
init_db()

# القائمة الجانبية
st.sidebar.title("🛠️ القائمة الرئيسية")
menu = ["📊 الإحصائيات", "➕ إضافة حملة جديدة", "📋 سجل الحملات", "👥 دليل المراقبين"]
choice = st.sidebar.radio("انتقل إلى:", menu)

# --- صفحة الإحصائيات ---
if choice == "📊 الإحصائيات":
    st.title("📈 لوحة مؤشرات النظام")
    df_c = get_campaigns()
    df_o = get_observers()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي الحملات", len(df_c))
    col2.metric("عدد المراقبين المسجلين", len(df_o))
    col3.metric("حالة القاعدة", "Neon PostgreSQL ✅")

    st.divider()
    if not df_c.empty:
        st.subheader("أحدث الحملات الميدانية")
        st.dataframe(df_c.head(10), use_container_width=True)

# --- صفحة إضافة حملة ---
elif choice == "➕ إضافة حملة جديدة":
    st.title("📝 إدخال بيانات حملة ميدانية")
    with st.form("add_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            day_date = st.text_input("اليوم والتاريخ")
            region = st.selectbox("المنطقة", ["الرياض", "مكة المكرمة", "المدينة المنورة", "الشرقية", "عسير", "تبوك", "القصيم"])
            city = st.text_input("المدينة")
            group_name = st.text_input("اسم التجمع")
        with c2:
            survey_count = st.number_input("عدد المنشآت", min_value=0, step=1)
            inspectors = st.text_area("مأموري الضبط")
            map_link = st.text_input("رابط الخرائط (Google Maps)")
        
        if st.form_submit_button("حفظ البيانات في السحابة 💾"):
            if group_name and city:
                data = {
                    "day_date": day_date, "region": region, "city": city,
                    "group_name": group_name, "survey_count": survey_count,
                    "inspectors": inspectors, "map_link": map_link
                }
                add_campaign(data)
                st.success(f"تم تسجيل حملة {group_name} بنجاح!")
                st.balloons()
            else:
                st.warning("يرجى إكمال البيانات الأساسية.")

# --- صفحة سجل الحملات ---
elif choice == "📋 سجل الحملات":
    st.title("🗂️ سجل جميع الجولات الميدانية")
    df = get_campaigns()
    search = st.text_input("🔍 بحث عن حملة...")
    if search:
        df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]
    st.dataframe(df, use_container_width=True)

# --- صفحة دليل المراقبين ---
elif choice == "👥 دليل المراقبين":
    st.title("👨‍✈️ دليل مأموري الضبط والمراقبين")
    df_obs = get_observers()
    search_obs = st.text_input("🔍 ابحث عن مراقب (بالاسم أو المنطقة)...")
    if search_obs:
        df_obs = df_obs[df_obs.apply(lambda row: row.astype(str).str.contains(search_obs, case=False).any(), axis=1)]
    st.dataframe(df_obs, use_container_width=True)


elif choice == "👥 دليل المراقبين":
    st.title("👨‍✈️ إدارة مأموري الضبط والمراقبين")
    
    # تقسيم الصفحة إلى تبويبين (Tabs)
    tab1, tab2 = st.tabs(["📋 عرض القائمة", "➕ إضافة مراقب جديد"])
    
    with tab1:
        df_obs = get_observers()
        search_obs = st.text_input("🔍 ابحث عن مراقب (بالاسم، الجوال، أو المدينة)...")
        if search_obs:
            df_obs = df_obs[df_obs.apply(lambda row: row.astype(str).str.contains(search_obs, case=False).any(), axis=1)]
        st.dataframe(df_obs, use_container_width=True)
        
    with tab2:
        st.subheader("إدخال بيانات مراقب جديد")
        with st.form("observer_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("الاسم الكامل")
                email = st.text_input("الايميل")
                phone = st.text_input("رقم الجوال")
                status = st.selectbox("حالة المراقب", ["على راس العمل", "مجاز", "متقاعد"])
            with col2:
                work = st.text_input("جهة العمل", value="هيئة الزكاة والضريبة والجمارك")
                region = st.selectbox("المنطقة ", ["الرياض", "مكة المكرمة", "المدينة المنورة", "الشرقية", "عسير", "الباحة", "تبوك", "القصيم", "حائل", "الجوف", "الحدود الشمالية", "نجران", "جازان"])
                city = st.text_input("المدينة")
            
            if st.form_submit_button("حفظ المراقب 💾"):
                if name and email:
                    from database import add_observer # استدعاء الوظيفة الجديدة
                    obs_data = {
                        "name": name, "email": email, "status": status,
                        "phone": phone, "work": work, "region": region, "city": city
                    }
                    add_observer(obs_data)
                    st.success(f"تمت إضافة المراقب {name} بنجاح!")
                    st.balloons()
                else:
                    st.warning("يرجى إدخال الاسم والايميل على الأقل.")
