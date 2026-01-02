import streamlit as st
from database import init_db, add_campaign, get_campaigns, get_observers, add_observer
import pandas as pd

st.set_page_config(page_title="نظام الرقابة الذكي", layout="wide", page_icon="🛡️")
init_db()

# القائمة الجانبية
st.sidebar.title("🛠️ القائمة الرئيسية")
menu = ["📊 الإحصائيات", "➕ إضافة حملة جديدة", "📋 سجل الحملات", "👥 دليل المراقبين"]
choice = st.sidebar.radio("انتقل إلى:", menu)

# --- صفحة دليل المراقبين ---
if choice == "👥 دليل المراقبين":
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
                region = st.selectbox("المنطقة ", ["الرياض", "مكة المكرمة", "المدينة المنورة", "الشرقية", "عسير", "تبوك", "القصيم"])
                city = st.text_input("المدينة")
            
            if st.form_submit_button("حفظ المراقب 💾"):
                # --- الفلاتر والشروط (المنطق الذي يمنع كلمة test) ---
                
                # 1. فحص الاسم
                if len(name) < 3 or name.lower() == "test":
                    st.error("❌ يرجى إدخال اسم حقيقي وليس 'test'.")
                
                # 2. فحص الإيميل
                elif "@" not in email or "." not in email:
                    st.error("❌ صيغة الإيميل غير صحيحة (يجب أن يحتوي على @ ونقطة).")
                
                # 3. فحص الجوال (بداية بـ 966 وطول 12 رقم)
                elif not phone_input.startswith("966") or len(phone_input) != 12:
                    st.error("❌ رقم الجوال يجب أن يبدأ بـ 966 ويتكون من 12 رقماً إجمالاً.")
                
                # 4. فحص المدينة
                elif city.lower() == "test" or len(city) < 2:
                    st.error("❌ يرجى إدخال اسم مدينة صحيح.")
                
                else:
                    # إذا نجحت كل الشروط يتم الحفظ
                    add_observer({
                        "name": name, 
                        "email": email, 
                        "status": status, 
                        "phone": phone_input, 
                        "work": work, 
                        "region": region, 
                        "city": city
                    })
                    st.success(f"✅ تمت إضافة {name} بنجاح!")
                    st.balloons()
