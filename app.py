import streamlit as st
from database import (init_db, اضافة_حملة, جلب_الحملات, جلب_المراقبين, 
                      اضافة_مراقب, جلب_مراقبين_بالجهة, تحقق_دخول_المراقب, جلب_حملات_المراقب)
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="نظام الإدارة الرقابية", layout="wide")

# محاولة تهيئة الجداول عند بدء التطبيق
try:
    init_db()
except Exception as e:
    st.error(f"فشل الاتصال بقاعدة البيانات. تأكدي من الرابط في Secrets. الخطأ: {e}")
    st.stop()

if 'logged_in' not in st.session_state:
    st.session_state.update({'logged_in': False, 'user_role': None, 'user_name': None})

# واجهة تسجيل الدخول
if not st.session_state['logged_in']:
    st.header("بوابة تسجيل الدخول")
    login_type = st.radio("نوع الدخول:", ["مراقب ميداني", "إدارة النظام"], horizontal=True)
    if login_type == "إدارة النظام":
        pwd = st.text_input("كلمة المرور:", type="password")
        if st.button("دخول"):
            if pwd == "Admin2026":
                st.session_state.update({'logged_in': True, 'user_role': 'admin'})
                st.rerun()
            else: st.error("كلمة المرور خاطئة")
    else:
        email = st.text_input("البريد الإلكتروني:")
        if st.button("دخول المراقب"):
            name = تحقق_دخول_المراقب(email)
            if name:
                st.session_state.update({'logged_in': True, 'user_role': 'observer', 'user_name': name})
                st.rerun()
            else: st.error("البريد غير مسجل")
    st.stop()

if st.sidebar.button("تسجيل الخروج"):
    st.session_state.clear()
    st.rerun()

# --- لوحة الإدارة ---
if st.session_state['user_role'] == 'admin':
    menu = ["الإحصائيات", "إضافة حملة جديدة", "سجل الحملات", "دليل المراقبين"]
    choice = st.sidebar.selectbox("القائمة:", menu)

    if choice == "إضافة حملة جديدة":
        st.header("تسجيل حملة ميدانية")
        region = st.selectbox("المنطقة:", ["الرياض", "مكة المكرمة", "المدينة المنورة", "الشرقية", "عسير", "تبوك", "القصيم"])
        
        inspectors_choice = st.multiselect("مأموري الضبط (الجهات المشاركة):", [
            "وزارة التجارة", "وزارة البلديات والإسكان", 
            "وزارة الموارد البشرية والتنمية الاجتماعية", 
            "وزارة البيئة والمياه والزراعة", "هيئة الزكاة والضريبة والجمارك"
        ])

        filtered_obs = جلب_مراقبين_بالجهة(region, inspectors_choice)

        with st.form("camp_form_final"):
            col1, col2 = st.columns(2)
            with col1:
                date_val = st.date_input("تاريخ الحملة")
                city = st.text_input("المدينة")
                group_name = st.text_input("اسم التجمع")
            with col2:
                leader = st.selectbox("قائد الفريق:", options=filtered_obs if filtered_obs else ["يرجى اختيار جهة أولاً"])
                participants = st.multiselect("المراقبين المشاركين:", options=filtered_obs)
                count = st.number_input("إجمالي المنشآت", min_value=0, step=1)
            
            map_link = st.text_input("رابط الخرائط")
            
            if st.form_submit_button("حفظ البيانات"):
                if group_name and leader != "يرجى اختيار جهة أولاً":
                    days_map = {'Monday':'الاثنين','Tuesday':'الثلاثاء','Wednesday':'الأربعاء','Thursday':'الخميس','Friday':'الجمعة','Saturday':'السبت','Sunday':'الأحد'}
                    day_name = days_map[date_val.strftime('%A')]
                    
                    data = {
                        "day": day_name, "date": date_val, "region": region, "city": city,
                        "group_name": group_name, "leader": leader, 
                        "participants": ", ".join(participants), "survey_count": int(count),
                        "inspectors": ", ".join(inspectors_choice), "map_link": map_link
                    }
                    اضافة_حملة(data)
                    st.success("تم الحفظ بنجاح")
                else: st.error("أكمل الحقول المطلوبة")

    elif choice == "سجل الحملات":
        st.dataframe(جلب_الحملات(), use_container_width=True)

    elif choice == "دليل المراقبين":
        t1, t2 = st.tabs(["قائمة المراقبين", "إضافة مراقب"])
        with t1: st.dataframe(جلب_المراقبين(), use_container_width=True)
        with t2:
            with st.form("add_obs_form"):
                n = st.text_input("الاسم")
                e = st.text_input("الايميل")
                w = st.selectbox("الجهة", ["وزارة التجارة", "وزارة البلديات والإسكان", "وزارة الموارد البشرية والتنمية الاجتماعية", "وزارة البيئة والمياه والزراعة", "هيئة الزكاة والضريبة والجمارك"])
                r = st.selectbox("المنطقة", ["الرياض", "مكة المكرمة", "المدينة المنورة", "الشرقية", "عسير", "تبوك", "القصيم"])
                if st.form_submit_button("حفظ"):
                    اضافة_مراقب({"name": n, "email": e, "status": "نشط", "phone": "", "work": w, "region": r, "city": ""})
                    st.success("تمت الإضافة")

# --- لوحة المراقب ---
elif st.session_state['user_role'] == 'observer':
    st.header(f"أهلاً {st.session_state['user_name']}")
    tasks = جلب_حملات_المراقب(st.session_state['user_name'])
    st.dataframe(tasks, use_container_width=True)
