import streamlit as st
from database import (init_db, اضافة_حملة, جلب_الحملات, جلب_المراقبين, 
                      اضافة_مراقب, جلب_مراقبين_بالجهة, تحقق_دخول_المراقب, 
                      جلب_حملات_المراقب, get_engine, ارسل_بريد_تكليف)
import pandas as pd
from datetime import datetime
from sqlalchemy import text

st.set_page_config(page_title="نظام الإدارة الرقابية", layout="wide", page_icon="🛡️")

# تهيئة الجداول عند التشغيل
try:
    init_db()
except Exception as e:
    st.error(f"فشل الاتصال بقاعدة البيانات. تأكدي من Secrets. الخطأ: {e}")
    st.stop()

if 'logged_in' not in st.session_state:
    st.session_state.update({'logged_in': False, 'user_role': None, 'user_name': None})

# --- تنسيق CSS للواجهة ---
if not st.session_state['logged_in']:
    st.markdown("""
        <style>
        [data-testid="stSidebar"] { display: none; }
        .main-title { color: #1E3A8A; font-size: 28px; font-weight: bold; text-align: center; }
        .sub-title { color: #64748b; text-align: center; margin-bottom: 30px; }
        </style>
        """, unsafe_allow_html=True)

    if 'login_mode' not in st.session_state:
        st.session_state['login_mode'] = None

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="main-title">🛡️ نظام الإدارة الرقابية</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">اختر نوع الحساب للمتابعة</div>', unsafe_allow_html=True)

        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("👤 مراقب ميداني", use_container_width=True):
                st.session_state['login_mode'] = 'observer'
        with btn_col2:
            if st.button("⚙️ إدارة النظام", use_container_width=True):
                st.session_state['login_mode'] = 'admin'

        st.divider()

        if st.session_state['login_mode'] == 'admin':
            with st.form("admin_login"):
                st.subheader("دخول الإدارة")
                pwd = st.text_input("كلمة المرور", type="password")
                if st.form_submit_button("دخول", use_container_width=True):
                    if pwd == "Admin2026":
                        st.session_state.update({'logged_in': True, 'user_role': 'admin'})
                        st.rerun()
                    else: st.error("كلمة المرور خاطئة")

        elif st.session_state['login_mode'] == 'observer':
            with st.form("observer_login"):
                st.subheader("دخول المراقبين")
                email_login = st.text_input("البريد الإلكتروني")
                if st.form_submit_button("تحقق ودخول", use_container_width=True):
                    res = تحقق_دخول_المراقب(email_login)
                    if res:
                        st.session_state.update({'logged_in': True, 'user_role': 'observer', 'user_name': res[0]})
                        st.rerun()
                    else: st.error("البريد غير مسجل")
    st.stop()

# زر تسجيل الخروج
if st.sidebar.button("تسجيل الخروج"):
    st.session_state.clear()
    st.rerun()

# --- صلاحيات الإدارة ---
if st.session_state['user_role'] == 'admin':
    menu = ["الإحصائيات", "إضافة حملة جديدة", "سجل الحملات", "دليل المراقبين"]
    choice = st.sidebar.selectbox("القائمة:", menu)

    if choice == "الإحصائيات":
        st.header("📊 لوحة المؤشرات")
        df = جلب_الحملات()
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("إجمالي الحملات", len(df))
            st.bar_chart(df["المنطقة"].value_counts())
        else:
            st.info("لا توجد بيانات.")

    elif choice == "إضافة حملة جديدة":
        st.header("تسجيل حملة ميدانية")
        region = st.selectbox("المنطقة:", ["الرياض", "مكة المكرمة", "المدينة المنورة", "الشرقية", "عسير", "تبوك", "القصيم", "الباحة", "الجوف", "الحدود الشمالية"])
        inspectors_choice = st.multiselect("الجهات المشاركة:", ["وزارة التجارة", "وزارة الموارد البشرية", "وزارة البيئة", "هيئة الزكاة"])
        filtered_obs = جلب_مراقبين_بالجهة(region, inspectors_choice)

        with st.form("camp_form"):
            col1, col2 = st.columns(2)
            with col1:
                date_val = st.date_input("تاريخ الحملة")
                city = st.text_input("المدينة")
                group_name = st.text_input("اسم التجمع")
            with col2:
                leader = st.selectbox("قائد الفريق:", options=filtered_obs if filtered_obs else ["لا يوجد مراقبين"])
                count = st.number_input("المنشآت", min_value=0)
            
            if st.form_submit_button("حفظ وإرسال تكليف"):
                if group_name and leader != "لا يوجد مراقبين":
                    data = {
                        "day": "يوم", "date": str(date_val), "region": region, "city": city,
                        "group_name": group_name, "leader": leader, "participants": "", 
                        "survey_count": int(count), "inspectors": ", ".join(inspectors_choice), "map_link": ""
                    }
                    اضافة_حملة(data)
                    st.success(f"تم الحفظ بنجاح وتكليف {leader}")
                else:
                    st.error("أكمل البيانات")

    elif choice == "دليل المراقبين":
        t1, t2 = st.tabs(["القائمة", "إضافة مراقب"])
        with t1: st.dataframe(جلب_المراقبين(), use_container_width=True)
        with t2:
            with st.form("add_obs"):
                n = st.text_input("الاسم")
                e = st.text_input("الايميل")
                p = st.text_input("الجوال (يبدأ بـ 966)", value="966")
                r = st.selectbox("المنطقة", ["الرياض", "مكة المكرمة", "المدينة المنورة", "الشرقية"])
                if st.form_submit_button("حفظ"):
                    if len(p) == 12 and "@" in e:
                        اضافة_مراقب({"name": n, "email": e, "status": "نشط", "phone": p, "work": "جهة", "region": r, "city": ""})
                        st.success("تمت الإضافة")
                    else: st.error("تأكد من البيانات")

# --- صلاحيات المراقب ---
elif st.session_state['user_role'] == 'observer':
    st.header(f"👋 أهلاً، {st.session_state['user_name']}")
    tasks = جلب_حملات_المراقب(st.session_state['user_name'])
    st.dataframe(tasks, use_container_width=True)
