import streamlit as st
import pandas as pd
import plotly.express as px

# إعدادات الصفحة
st.set_page_config(page_title="نظام الحملات الرقابية", layout="wide")

# دالة لتحميل البيانات (مع التخزين المؤقت للسرعة)
@st.cache_data
def load_data():
    # تأكدي أن أسماء الملفات تطابق المرفوعة في GitHub تماماً
    observers_df = pd.read_excel("observers.xlsx")
    campaigns_df = pd.read_excel("campaigns.xlsx")
    return observers_df, campaigns_df

try:
    observers, campaigns = load_data()

    # القائمة الجانبية
    st.sidebar.title("القائمة الرئيسية")
    page = st.sidebar.radio("انتقل إلى:", ["لوحة التحكم", "تخطيط حملة جديدة", "بيانات المراقبين"])

    if page == "لوحة التحكم":
        st.title("📊 مؤشرات الحملات الرقابية")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("إجمالي الحملات", len(campaigns))
        col2.metric("عدد المراقبين", len(observers))
        col3.metric("المناطق المغطاة", campaigns['المنطقة'].nunique())

        st.divider()
        st.subheader("توزيع الحملات حسب المناطق")
        fig = px.bar(campaigns, x='المنطقة', title="عدد الحملات في كل منطقة")
        st.plotly_chart(fig, use_container_width=True)

    elif page == "تخطيط حملة جديدة":
        st.title("➕ إنشاء وتخطيط حملة إلكترونية")
        
        with st.form("campaign_form"):
            st.subheader("البيانات الأساسية")
            c1, c2 = st.columns(2)
            with c1:
                camp_name = st.text_input("اسم التجمع / الحملة")
                region = st.selectbox("المنطقة", campaigns['المنطقة'].unique())
            with c2:
                city = st.selectbox("المدينة", campaigns[campaigns['المنطقة'] == region]['المدينة'].unique())
                date = st.date_input("تاريخ الحملة")

            st.divider()
            st.subheader("اختيار فريق العمل")
            # فلترة المراقبين بناءً على المدينة المختارة للحملة
            local_observers = observers[(observers['المدينة'] == city) & (observers['حالة المراقب'] == 'نشط')]
            
            selected_leader = st.selectbox("تحديد قائد الحملة", local_observers['الاسم'].unique())
            selected_team = st.multiselect("تحديد المراقبين المشاركين", local_observers['الاسم'].unique())
            
            submitted = st.form_submit_button("حفظ وتوثيق الحملة")
            if submitted:
                st.success(f"تم جدولة حملة '{camp_name}' بنجاح بقيادة {selected_leader}")

    elif page == "بيانات المراقبين":
        st.title("👥 قاعدة بيانات المراقبين")
        search = st.text_input("بحث بالاسم أو جهة العمل")
        filtered_obs = observers[observers['الاسم'].str.contains(search) | observers['جهة العمل'].str.contains(search)]
        st.dataframe(filtered_obs, use_container_width=True)

except Exception as e:
    st.error(f"حدث خطأ في تحميل الملفات. تأكدي من رفع ملفات الإكسل بشكل صحيح. الخطأ: {e}")
