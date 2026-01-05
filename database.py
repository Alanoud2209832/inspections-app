import streamlit as st
from database import (init_db, add_campaign, get_campaigns, get_observers, 
                      add_observer, get_observers_by_region, check_observer_login, get_campaigns_for_observer)
import pandas as pd

st.set_page_config(page_title="نظام الإدارة الرقابية", layout="wide")

# تصميم الواجهة الرسمي
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #004b87; color: white; font-weight: bold; }
    .stSelectbox, .stTextInput, .stNumberInput { border-radius: 5px; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #004b87; }
    </style>
    """, unsafe_allow_html=True)

init_db()

# إدارة الجلسة
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['user_role'] = None
    st.session_state['user_name'] = None

# --- واجهة تسجيل الدخول ---
if not st.session_state['logged_in']:
    st.header("بوابة تسجيل الدخول")
    login_type = st.radio("نوع الهوية:", ["مراقب ميداني", "إدارة النظام"], horizontal=True)
    
    with st.container():
        if login_type == "إدارة النظام":
            password = st.text_input("كلمة مرور الإدارة:", type="password")
            if st.button("دخول الإدارة"):
                if password == "Admin2026":
                    st.session_state['logged_in'] = True
                    st.session_state['user_role'] = 'admin'
                    st.rerun()
                else:
                    st.error("كلمة المرور غير صحيحة")
        else:
            email_input = st.text_input("أدخل البريد الإلكتروني المعتمد:")
            if st.button("دخول المراقب"):
                if email_input:
                    obs_name = check_observer_login(email_input)
                    if obs_name:
                        st.session_state['logged_in'] = True
                        st.session_state['user_role'] = 'observer'
                        st.session_state['user_name'] = obs_name
                        st.rerun()
                    else:
                        st.error("البريد الإلكتروني غير مسجل في النظام.")
                else:
                    st.warning("يرجى إدخال البريد الإلكتروني.")
    st.stop()

# زر الخروج
if st.sidebar.button("تسجيل الخروج"):
    st.session_state['logged_in'] = False
    st.rerun()

# --- واجهة المدير ---
if st.session_state['user_role'] == 'admin':
    st.sidebar.title("لوحة الإدارة")
    menu = ["الإحصائيات", "إضافة حملة جديدة", "سجل الحملات", "دليل المراقبين"]
    choice = st.sidebar.selectbox("القائمة الإجرائية:", menu)

    if choice == "الإحصائيات":
        st.header("مؤشرات النظام")
        df_c = get_campaigns()
        df_o = get_observers()
        c1, c2 = st.columns(2)
        c1.metric("إجمالي الحملات", len(df_c))
        c2.metric("المراقبين المعتمدين", len(df_o))
        st.dataframe(df_c.head(10), use_container_width=True)

    elif choice == "إضافة حملة جديدة":
        st.header("تسجيل حملة ميدانية جديدة")
        region = st.selectbox("المنطقة الإدارية:", ["الرياض", "مكة المكرمة", "المدينة المنورة", "الشرقية", "عسير", "تبوك", "القصيم"])
        filtered_names = get_observers_by_region(region)
        
        with st.form("camp_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                selected_date = st.date_input("تاريخ الحملة")
                city = st.text_input("المدينة / المحافظة")
                group_name = st.text_input("اسم التجمع")
            with col2:
                leader = st.selectbox("قائد الفريق الميداني:", options=filtered_names if filtered_names else ["لا يوجد"])
                participants = st.multiselect("المراقبين المشاركين:", options=filtered_names)
                survey_count = st.number_input("إجمالي المنشآت", min_value=0, step=1)
            
            st.markdown("---")
            inspectors = st.text_area("مأموري الضبط المشاركين")
            map_link = st.text_input("رابط الموقع الجغرافي")
            
            # تم تصحيح مكان الزر ليكون داخل النموذج (داخل الـ with)
            if st.form_submit_button("اعتماد وحفظ البيانات"):
                if group_name and leader != "لا يوجد":
                    p_str = ", ".join(participants) if participants else "لا يوجد"
                    data_to_save = {
                        "day_date": str(selected_date), 
                        "region": region, 
                        "city": city, 
                        "group_name": group_name, 
                        "leader": leader, 
                        "participants": p_str,
                        "survey_count": int(survey_count), 
                        "inspectors": inspectors, 
                        "map_link": map_link
                    }
                    try:
                        add_campaign(data_to_save)
                        st.success("تم الحفظ بنجاح")
                    except Exception as e:
                        st.error(f"خطأ في قاعدة البيانات: {e}")
                else:
                    st.error("يرجى استكمال البيانات الأساسية")

    elif choice == "سجل الحملات":
        st.header("سجل الجولات الرقابية")
        df = get_campaigns()
        search_query = st.text_input("البحث السريع (حسب المنطقة أو المدينة):")
        if search_query:
            df = df[df['المنطقة'].str.contains(search_query, na=False) | 
                    df['المدينة'].str.contains(search_query, na=False)]
        st.dataframe(df, use_container_width=True)

    elif choice == "دليل المراقبين":
        st.header("إدارة القوى البشرية")
        tab1, tab2 = st.tabs(["قائمة المراقبين", "إضافة مراقب"])
        with tab1:
            st.dataframe(get_observers(), use_container_width=True)
        with tab2:
            with st.form("obs_form"):
                n = st.text_input("الاسم الكامل")
                e = st.text_input("البريد الإلكتروني الرسمي")
                p = st.text_input("رقم الجوال")
                r = st.selectbox("المنطقة الإدارية", ["الرياض", "مكة المكرمة", "المدينة المنورة", "الشرقية", "عسير", "تبوك", "القصيم"])
                w = st.selectbox("جهة العمل", ["وزارة البيئة والمياه والزراعة", "وزارة الموارد البشرية والتنمية الاجتماعية", "هيئة الزكاة والضريبة والجمارك"])
                if st.form_submit_button("تسجيل المراقب"):
                    add_observer({"name": n, "email": e, "status": "نشط", "phone": p, "work": w, "region": r, "city": ""})
                    st.success("تمت الإضافة بنجاح")

# --- واجهة المراقب ---
elif st.session_state['user_role'] == 'observer':
    st.sidebar.title(f"مرحباً، {st.session_state['user_name']}")
    st.header("جدول المهام الميدانية الخاصة بك")
    
    my_campaigns = get_campaigns_for_observer(st.session_state['user_name'])
    
    if my_campaigns.empty:
        st.info("لا توجد مهام مسجلة باسمك حالياً.")
    else:
        for index, row in my_campaigns.iterrows():
            with st.expander(f"📍 {row['اسم التجمع']} - {row['اليوم والتاريخ']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**المنطقة/المدينة:** {row['المنطقة']} - {row['المدينة']}")
                    st.write(f"**دورك:** {'قائد الفريق' if row['قائد الفريق'] == st.session_state['user_name'] else 'مراقب مشارك'}")
                with col2:
                    st.write(f"**عدد المنشآت:** {row['عدد المنشآت بناءً على المسح الميداني']}")
                    if row['موقع التجمع على الخرائط']:
                        st.link_button("فتح الموقع", row['موقع التجمع على الخرائط'])
                st.markdown(f"**المشاركين الآخرين:** {row['المراقبين المشاركين']}")
