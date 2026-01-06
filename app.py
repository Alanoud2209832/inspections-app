import streamlit as st
from database import (init_db, اضافة_حملة, جلب_الحملات, جلب_المراقبين, 
                      اضافة_مراقب, جلب_مراقبين_بالجهة, تحقق_دخول_المراقب, 
                      جلب_بريد_المراقب_بالاسم, 
                      جلب_حملات_المراقب, get_engine, ارسل_بريد_تكليف)
import pandas as pd
from datetime import datetime
from sqlalchemy import text

st.set_page_config(page_title="نظام الإدارة الرقابية", layout="wide", page_icon="🛡️")

# محاولة تهيئة الجداول عند بدء التطبيق
try:
    init_db()
except Exception as e:
    st.error(f"فشل الاتصال بقاعدة البيانات. تأكدي من الرابط في Secrets. الخطأ: {e}")
    st.stop()

if 'logged_in' not in st.session_state:
    st.session_state.update({'logged_in': False, 'user_role': None, 'user_name': None})

# --- تنسيق CSS المطور للواجهة ---
if not st.session_state['logged_in']:
    st.markdown("""
        <style>
        [data-testid="stSidebar"] { display: none; }
        .login-container { max-width: 450px; margin: auto; padding: 40px; background: white; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); text-align: center; }
        .main-title { color: #1E3A8A; font-size: 28px; font-weight: bold; margin-bottom: 5px; text-align: center; }
        .sub-title { color: #64748b; margin-bottom: 30px; font-size: 14px; text-align: center; }
        </style>
        """, unsafe_allow_html=True)

    if 'login_mode' not in st.session_state:
        st.session_state['login_mode'] = None

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="main-title">🛡️ نظام الإدارة الرقابية</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">اختر نوع الحساب للوصول إلى صلاحياتك</div>', unsafe_allow_html=True)

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
                pwd = st.text_input("كلمة المرور", type="password", placeholder="••••••••")
                if st.form_submit_button("دخول النظام", use_container_width=True):
                    if pwd == "Admin2026":
                        st.session_state.update({'logged_in': True, 'user_role': 'admin'})
                        st.rerun()
                    else: st.error("كلمة المرور خاطئة")

        elif st.session_state['login_mode'] == 'observer':
            with st.form("observer_login"):
                st.subheader("دخول المراقبين")
                email_login = st.text_input("البريد الإلكتروني", placeholder="example@domain.com")
                if st.form_submit_button("تحقق ودخول", use_container_width=True):
                    res = تحقق_دخول_المراقب(email_login)
                    if res:
                        st.session_state.update({'logged_in': True, 'user_role': 'observer', 'user_name': res[0]})
                        st.rerun()
                    else: st.error("البريد غير مسجل")
        else:
            st.info("الرجاء النقر على نوع الحساب أعلاه للمتابعة")
    st.stop()

if st.sidebar.button("تسجيل الخروج"):
    st.session_state.clear()
    st.rerun()

# --- لوحة الإدارة ---
if st.session_state['user_role'] == 'admin':
    menu = ["الإحصائيات", "إضافة حملة جديدة", "سجل الحملات", "دليل المراقبين"]
    choice = st.sidebar.selectbox("القائمة:", menu)

    if choice == "الإحصائيات":
        st.header("📊 لوحة المؤشرات العامة")
        df_campaigns = جلب_الحملات()
        df_observers = جلب_المراقبين()
        
        c1, c2 = st.columns(2)
        with c1:
            st.metric("إجمالي الحملات", len(df_campaigns) if not df_campaigns.empty else 0)
        with c2:
            st.metric("عدد المراقبين المسجلين", len(df_observers) if not df_observers.empty else 0)
            
        st.divider()
        
        if not df_campaigns.empty:
            col_region = "المنطقة"
            col_inspectors = "مأموري الضبط من وزارة التجارة"
            
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.subheader("توزيع الحملات حسب المناطق")
                if col_region in df_campaigns.columns:
                    st.bar_chart(df_campaigns[col_region].value_counts())
            with col_chart2:
                if col_inspectors in df_campaigns.columns:
                    st.subheader("مشاركة الجهات")
                    list_insp = df_campaigns[col_inspectors].dropna().astype(str).str.split(', ').explode()
                    st.bar_chart(list_insp.value_counts())
        else:
            st.info("لا توجد بيانات حملات لعرض الرسوم البيانية.")

    elif choice == "إضافة حملة جديدة":
        st.header("تسجيل حملة ميدانية")
        region = st.selectbox("المنطقة:", ["الرياض", "مكة المكرمة", "المدينة المنورة", "الشرقية", "عسير", "تبوك", "القصيم", "الباحة", "الحدود الشمالية", "الجوف"])
        inspectors_choice = st.multiselect("الجهات المشاركة:", ["وزارة التجارة", "وزارة البلديات والإسكان", "وزارة الموارد البشرية والتنمية الاجتماعية", "وزارة البيئة والمياه والزراعة", "هيئة الزكاة والضريبة والجمارك"])
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
            
            if st.form_submit_button("حفظ البيانات وإرسال تكليف"):
                if group_name and leader != "يرجى اختيار جهة أولاً":
                    days_map = {'Monday':'الاثنين','Tuesday':'الثلاثاء','Wednesday':'الأربعاء','Thursday':'الخميس','Friday':'الجمعة','Saturday':'السبت','Sunday':'الأحد'}
                    data = {
                        "day": days_map[date_val.strftime('%A')],
                        "date": str(date_val),
                        "region": region,
                        "city": city,
                        "group_name": group_name,
                        "leader": leader,
                        "participants": ", ".join(participants),
                        "survey_count": int(count),
                        "inspectors": ", ".join(inspectors_choice),
                        "map_link": map_link
                    }
                    اضافة_حملة(data)
                    
                    try:
                        res = جلب_بريد_المراقب_بالاسم(leader)
                        if res:
                            ارسل_بريد_تكليف(res[1], res[0], data)
                            st.success(f"✅ تم حفظ الحملة وإرسال بريد تكليف إلى {leader}")
                            st.balloons()
                        else:
                            st.warning("⚠️ تم حفظ الحملة، ولكن لم يتم العثور على بريد القائد في 'دليل المراقبين'.")
                    except Exception as e:
                        st.error(f"❌ حدث خطأ أثناء إرسال البريد: {e}")
                else:
                    st.error("يرجى إكمال البيانات واختيار القائد")

    elif choice == "سجل الحملات":
        st.header("سجل الحملات الميدانية")
        st.dataframe(جلب_الحملات(), use_container_width=True)

    elif choice == "دليل المراقبين":
        t1, t2 = st.tabs(["قائمة المراقبين", "إضافة مراقب جديد"])
        with t1: 
            df_obs = جلب_المراقبين()
            st.dataframe(df_obs, use_container_width=True)
        with t2:
            st.subheader("إدخال بيانات مراقب جديد")
            with st.form("add_obs_v2", clear_on_submit=True):
                n = st.text_input("الاسم الكامل")
                e = st.text_input("البريد الإلكتروني", placeholder="example@domain.com")
                p = st.text_input("رقم الجوال", value="966", help="يجب أن يبدأ بـ 966 ويتكون من 12 رقماً")
                w = st.selectbox("الجهة", ["وزارة التجارة", "وزارة البلديات والإسكان", "وزارة الموارد البشرية والتنمية الاجتماعية", "وزارة البيئة والمياه والزراعة", "هيئة الزكاة والضريبة والجمارك"])
                r = st.selectbox("المنطقة", ["الرياض", "مكة المكرمة", "المدينة المنورة", "الشرقية", "عسير", "تبوك", "القصيم", "الباحة", "الحدود الشمالية", "الجوف"])
                
                if st.form_submit_button("حفظ بيانات المراقب 💾"):
                    if len(n) < 3:
                        st.error("❌ يرجى إدخال اسم حقيقي.")
                    elif "@" not in e:
                        st.error("❌ صيغة البريد الإلكتروني غير صحيحة.")
                    else:
                        اضافة_مراقب({"name": n, "email": e, "status": "نشط", "phone": p, "work": w, "region": r, "city": ""})
                        st.success(f"✅ تمت إضافة {n} بنجاح")
                        st.balloons()

elif st.session_state['user_role'] == 'observer':
    st.header(f"👋 أهلاً بك، {st.session_state['user_name']}")
    st.subheader("📋 المهام الموكلة إليك")
    tasks = جلب_حملات_المراقب(st.session_state['user_name'])
    if not tasks.empty:
        st.dataframe(tasks, use_container_width=True)
    else:
        st.info("لا توجد مهام مسجلة باسمك حالياً.")
