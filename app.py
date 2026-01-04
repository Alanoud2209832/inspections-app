import streamlit as st
from database import init_db, add_campaign, get_campaigns, get_observers, add_observer, get_observers_by_region
import pandas as pd

# إعدادات الصفحة الرسمية
st.set_page_config(page_title="نظام الإدارة الرقابية", layout="wide")

# تحسين مظهر الواجهة عبر CSS
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        width: 100%; 
        border-radius: 5px; 
        height: 3em; 
        background-color: #004b87; 
        color: white; 
        font-weight: bold;
    }
    .stSelectbox, .stTextInput, .stNumberInput { border-radius: 5px; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #004b87; }
    </style>
    """, unsafe_allow_html=True)

# تهيئة قاعدة البيانات
init_db()

# القائمة الجانبية
st.sidebar.title("نظام الإدارة الرقابية")
menu = ["الرئيسية", "إضافة حملة جديدة", "سجل الحملات", "دليل المراقبين"]
choice = st.sidebar.selectbox("القائمة :", menu)

# --- الصفحة الرئيسية ---
if choice == "الرئيسية ":
    st.header("لوحة المؤشرات العامة")
    df_c = get_campaigns()
    df_o = get_observers()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("إجمالي الحملات المنفذة", len(df_c))
    with col2:
        st.metric("عدد المراقبين المعتمدين", len(df_o))
    with col3:
        st.metric("حالة النظام", "نشط")
    
    st.divider()
    st.subheader("أحدث النشاطات الميدانية")
    st.dataframe(df_c.head(10), use_container_width=True)

# --- صفحة إضافة حملة جديدة ---
elif choice == "إضافة حملة جديدة":
    st.header("نموذج تسجيل حملة رقابية")
    
    # اختيار المنطقة
    region = st.selectbox("المنطقة الإدارية للعمل:", ["الرياض", "مكة المكرمة", "المدينة المنورة", "الشرقية", "عسير", "تبوك", "القصيم"])
    
    from database import get_observers_by_region
    filtered_names = get_observers_by_region(region)
    
    if not filtered_names:
        st.info(f"تنبيه: لا يوجد مراقبين مسجلين حالياً في منطقة {region}.")

    with st.container():
        with st.form("campaign_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                selected_date = st.date_input("تاريخ تنفيذ الحملة")
                days_ar = {
                    "Saturday": "السبت", "Sunday": "الأحد", "Monday": "الاثنين", 
                    "Tuesday": "الثلاثاء", "Wednesday": "الأربعاء", "Thursday": "الخميس", "Friday": "الجمعة"
                }
                day_name = days_ar.get(selected_date.strftime('%A'))
                full_date_str = f"{day_name} {selected_date.strftime('%Y-%m-%d')}"
                
                city = st.text_input("المدينة / المحافظة")
                group_name = st.text_input("اسم التجمع المستهدف")
            
            with col2:
                leader = st.selectbox("قائد الفريق :", options=filtered_names if filtered_names else ["لا يوجد أسماء"])
                participants = st.multiselect("المراقبين المشاركين:", options=filtered_names)
                survey_count = st.number_input("إجمالي المنشآت (المسح الميداني)", min_value=0, step=1)
            
            st.markdown("---")
            inspectors = st.text_area("مأموري الضبط المشاركين من وزارة التجارة")
            map_link = st.text_input(" الموقع الجغرافي (Google Maps)")
            
            submitted = st.form_submit_button("اعتماد وحفظ بيانات الحملة")
            
            if submitted:
                if group_name and filtered_names and leader != "لا يوجد أسماء":
                    p_str = ", ".join(participants) if participants else "لا يوجد"
                    data = {
                        "day_date": full_date_str, "region": region, "city": city,
                        "group_name": group_name, "leader": leader, "participants": p_str,
                        "survey_count": int(survey_count), "inspectors": inspectors, "map_link": map_link
                    }
                    try:
                        add_campaign(data)
                        st.success("تم تسجيل بيانات الحملة في سجل النظام بنجاح.")
                    except Exception as e:
                        st.error(f"خطأ في الاتصال بقاعدة البيانات: {e}")
                else:
                    st.error("يرجى استكمال الحقول الأساسية (اسم التجمع وقائد الفريق).")

# --- صفحة سجل الحملات ---
elif choice == "سجل الحملات":
    st.header("سجل الجولات الرقابية ")
    df = get_campaigns()
    
    # محرك البحث المحدث (المنطقة والمدينة)
    search_query = st.text_input("البحث السريع (حسب المنطقة أو المدينة):")
    if search_query:
        # البحث في عمود المنطقة وعمود المدينة
        df = df[df['المنطقة'].str.contains(search_query, na=False) | 
                df['المدينة'].str.contains(search_query, na=False)]
        
    st.dataframe(df, use_container_width=True)

# --- صفحة دليل المراقبين ---
elif choice == "دليل المراقبين":
    st.header("إدارة بيانات المراقبين")
    
    tab1, tab2 = st.tabs(["قائمة المراقبين", "إضافة مراقب"])
    
    with tab1:
        st.dataframe(get_observers(), use_container_width=True)
        
    with tab2:
        st.subheader("تسجيل بيانات مراقب جديد")
        with st.form("obs_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("الاسم الكامل")
                email = st.text_input("البريد الإلكتروني ")
                phone = st.text_input("رقم الجوال ", value="966")
            with c2:
                status = st.selectbox("الحالة الحالية", ["على رأس العمل", "في مهمة عمل", "مجاز"])
                region_obs = st.selectbox("المنطقة الإدارية التابع لها", ["الرياض", "مكة المكرمة", "المدينة المنورة", "الشرقية", "عسير", "تبوك", "القصيم"])
                # تعديل حقل جهة العمل إلى قائمة خيارات
                work = st.selectbox("جهة العمل", [
                    "وزارة البيئة والمياه والزراعة", 
                    "وزارة الموارد البشرية والتنمية الاجتماعية", 
                    "هيئة الزكاة والضريبة والجمارك"
                ])

            if st.form_submit_button("حفظ البيانات"):
                if len(name) > 5 and "@" in email:
                    add_observer({
                        "name": name, "email": email, "status": status, 
                        "phone": phone, "work": work, "region": region_obs, "city": ""
                    })
                    st.success(f"تمت إضافة المراقب {name} بنجاح.")
                    st.rerun()
                else:
                    st.error("يرجى التأكد من كتابة الاسم الكامل والبريد الإلكتروني بشكل صحيح.")
