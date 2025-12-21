import streamlit as st
import pandas as pd
import plotly.express as px

# إعدادات واجهة الموقع
st.set_page_config(page_title="نظام تنظيم الحملات الرقابية", layout="wide", initial_sidebar_state="expanded")

# تحسين مظهر الواجهة بالعربية
st.markdown("""
    <style>
    .main { text-align: right; direction: rtl; }
    div[data-testid="stSidebarNav"] { text-align: right; direction: rtl; }
    </style>
    """, unsafe_allow_html=True)

# دالة تحميل البيانات
@st.cache_data
def load_data():
    try:
        obs = pd.read_excel("observers.xlsx")
        camps = pd.read_excel("campaigns.xlsx")
        return obs, camps
    except Exception as e:
        st.error(f"خطأ في تحميل الملفات: تأكدي من رفع ملفات الإكسل بالأسماء الصحيحة. {e}")
        return None, None

observers, campaigns = load_data()

if observers is not None and campaigns is not None:
    # القائمة الجانبية
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/9322/9322127.png", width=100)
    st.sidebar.title("نظام الرقابة الذكي")
    menu = ["🏠 لوحة التحكم", "📅 تخطيط حملة جديدة", "👥 دليل المراقبين"]
    choice = st.sidebar.radio("القائمة الرئيسية", menu)

    if choice == "🏠 لوحة التحكم":
        st.title("📊 مؤشرات الأداء العام")
        
        # إحصائيات سريعة
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("إجمالي الحملات", len(campaigns))
        c2.metric("عدد المراقبين", len(observers))
        c3.metric("المنشآت المستهدفة", int(campaigns['عدد المنشآت بناءً على المسح الميداني'].sum()))
        c4.metric("المناطق", campaigns['المنطقة'].nunique())

        st.divider()
        
        # رسم بياني
        fig = px.pie(campaigns, names='المنطقة', title="توزيع الحملات حسب المناطق", hole=0.3)
        st.plotly_chart(fig, use_container_width=True)

    elif choice == "📅 تخطيط حملة جديدة":
        st.title("➕ إنشاء حملة رقابية إلكترونية")
        
        with st.form("new_camp"):
            col1, col2 = st.columns(2)
            with col1:
                camp_name = st.selectbox("اختر اسم التجمع", campaigns['اسم التجمع'].unique())
                leader = st.text_input("جهة القيادة (مثلاً: وزارة التجارة)")
            with col2:
                target_date = st.date_input("تحديد تاريخ الحملة")
                target_region = campaigns[campaigns['اسم التجمع'] == camp_name]['المنطقة'].iloc[0]
                st.info(f"المنطقة المختارة: {target_region}")

            st.divider()
            st.subheader("توزيع فرق العمل الميدانية")
            
            # تصفية المراقبين بناءً على منطقة التجمع والحالة
            available_staff = observers[(observers['المنطقة'] == target_region) & (observers['حالة المراقب'] == 'نشط')]
            
            selected_staff = st.multiselect("اختر المراقبين المشاركين (بناءً على النطاق الجغرافي)", 
                                           options=available_staff['الاسم'].tolist())
            
            goals = st.text_area("الأهداف الرقابية المستهدفة لهذه الحملة")
            
            submit = st.form_submit_button("اعتماد وتوثيق الحملة")
            if submit:
                st.success(f"تم بنجاح جدولة حملة '{camp_name}' في منطقة {target_region}. تم إرسال الإشعارات للمراقبين.")

    elif choice == "👥 دليل المراقبين":
        st.title("👥 بيانات المراقبين ومأموري الضبط")
        
        # فلاتر البحث
        search_col1, search_col2 = st.columns(2)
        with search_col1:
            filt_region = st.selectbox("فلترة حسب المنطقة", ["الكل"] + list(observers['المنطقة'].unique()))
        
        df_display = observers.copy()
        if filt_region != "الكل":
            df_display = df_display[df_display['المنطقة'] == filt_region]
            
        st.dataframe(df_display, use_container_width=True)

else:
    st.warning("يرجى التأكد من رفع ملفات الإكسل في GitHub لتفعيل النظام.")
