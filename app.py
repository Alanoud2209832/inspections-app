import streamlit as st
from database import init_db, add_campaign, get_campaigns, get_observers, add_observer, get_observers_by_region
import pandas as pd

st.set_page_config(page_title="نظام الرقابة الذكي", layout="wide", page_icon="🛡️")

# تهيئة قاعدة البيانات
init_db()

# القائمة الجانبية
st.sidebar.title("🛠️ القائمة الرئيسية")
menu = ["📊 الإحصائيات", "➕ إضافة حملة جديدة", "📋 سجل الحملات", "👥 دليل المراقبين"]
choice = st.sidebar.radio("انتقل إلى:", menu)

# --- صفحة الإحصائيات ---
if choice == "📊 الإحصائيات":
    st.title("📈 لوحة مؤشرات النظام")
    df_c = get_campaigns()
    df_o = get_observers()
    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي الحملات", len(df_c))
    col2.metric("عدد المراقبين", len(df_o))
    col3.metric("حالة القاعدة", "Neon Online ✅")
    st.divider()
    st.subheader("أحدث النشاطات الميدانية")
    st.dataframe(df_c.head(10), use_container_width=True)

# --- صفحة إضافة حملة جديدة ---
# --- جزء إضافة حملة جديدة المطور في app.py ---
elif choice == "➕ إضافة حملة جديدة":
    st.title("📝 إدخال بيانات حملة ميدانية")
    
    # 1. اختيار المنطقة (خارج الفورم لضمان التحديث الفوري للأسماء)
    region = st.selectbox("المنطقة", ["الرياض", "مكة المكرمة", "المدينة المنورة", "الشرقية", "عسير", "تبوك", "القصيم", "الباحة", "الجوف"])
    
    # جلب المراقبين المفلترين بناءً على المنطقة المختارة
    from database import get_observers_by_region
    filtered_names = get_observers_by_region(region)
    
    if not filtered_names:
        st.warning(f"⚠️ لا يوجد مراقبين مسجلين في منطقة {region}. يرجى إضافتهم من دليل المراقبين أولاً.")

    # 2. بداية النموذج لإدخال بقية البيانات
    with st.form("main_campaign_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            selected_date = st.date_input("اختر التاريخ")
            days_ar = {"Saturday": "السبت", "Sunday": "الأحد", "Monday": "الاثنين", "Tuesday": "الثلاثاء", "Wednesday": "الأربعاء", "Thursday": "الخميس", "Friday": "الجمعة"}
            day_name_ar = days_ar.get(selected_date.strftime("%A"), selected_date.strftime("%A"))
            full_date_str = f"{day_name_ar} {selected_date.strftime('%Y-%m-%d')}"
            
            city = st.text_input("المدينة")
            group_name = st.text_input("اسم التجمع")
            
        with col2:
            # قائد الفريق
            leader = st.selectbox("قائد الفريق", options=filtered_names if filtered_names else ["لا يوجد مراقبين"])
            
            # المشاركين (Multi-select)
            participants = st.multiselect("تحديد المراقبين المشاركين", options=filtered_names)
            
            survey_count = st.number_input("عدد المنشآت", min_value=0, step=1)
            inspectors = st.text_area("مأموري الضبط من جهات أخرى")
            map_link = st.text_input("رابط الخرائط")
        
        submit_button = st.form_submit_button("حفظ الحملة الميدانية 💾")
        
        if submit_button:
            if group_name and filtered_names and leader != "لا يوجد مراقبين":
                participants_str = ", ".join(participants) if participants else "لا يوجد"
                
                campaign_data = {
                    "day_date": str(full_date_str),
                    "region": str(region), # نأخذ المنطقة المختارة من الأعلى
                    "city": str(city),
                    "group_name": str(group_name),
                    "leader": str(leader),
                    "participants": participants_str,
                    "survey_count": int(survey_count),
                    "inspectors": str(inspectors),
                    "map_link": str(map_link)
                }
                
                try:
                    add_campaign(campaign_data)
                    st.success(f"✅ تم حفظ حملة {group_name} بنجاح!")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ فشل الحفظ: {e}")
            else:
                st.error("⚠️ يرجى إدخال اسم التجمع والتأكد من وجود مراقبين في المنطقة.")

# --- صفحة سجل الحملات ---
elif choice == "📋 سجل الحملات":
    st.title("🗂️ سجل الجولات الميدانية")
    df = get_campaigns()
    st.dataframe(df, use_container_width=True)

# --- صفحة دليل المراقبين ---
elif choice == "👥 دليل المراقبين":
    st.title("👨‍✈️ إدارة دليل المراقبين")
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
                email = st.text_input("الايميل")
                phone_input = st.text_input("رقم الجوال", value="966")
                status = st.selectbox("حالة المراقب", ["على راس العمل", "مجاز", "متقاعد"])
            with col2:
                work = st.selectbox("جهة العمل", ["هيئة الزكاة والضريبة والجمارك", "وزارة التجارة", "وزارة البيئة والمياه والزراعة", "وزارة الموارد البشرية"])
                region_obs = st.selectbox("المنطقة ", ["الرياض", "مكة المكرمة", "المدينة المنورة", "الشرقية", "عسير", "تبوك", "القصيم"])
                city_obs = st.text_input("المدينة")
            
            if st.form_submit_button("حفظ المراقب 💾"):
                if len(name) > 3 and "@" in email and len(phone_input) == 12 and name.lower() != "test":
                    add_observer({"name": name, "email": email, "status": status, "phone": phone_input, "work": work, "region": region_obs, "city": city_obs})
                    st.success(f"✅ تمت إضافة المراقب {name} بنجاح")
                    st.rerun()
                else:
                    st.error("❌ يرجى التحقق من صحة البيانات (الاسم حقيقي، الإيميل صحيح، الجوال 12 رقم)")
