import streamlit as st
from database import (init_db, اضافة_حملة, جلب_الحملات, جلب_المراقبين, 
                      اضافة_مراقب, جلب_مراقبين_بالجهة, تحقق_دخول_المراقب, جلب_حملات_المراقب)
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="نظام الإدارة الرقابية", layout="wide")

# تصميم الواجهة
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #004b87; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

init_db()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['user_role'] = None
    st.session_state['user_name'] = None

if not st.session_state['logged_in']:
    st.header("بوابة تسجيل الدخول")
    login_type = st.radio("نوع الدخول:", ["مراقب ميداني", "إدارة النظام"], horizontal=True)
    
    if login_type == "إدارة النظام":
        password = st.text_input("كلمة مرور الإدارة:", type="password")
        if st.button("دخول"):
            if password == "Admin2026":
                st.session_state['logged_in'] = True
                st.session_state['user_role'] = 'admin'
                st.rerun()
            else:
                st.error("خطأ في كلمة المرور")
    else:
        email = st.text_input("البريد الإلكتروني:")
        if st.button("دخول المراقب"):
            name = تحقق_دخول_المراقب(email)
            if name:
                st.session_state['logged_in'] = True
                st.session_state['user_role'] = 'observer'
                st.session_state['user_name'] = name
                st.rerun()
            else:
                st.error("الحساب غير مسجل")
    st.stop()

if st.sidebar.button("تسجيل الخروج"):
    st.session_state.clear()
    st.rerun()

# --- لوحة المدير ---
if st.session_state['user_role'] == 'admin':
    st.sidebar.title("لوحة الإدارة")
    menu = ["الإحصائيات", "إضافة حملة جديدة", "سجل الحملات", "دليل المراقبين"]
    choice = st.sidebar.selectbox("القائمة:", menu)

    if choice == "الإحصائيات":
        st.header("مؤشرات النظام")
        df_c = جلب_الحملات()
        st.metric("إجمالي الحملات", len(df_c))
        st.dataframe(df_c, use_container_width=True)

    elif choice == "إضافة حملة جديدة":
        st.header("تسجيل حملة جديدة")
        
        region = st.selectbox("المنطقة:", ["الرياض", "مكة المكرمة", "المدينة المنورة", "الشرقية", "عسير", "تبوك", "القصيم"])
        
        # اختيار مأموري الضبط (جهات الضبط)
        inspectors_list = st.multiselect("مأموري الضبط (الجهات المشاركة):", [
            "وزارة التجارة",
            "وزارة البلديات والإسكان",
            "وزارة الموارد البشرية والتنمية الاجتماعية",
            "وزارة البيئة والمياه والزراعة",
            "هيئة الزكاة والضريبة والجمارك"
        ])

        # جلب المراقبين التابعين للجهات المختارة فقط
        filtered_observers = جلب_مراقبين_بالجهة(region, inspectors_list)
        
        with st.form("camp_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                date_val = st.date_input("تاريخ الحملة")
                city = st.text_input("المدينة")
                group_name = st.text_input("اسم التجمع")
            with col2:
                # قائد الفريق يفلتر بناءً على الجهة المختارة
                leader = st.selectbox("قائد الفريق الميداني:", 
                                     options=filtered_observers if filtered_observers else ["يرجى اختيار جهة أولاً"])
                participants = st.multiselect("المراقبين المشاركين:", options=filtered_observers)
                survey_count = st.number_input("إجمالي المنشآت", min_value=0, step=1)
            
            map_link = st.text_input("رابط الموقع الجغرافي")
            
            if st.form_submit_button("اعتماد وحفظ البيانات"):
                if group_name and leader != "يرجى اختيار جهة أولاً":
                    # تحويل التاريخ لاسم اليوم بالعربي
                    days_map = {
                        'Monday': 'الاثنين', 'Tuesday': 'الثلاثاء', 'Wednesday': 'الأربعاء',
                        'Thursday': 'الخميس', 'Friday': 'الجمعة', 'Saturday': 'السبت', 'Sunday': 'الأحد'
                    }
                    day_name = days_map[date_val.strftime('%A')]
                    
                    data = {
                        "day": day_name,
                        "date": date_val,
                        "region": region,
                        "city": city,
                        "group_name": group_name,
                        "leader": leader,
                        "participants": ", ".join(participants) if participants else "لا يوجد",
                        "survey_count": int(survey_count),
                        "inspectors": ", ".join(inspectors_list),
                        "map_link": map_link
                    }
                    اضافة_حملة(data)
                    st.success(f"تم الحفظ بنجاح ليوم {day_name}")
                else:
                    st.error("يرجى اختيار جهة عمل (مأموري ضبط) وتعبئة الحقول الأساسية")

    elif choice == "سجل الحملات":
        st.header("سجل الجولات")
        st.dataframe(جلب_الحملات(), use_container_width=True)

    elif choice == "دليل المراقبين":
        st.header("إدارة المراقبين")
        t1, t2 = st.tabs(["قائمة المراقبين", "إضافة مراقب"])
        with t1:
            st.dataframe(جلب_المراقبين(), use_container_width=True)
        with t2:
            with st.form("add_obs"):
                n = st.text_input("الاسم الكامل")
                e = st.text_input("الايميل")
                p = st.text_input("الجوال")
                r = st.selectbox("المنطقة", ["الرياض", "مكة المكرمة", "المدينة المنورة", "الشرقية", "عسير", "تبوك", "القصيم"])
                w = st.selectbox("جهة العمل", [
                    "وزارة التجارة", 
                    "وزارة البلديات والإسكان", 
                    "وزارة الموارد البشرية والتنمية الاجتماعية", 
                    "وزارة البيئة والمياه والزراعة", 
                    "هيئة الزكاة والضريبة والجمارك"
                ])
                if st.form_submit_button("حفظ"):
                    اضافة_مراقب({"name": n, "email": e, "status": "نشط", "phone": p, "work": w, "region": r, "city": ""})
                    st.success("تمت الإضافة")

# --- لوحة المراقب ---
elif st.session_state['user_role'] == 'observer':
    st.header(f"مرحباً {st.session_state['user_name']}")
    my_tasks = جلب_حملات_المراقب(st.session_state['user_name'])
    if my_tasks.empty:
        st.info("لا توجد مهام مسجلة.")
    else:
        for _, row in my_tasks.iterrows():
            with st.expander(f"📅 {row['اليوم']} - {row['التاريخ']} | {row['اسم التجمع']}"):
                st.write(f"**المدينة:** {row['المدينة']}")
                st.write(f"**الجهات المشاركة:** {row['مأموري الضبط من وزارة التجارة']}")
                if row['موقع التجمع على الخرائط']:
                    st.link_button("موقع التجمع", row['موقع التجمع على الخرائط'])
