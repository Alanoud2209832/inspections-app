import streamlit as st
from database import init_db, add_campaign, get_campaigns, get_observers, add_observer
import pandas as pd

st.set_page_config(page_title="نظام الرقابة الذكي", layout="wide", page_icon="🛡️")
init_db()

st.sidebar.title("🛠️ القائمة الرئيسية")
menu = ["📊 الإحصائيات", "➕ إضافة حملة جديدة", "📋 سجل الحملات", "👥 دليل المراقبين"]
choice = st.sidebar.radio("انتقل إلى:", menu)

# ... (أكواد الإحصائيات والحملات تبقى كما هي) ...

if choice == "📊 الإحصائيات":
    st.title("📈 لوحة مؤشرات النظام")
    df_c = get_campaigns()
    df_o = get_observers()
    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي الحملات", len(df_c))
    col2.metric("عدد المراقبين", len(df_o))
    col3.metric("حالة القاعدة", "Neon Online ✅")
    st.dataframe(df_c.head(10), use_container_width=True)

elif choice == "➕ إضافة حملة جديدة":
    st.title("📝 إدخال بيانات حملة ميدانية")
    with st.form("add_campaign_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            day_date = st.text_input("اليوم والتاريخ")
            region = st.selectbox("المنطقة", ["الرياض", "مكة المكرمة", "المدينة المنورة", "الشرقية", "عسير", "تبوك", "القصيم"])
            city = st.text_input("المدينة")
            group_name = st.text_input("اسم التجمع")
        with c2:
            survey_count = st.number_input("عدد المنشآت", min_value=0, step=1)
            inspectors = st.text_area("مأموري الضبط")
            map_link = st.text_input("رابط الخرائط")
        if st.form_submit_button("حفظ الحملة 💾"):
            add_campaign({"day_date": day_date, "region": region, "city": city, "group_name": group_name, "survey_count": survey_count, "inspectors": inspectors, "map_link": map_link})
            st.success("تم الحفظ!")

elif choice == "📋 سجل الحملات":
    st.title("🗂️ سجل الجولات الميدانية")
    st.dataframe(get_campaigns(), use_container_width=True)

elif choice == "👥 دليل المراقبين":
    st.title("👨‍✈️ إدارة المراقبين")
    tab1, tab2 = st.tabs(["📋 عرض القائمة", "➕ إضافة مراقب جديد"])
    
    with tab1:
        df_obs = get_observers()
        st.dataframe(df_obs, use_container_width=True)
        
    with tab2:
        st.subheader("إدخال بيانات مراقب جديد")
        with st.form("observer_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("الاسم الكامل")
                # إضافة ميزة التأكد من صيغة الإيميل
                email = st.text_input("الايميل", placeholder="example@domain.com")
                
                # إجبار رقم الجوال على البدء بـ 966
                phone_input = st.text_input("رقم الجوال", value="966", help="ابدأ بـ 966 ثم رقم الجوال")
                
                status = st.selectbox("حالة المراقب", ["على راس العمل", "مجاز", "متقاعد"])
            with col2:
                work = st.selectbox("جهة العمل", [
                    "هيئة الزكاة والضريبة والجمارك",
                    "وزارة البيئة والمياه والزراعة",
                    "وزارة الموارد البشرية والتنمية الاجتماعية"
                ])
                region = st.selectbox("المنطقة ", ["الرياض", "مكة المكرمة", "المدينة المنورة", "الشرقية", "عسير", "الباحة", "تبوك", "القصيم", "حائل", "الجوف", "الحدود الشمالية", "نجران", "جازان"])
                city = st.text_input("المدينة")
            
           if st.form_submit_button("حفظ المراقب 💾"):
                # حساب طول الرقم المدخل
                # 966 (3 أرقام) + 9 أرقام للجوال (مثل 505...) = 12 رقم إجمالي
                
                if not name:
                    st.error("يرجى إدخال الاسم.")
                elif "@" not in email or "." not in email:
                    st.error("يرجى إدخال بريد إلكتروني صحيح.")
                elif not phone_input.startswith("966"):
                    st.error("يجب أن يبدأ رقم الجوال بـ 966")
                elif len(phone_input) < 12:
                    st.error(f"رقم الجوال ناقص! لقد أدخلت {len(phone_input)} أرقام فقط، والمطلوب 12 رقم (966 متبوعة بـ 9 أرقام)")
                elif len(phone_input) > 12:
                    st.error(f"رقم الجوال طويل جداً! لقد أدخلت {len(phone_input)} أرقام.")
                else:
                    # إذا اجتازت البيانات كل الفحوصات
                    add_observer({
                        "name": name, 
                        "email": email, 
                        "status": status, 
                        "phone": phone_input, 
                        "work": work, 
                        "region": region, 
                        "city": city
                    })
                    st.success(f"تمت إضافة {name} بنجاح!")
                    st.balloons()
