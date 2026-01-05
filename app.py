import streamlit as st
from database import (init_db, اضافة_حملة, جلب_الحملات, جلب_المراقبين, 
                      اضافة_مراقب, جلب_المراقبين_حسب_المنطقة, تحقق_دخول_المراقب, جلب_حملات_المراقب)
import pandas as pd

st.set_page_config(page_title="نظام الإدارة الرقابية", layout="wide")

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
        كلمة_المرور = st.text_input("كلمة مرور الإدارة:", type="password")
        if st.button("دخول الإدارة"):
            if كلمة_المرور == "Admin2026":
                st.session_state['logged_in'] = True
                st.session_state['user_role'] = 'admin'
                st.rerun()
            else:
                st.error("كلمة المرور غير صحيحة")
    else:
        ايميل_المراقب = st.text_input("أدخل البريد الإلكتروني المعتمد:")
        if st.button("دخول المراقب"):
            الاسم = تحقق_دخول_المراقب(ايميل_المراقب)
            if الاسم:
                st.session_state['logged_in'] = True
                st.session_state['user_role'] = 'observer'
                st.session_state['user_name'] = الاسم
                st.rerun()
            else:
                st.error("البريد الإلكتروني غير مسجل.")
    st.stop()

if st.sidebar.button("تسجيل الخروج"):
    st.session_state.clear()
    st.rerun()

# --- واجهة المدير ---
if st.session_state['user_role'] == 'admin':
    st.sidebar.title("لوحة الإدارة")
    menu = ["الإحصائيات", "إضافة حملة جديدة", "سجل الحملات", "دليل المراقبين"]
    choice = st.sidebar.selectbox("القائمة الإجرائية:", menu)

    if choice == "الإحصائيات":
        st.header("مؤشرات النظام")
        حملات = جلب_الحملات()
        مراقبون = جلب_المراقبين()
        c1, c2 = st.columns(2)
        c1.metric("إجمالي الحملات", len(حملات))
        c2.metric("المراقبين المعتمدين", len(مراقبون))
        st.dataframe(حملات.head(10), use_container_width=True)

    elif choice == "إضافة حملة جديدة":
        st.header("تسجيل حملة ميدانية")
        المنطقة = st.selectbox("المنطقة:", ["الرياض", "مكة المكرمة", "المدينة المنورة", "الشرقية", "عسير", "تبوك", "القصيم"])
        المراقبين_المتاحين = جلب_المراقبين_حسب_المنطقة(المنطقة)
        
        with st.form("نموذج_الحملة", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                تاريخ = st.date_input("تاريخ الحملة")
                مدينة = st.text_input("المدينة")
                تجمع = st.text_input("اسم التجمع")
            with col2:
                قائد = st.selectbox("قائد الفريق:", options=المراقبين_المتاحين if المراقبين_المتاحين else ["لا يوجد"])
                مشاركين = st.multiselect("المراقبين المشاركين:", options=المراقبين_المتاحين)
                عدد = st.number_input("عدد المنشآت", min_value=0, step=1)
            
            ضبط = st.text_area("مأموري الضبط")
            رابط = st.text_input("رابط الخرائط")
            
            if st.form_submit_button("حفظ البيانات"):
                if تجمع and قائد != "لا يوجد":
                    مشاركين_نص = ", ".join(مشاركين) if مشاركين else "لا يوجد"
                    بيانات_للحفظ = {
                        "تاريخ": str(تاريخ), "منطقة": المنطقة, "مدينة": مدينة,
                        "تجمع": تجمع, "قائد": قائد, "مشاركين": مشاركين_نص,
                        "عدد": int(عدد), "ضبط": ضبط, "رابط": رابط
                    }
                    اضافة_حملة(بيانات_للحفظ)
                    st.success("تم الحفظ بنجاح")
                else:
                    st.error("تأكد من إدخال اسم التجمع وقائد الفريق")

    elif choice == "سجل الحملات":
        st.header("سجل الرقابة")
        df = جلب_الحملات()
        بحث = st.text_input("البحث بالمنطقة أو المدينة:")
        if بحث:
            df = df[df['المنطقة'].str.contains(بحث, na=False) | df['المدينة'].str.contains(بحث, na=False)]
        st.dataframe(df, use_container_width=True)

    elif choice == "دليل المراقبين":
        st.header("إدارة المراقبين")
        t1, t2 = st.tabs(["القائمة", "إضافة"])
        with t1: st.dataframe(جلب_المراقبين(), use_container_width=True)
        with t2:
            with st.form("اضافة_مراقب"):
                n = st.text_input("الاسم")
                e = st.text_input("الايميل")
                p = st.text_input("الجوال")
                r = st.selectbox("المنطقة", ["الرياض", "مكة المكرمة", "المدينة المنورة", "الشرقية", "عسير", "تبوك", "القصيم"])
                w = st.selectbox("جهة العمل", ["وزارة البيئة والمياه والزراعة", "وزارة الموارد البشرية والتنمية الاجتماعية", "هيئة الزكاة والضريبة والجمارك"])
                if st.form_submit_button("حفظ المراقب"):
                    اضافة_مراقب({"name": n, "email": e, "status": "نشط", "phone": p, "work": w, "region": r, "city": ""})
                    st.success("تمت الإضافة")

# --- واجهة المراقب ---
elif st.session_state['user_role'] == 'observer':
    st.header(f"أهلاً بك، {st.session_state['user_name']}")
    حملاتي = جلب_حملات_المراقب(st.session_state['user_name'])
    
    if حملاتي.empty:
        st.info("لا توجد مهام حالياً.")
    else:
        for idx, row in حملاتي.iterrows():
            with st.expander(f"📍 {row['اسم التجمع']} - {row['اليوم والتاريخ']}"):
                st.write(f"**المدينة:** {row['المدينة']}")
                st.write(f"**مأموري الضبط:** {row['مأموري الضبط من وزارة التجارة']}")
                if row['موقع التجمع على الخرائط']:
                    st.link_button("فتح الموقع", row['موقع التجمع على الخرائط'])
