import streamlit as st
from database import init_db, add_campaign, get_campaigns, get_observers, add_observer, get_observers_by_region
import pandas as pd

# إعدادات الصفحة الرسمية
st.set_page_config(page_title="نظام الإدارة الرقابية", layout="wide")

# تطبيق نمط CSS بسيط لتحسين المظهر
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #004b87; color: white; }
    .stSelectbox, .stTextInput, .stNumberInput { border-radius: 5px; }
    </style>
    """, unsafe_allow_ Harris=True)

init_db()

# القائمة الجانبية
st.sidebar.title("نظام الإدارة الميدانية")
menu = ["الرئيسية والإحصائيات", "إضافة حملة جديدة", "سجل الحملات", "دليل المراقبين"]
choice = st.sidebar.selectbox("القائمة:", menu)

# --- الصفحة الرئيسية ---
if choice == "الرئيسية والإحصائيات":
    st.header("لوحة المؤشرات العامة")
    df_c = get_campaigns()
    df_o = get_observers()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("إجمالي الحملات", len(df_c))
    with col2:
        st.metric("المراقبين المسجلين", len(df_o))
    with col3:
        st.metric("الحالة", "متصل")
    
    st.subheader("آخر الحملات المضافة")
    st.dataframe(df_c.head(5), use_container_width=True)

# --- صفحة إضافة حملة جديدة ---
elif choice == "إضافة حملة جديدة":
    st.header("نموذج تسجيل حملة ميدانية")
    
    # اختيار المنطقة خارج النموذج لتحديث البيانات فوراً
    region = st.selectbox("منطقة العمل:", ["الرياض", "مكة المكرمة", "المدينة المنورة", "الشرقية", "عسير", "تبوك", "القصيم"])
    
    filtered_names = get_observers_by_region(region)
    
    if not filtered_names:
        st.warning(f"لا يوجد مراقبين مسجلين في منطقة {region}. يرجى تحديث دليل المراقبين أولاً.")

    with st.container():
        with st.form("campaign_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                selected_date = st.date_input("تاريخ الحملة")
                days_ar = {"Saturday": "السبت", "Sunday": "الأحد", "Monday": "الاثنين", "Tuesday": "الثلاثاء", "Wednesday": "الأربعاء", "Thursday": "الخميس", "Friday": "الجمعة"}
                full_date_str = f"{days_ar.get(selected_date.strftime('%A'))} {selected_date.strftime('%Y-%m-%d')}"
                
                city = st.text_input("المدينة")
                group_name = st.text_input("اسم التجمع المستهدف")
            
            with col2:
                leader = st.selectbox("قائد الفريق:", options=filtered_names if filtered_names else ["لا يوجد"])
                participants = st.multiselect("المراقبين المشاركين:", options=filtered_names)
                survey_count = st.number_input("عدد المنشآت (المسح الميداني)", min_value=0, step=1)
            
            st.divider()
            inspectors = st.text_area("مأموري الضبط المشاركين من جهات أخرى")
            map_link = st.text_input("رابط الموقع الجغرافي (Google Maps)")
            
            submitted = st.form_submit_button("اعتماد وحفظ البيانات")
            
            if submitted:
                if group_name and filtered_names and leader != "لا يوجد":
                    p_str = ", ".join(participants) if participants else "لا يوجد"
                    data = {
                        "day_date": full_date_str, "region": region, "city": city,
                        "group_name": group_name, "leader": leader, "participants": p_str,
                        "survey_count": int(survey_count), "inspectors": inspectors, "map_link": map_link
                    }
                    try:
                        add_campaign(data)
                        st.success("تم حفظ بيانات الحملة بنجاح في سجل النظام.")
                    except Exception as e:
                        st.error(f"حدث خطأ أثناء الحفظ: {e}")
                else:
                    st.error("يرجى إكمال البيانات الأساسية قبل الحفظ.")

# --- صفحة سجل الحملات ---
elif choice == "سجل الحملات":
    st.header("سجل الجولات الرقابية")
    df = get_campaigns()
    
    # فلتر بسيط للبحث
    search = st.text_input("البحث عن حملة (اسم التجمع أو القائد):")
    if search:
        df = df[df['اسم التجمع'].str.contains(search) | df['قائد الفريق'].str.contains(search)]
        
    st.dataframe(df, use_container_width=True)

# --- صفحة دليل المراقبين ---
elif choice == "دليل المراقبين":
    st.header("إدارة القوى البشرية (المراقبين)")
    
    tab1, tab2 = st.tabs(["قائمة المراقبين", "تسجيل مراقب جديد"])
    
    with tab1:
        st.dataframe(get_observers(), use_container_width=True)
        
    with tab2:
        with st.form("obs_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("الاسم الرباعي")
                email = st.text_input("البريد الإلكتروني")
                phone = st.text_input("رقم التواصل", value="966")
            with c2:
                status = st.selectbox("الحالة العملية", ["على رأس العمل", "مجاز"])
                region_obs = st.selectbox("المنطقة الإدارية", ["الرياض", "مكة المكرمة", "المدينة المنورة", "الشرقية", "عسير", "تبوك", "القصيم"])
                work = st.text_input("جهة الانتداب / العمل")

            if st.form_submit_button("تسجيل المراقب"):
                if len(name) > 5 and "@" in email:
                    add_observer({"name": name, "email": email, "status": status, "phone": phone, "work": work, "region": region_obs, "city": ""})
                    st.success(f"تم تسجيل المراقب {name} في النظام.")
                else:
                    st.error("يرجى التحقق من صحة البيانات المدخلة.")
