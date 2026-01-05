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

# --- تنسيق CSS لتحسين الواجهة وتوسيطها ---
# --- تنسيق CSS المطور للواجهة ---
st.markdown("""
    <style>
    /* إخفاء القائمة الجانبية في صفحة تسجيل الدخول */
    [data-testid="stSidebar"] { display: none; }
    
    /* تنسيق الحاوية الرئيسية */
    .login-container {
        max-width: 450px;
        margin: auto;
        padding: 40px;
        background: white;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    /* تنسيق العناوين */
    .main-title { color: #0B3B17; font-size: 55px; font-weight: bold; margin-bottom: 5px; text-align: center; }
    .sub-title { color: #64748b; margin-bottom: 30px; font-size: 14px; text-align: center; }
    
    /* تنسيق الحقول */
    .stTextInput > div > div > input {
        border-radius: 10px;
        height: 45px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- واجهة تسجيل الدخول المحدثة ---
if not st.session_state['logged_in']:
    # استخدام session_state لتحديد أي نموذج يظهر (مراقب أو مدير)
    if 'login_mode' not in st.session_state:
        st.session_state['login_mode'] = None

    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="main-title">نظام تنظيم الحملات الرقابية</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">اختر نوع الحساب للوصول إلى صلاحياتك</div>', unsafe_allow_html=True)

        # صف الأزرار لاختيار نوع الدخول
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            if st.button("👤 مراقب ", use_container_width=True):
                st.session_state['login_mode'] = 'observer'
        
        with btn_col2:
            if st.button("⚙️ إدارة النظام", use_container_width=True):
                st.session_state['login_mode'] = 'admin'

        st.divider()

        # إظهار النموذج بناءً على الاختيار
        if st.session_state['login_mode'] == 'admin':
            with st.form("admin_login"):
                st.subheader("تسجيل دخول للنظام")
                pwd = st.text_input("كلمة المرور", type="password", placeholder="••••••••")
                if st.form_submit_button("دخول", use_container_width=True):
                    if pwd == "Admin2026":
                        st.session_state.update({'logged_in': True, 'user_role': 'admin'})
                        st.rerun()
                    else:
                        st.error("كلمة المرور خاطئة")

        elif st.session_state['login_mode'] == 'observer':
            with st.form("observer_login"):
                st.subheader("دخول المراقبين")
                email = st.text_input("الرجاء ادخال البريد الإلكتروني", placeholder="example@domain.com")
                if st.form_submit_button("دخول", use_container_width=True):
                    name = تحقق_دخول_المراقب(email)
                    if name:
                        st.session_state.update({'logged_in': True, 'user_role': 'observer', 'user_name': name})
                        st.rerun()
                    else:
                        st.error("البريد الالكتروني غير مسجل")
        
        else:
            st.info("الرجاء اختيار  نوع الحساب للمتابعة")

    st.stop()

if st.sidebar.button("تسجيل الخروج"):
    st.session_state.clear()
    st.rerun()

# --- لوحة الإدارة ---
if st.session_state['user_role'] == 'admin':
    menu = ["الإحصائيات", "إضافة حملة جديدة", "سجل الحملات", "دليل المراقبين"]
    choice = st.sidebar.selectbox("القائمة:", menu)

    # --- 1. صفحة الإحصائيات المحدثة ---
    if choice == "الإحصائيات":
        st.header("📊 لوحة المؤشرات العامة")
        df = جلب_الحملات()
        
        if not df.empty:
            # استخدام الأسماء الحقيقية كما هي في قاعدة بياناتك
            col_sites = "عدد المنشآت بناءً على المسح الميدا"
            col_inspectors = "مأموري الضبط من وزارة التجارة"
            col_region = "الالمنطقة" if "الالمنطقة" in df.columns else "المنطقة"

            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("إجمالي الحملات", len(df))
            with c2:
                if col_sites in df.columns:
                    # تحويل القيم لرقمية وحساب المجموع
                    total_sites = pd.to_numeric(df[col_sites], errors='coerce').sum()
                    st.metric("إجمالي المنشآت الممسوحة", int(total_sites) if not pd.isna(total_sites) else 0)
                else:
                    st.metric("إجمالي المنشآت الممسوحة", "0")
            with c3:
                st.metric("المناطق النشطة", df[col_region].nunique() if col_region in df.columns else 0)

            st.divider()
            
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                if col_region in df.columns:
                    st.subheader("توزيع الحملات حسب المناطق")
                    st.bar_chart(df[col_region].value_counts())
            
            with col_chart2:
                if col_inspectors in df.columns:
                    st.subheader("مشاركة الجهات الضبطية")
                    # تنظيف البيانات وتقسيمها إذا كانت تحتوي على أسماء جهات متعددة
                    inspectors_list = df[col_inspectors].dropna().astype(str).str.split(', ').explode()
                    st.bar_chart(inspectors_list.value_counts())
        else:
            st.info("لا توجد بيانات مسجلة حالياً لعرض الإحصائيات.")

    elif choice == "إضافة حملة جديدة":
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
                count = st.number_input("إجمالي المنشآت بناءً على المسح", min_value=0, step=1)
            
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
                else: st.error("أكمل الحقول المطلوبة واختيار القائد")

    elif choice == "سجل الحملات":
        st.header("سجل الحملات الميدانية")
        st.dataframe(جلب_الحملات(), use_container_width=True)

    elif choice == "دليل المراقبين":
        st.header("إدارة بيانات المراقبين")
        t1, t2 = st.tabs(["قائمة المراقبين", "إضافة مراقب جديد"])
        with t1: 
            st.dataframe(جلب_المراقبين(), use_container_width=True)
        with t2:
            with st.form("add_obs_form_v2"):
                col_obs1, col_obs2 = st.columns(2)
                with col_obs1:
                    n = st.text_input("الاسم الكامل")
                    e = st.text_input("البريد الإلكتروني")
                    phone = st.text_input("رقم الجوال") 
                with col_obs2:
                    w = st.selectbox("الجهة التابع لها", ["وزارة التجارة", "وزارة البلديات والإسكان", "وزارة الموارد البشرية والتنمية الاجتماعية", "وزارة البيئة والمياه والزراعة", "هيئة الزكاة والضريبة والجمارك"])
                    r = st.selectbox("المنطقة الإدارية", ["الرياض", "مكة المكرمة", "المدينة المنورة", "الشرقية", "عسير", "تبوك", "القصيم"])
                
                if st.form_submit_button("حفظ بيانات المراقب"):
                    if n and e and phone:
                        اضافة_مراقب({
                            "name": n, "email": e, "status": "نشط", 
                            "phone": phone, "work": w, "region": r, "city": ""
                        })
                        st.success(f"تمت إضافة المراقب {n} بنجاح")
                    else:
                        st.warning("يرجى إكمال الاسم، الايميل، ورقم الجوال")

# --- لوحة المراقب ---
elif st.session_state['user_role'] == 'observer':
    st.header(f"أهلاً بك، {st.session_state['user_name']}")
    st.subheader("مهامك الميدانية")
    tasks = جلب_حملات_المراقب(st.session_state['user_name'])
    if not tasks.empty:
        st.dataframe(tasks, use_container_width=True)
    else:
        st.info("لا توجد حملات مسجلة باسمك حالياً.")
