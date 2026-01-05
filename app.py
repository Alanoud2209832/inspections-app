import streamlit as st
from database import (init_db, add_campaign, get_campaigns, get_observers, 
                      add_observer, get_observers_by_region, check_observer_login, get_campaigns_for_observer)
import pandas as pd

st.set_page_config(page_title="نظام الإدارة الرقابية", layout="wide")

# تصميم رسمي وتعديل CSS
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #004b87; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

init_db()

# --- منطق تسجيل الدخول باستخدام Session State ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['user_role'] = None
    st.session_state['user_name'] = None

if not st.session_state['logged_in']:
    st.header("تسجيل الدخول للنظام")
    login_type = st.radio("نوع الدخول:", ["مراقب ميداني", "إدارة النظام"], horizontal=True)
    
    with st.container():
        if login_type == "إدارة النظام":
            password = st.text_input("كلمة مرور الإدارة:", type="password")
            if st.button("دخول الإدارة"):
                if password == "Admin2026": # يمكنك تغيير كلمة المرور هنا
                    st.session_state['logged_in'] = True
                    st.session_state['user_role'] = 'admin'
                    st.rerun()
                else:
                    st.error("كلمة المرور غير صحيحة")
        
        else:
            phone = st.text_input("أدخل رقم الجوال المسجل (بدون +966):", placeholder="5xxxxxxxx")
            if st.button("دخول المراقب"):
                # تأكدي أن الرقم في قاعدة البيانات يبدأ بـ 966 أو حسب إدخالك
                full_phone = f"966{phone}" if not phone.startswith("966") else phone
                obs_name = check_observer_login(full_phone)
                if obs_name:
                    st.session_state['logged_in'] = True
                    st.session_state['user_role'] = 'observer'
                    st.session_state['user_name'] = obs_name
                    st.rerun()
                else:
                    st.error("رقم الجوال غير مسجل في دليل المراقبين")
    st.stop()

# --- بعد تسجيل الدخول ---

# زر خروج في القائمة الجانبية
if st.sidebar.button("تسجيل الخروج"):
    st.session_state['logged_in'] = False
    st.rerun()

# --- واجهة المدير ---
if st.session_state['user_role'] == 'admin':
    st.sidebar.title("لوحة الإدارة")
    menu = ["الإحصائيات العامة", "إضافة حملة جديدة", "سجل كافة الحملات", "إدارة المراقبين"]
    choice = st.sidebar.selectbox("القائمة الإجرائية:", menu)

    if choice == "الإحصائيات العامة":
        st.header("مؤشرات أداء النظام")
        df_c = get_campaigns()
        df_o = get_observers()
        c1, c2 = st.columns(2)
        c1.metric("إجمالي الحملات", len(df_c))
        c2.metric("المراقبين المعتمدين", len(df_o))
        st.dataframe(df_c.head(10), use_container_width=True)

    elif choice == "إضافة حملة جديدة":
        st.header("تسجيل حملة ميدانية")
        region = st.selectbox("المنطقة:", ["الرياض", "مكة المكرمة", "المدينة المنورة", "الشرقية", "عسير", "تبوك", "القصيم"])
        filtered_names = get_observers_by_region(region)
        
        with st.form("camp_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                selected_date = st.date_input("التاريخ")
                city = st.text_input("المدينة")
                group_name = st.text_input("اسم التجمع")
            with col2:
                leader = st.selectbox("قائد الفريق:", options=filtered_names if filtered_names else ["لا يوجد"])
                participants = st.multiselect("المشاركين:", options=filtered_names)
                survey_count = st.number_input("المنشآت", min_value=0, step=1)
            
            inspectors = st.text_area("مأموري الضبط")
            map_link = st.text_input("رابط الخرائط")
            
            if st.form_submit_button("اعتماد الحفظ"):
                if group_name and leader != "لا يوجد":
                    p_str = ", ".join(participants) if participants else "لا يوجد"
                    add_campaign({"day_date": str(selected_date), "region": region, "city": city, 
                                  "group_name": group_name, "leader": leader, "participants": p_str,
                                  "survey_count": int(survey_count), "inspectors": inspectors, "map_link": map_link})
                    st.success("تم الحفظ")

    elif choice == "سجل كافة الحملات":
        st.header("سجل الرقابة الموحد")
        st.dataframe(get_campaigns(), use_container_width=True)

    elif choice == "إدارة المراقبين":
        st.header("دليل القوى العاملة")
        tab1, tab2 = st.tabs(["العرض", "الإضافة"])
        with tab1: st.dataframe(get_observers(), use_container_width=True)
        with tab2:
            with st.form("obs"):
                n = st.text_input("الاسم")
                e = st.text_input("الإيميل")
                p = st.text_input("الجوال (966xxxxxxxxx)")
                r = st.selectbox("المنطقة", ["الرياض", "مكة المكرمة", "المدينة المنورة", "الشرقية", "عسير", "تبوك", "القصيم"])
                w = st.selectbox("جهة العمل", ["وزارة البيئة والمياه والزراعة", "وزارة الموارد البشرية والتنمية الاجتماعية", "هيئة الزكاة والضريبة والجمارك"])
                if st.form_submit_button("حفظ"):
                    add_observer({"name": n, "email": e, "status": "نشط", "phone": p, "work": w, "region": r, "city": ""})
                    st.success("تمت الإضافة")

# --- واجهة المراقب ---
elif st.session_state['user_role'] == 'observer':
    st.sidebar.title(f"أهلاً، {st.session_state['user_name']}")
    st.header(f"قائمة الحملات الميدانية الخاصة بك")
    
    # جلب الحملات المخصصة لهذا المراقب فقط
    my_campaigns = get_campaigns_for_observer(st.session_state['user_name'])
    
    if my_campaigns.empty:
        st.info("لا توجد حملات مسجلة باسمك حالياً.")
    else:
        for index, row in my_campaigns.iterrows():
            with st.expander(f"📅 {row['اليوم والتاريخ']} - {row['اسم التجمع']} ({row['المدينة']})"):
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"**الدور:** {'قائد فريق' if row['قائد الفريق'] == st.session_state['user_name'] else 'مراقب مشارك'}")
                    st.write(f"**المنطقة:** {row['المنطقة']}")
                    st.write(f"**عدد المنشآت المستهدفة:** {row['عدد المنشآت بناءً على المسح الميداني']}")
                with c2:
                    st.write(f"**المشاركين الآخرين:** {row['المراقبين المشاركين']}")
                    if row['موقع التجمع على الخرائط']:
                        st.link_button("📍 الانتقال لموقع المهمة", row['موقع التجمع على الخرائط'])
                st.info(f"مأموري الضبط: {row['مأموري الضبط من وزارة التجارة']}")
