import streamlit as st
from database import init_db, add_campaign, get_campaigns, get_observers, add_observer, get_observers_names
import pandas as pd

st.set_page_config(page_title="نظام الرقابة الذكي", layout="wide", page_icon="🛡️")
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
    st.subheader("أحدث النشاطات")
    st.dataframe(df_c.head(5), use_container_width=True)

# --- صفحة إضافة حملة جديدة ---
elif choice == "➕ إضافة حملة جديدة":
    st.title("📝 إدخال بيانات حملة ميدانية")
    
    # جلب الأسماء من ملف database
    from database import get_observers_names
    names_list = get_observers_names()
    
    with st.form("add_campaign_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            day_date = st.text_input("اليوم والتاريخ")
            region = st.selectbox("المنطقة", ["الرياض", "مكة المكرمة", "المدينة المنورة", "الشرقية", "عسير", "تبوك", "القصيم"])
            city = st.text_input("المدينة")
            group_name = st.text_input("اسم التجمع")
        with col2:
            # هنا يظهر حقل قائد الفريق
            leader = st.selectbox("قائد الفريق (من المراقبين المسجلين)", options=names_list if names_list else ["لا يوجد مراقبين مسجلين"])
            survey_count = st.number_input("عدد المنشآت", min_value=0, step=1)
            inspectors = st.text_area("مأموري الضبط المشاركين")
            map_link = st.text_input("رابط الخرائط")
        
        if st.form_submit_button("حفظ الحملة 💾"):
            if group_name and (names_list and leader != "لا يوجد مراقبين مسجلين"):
                add_campaign({
                    "day_date": day_date, "region": region, "city": city,
                    "group_name": group_name, "leader": leader,
                    "survey_count": survey_count, "inspectors": inspectors, "map_link": map_link
                })
                st.success(f"✅ تم حفظ حملة {group_name} بقيادة {leader}")
                st.balloons()
            else:
                st.error("⚠️ يرجى إدخال اسم التجمع والتأكد من وجود مراقبين مسجلين في النظام.")

# --- صفحة سجل الحملات ---
elif choice == "📋 سجل الحملات":
    st.title("🗂️ سجل الجولات الميدانية")
    df = get_campaigns()
    st.dataframe(df, use_container_width=True)

# --- صفحة دليل المراقبين ---
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
                email = st.text_input("الايميل", placeholder="example@domain.com")
                phone_input = st.text_input("رقم الجوال", value="966")
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
                if len(name) < 3 or name.lower() == "test":
                    st.error("❌ يرجى إدخال اسم حقيقي.")
                elif "@" not in email or "." not in email:
                    st.error("❌ صيغة الإيميل غير صحيحة.")
                elif not phone_input.startswith("966") or len(phone_input) != 12:
                    st.error("❌ رقم الجوال يجب أن يبدأ بـ 966 ويتكون من 12 رقماً.")
                elif city.lower() == "test":
                    st.error("❌ يرجى إدخال اسم مدينة صحيح.")
                else:
                    add_observer({
                        "name": name, "email": email, "status": status, 
                        "phone": phone_input, "work": work, "region": region, "city": city
                    })
                    st.success(f"✅ تمت إضافة {name} بنجاح!")
                    st.balloons()
