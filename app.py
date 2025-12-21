import streamlit as st
import pandas as pd

# إعدادات الصفحة
st.set_page_config(page_title="نظام الرقابة الذكي", layout="wide")

# --- الروابط المباشرة المستخرجة من روابطك ---

# ملف المراقبين (Observers)
# تم استخراج ID و GID من الرابط الأول
URL_OBSERVERS = "https://docs.google.com/spreadsheets/d/1xpp9MmUSjBg4EgGXeRIGwQghtMxAYuW2lFL8YSRZJRg/export?format=csv&gid=1189139415"

# ملف الحملات (Campaigns)
# تم استخراج ID و GID من الرابط الثاني
URL_CAMPAIGNS = "https://docs.google.com/spreadsheets/d/1aApLVf9PPIcClcelziEzUqwWXFrc8a4pZgfqesQoQBw/export?format=csv&gid=1064973789"

@st.cache_data(ttl=60)
def load_data():
    try:
        # قراءة البيانات مباشرة من روابط التصدير
        obs_df = pd.read_csv(URL_OBSERVERS)
        camp_df = pd.read_csv(URL_CAMPAIGNS)
        return obs_df, camp_df
    except Exception as e:
        st.error(f"خطأ في الاتصال بجداول جوجل: {e}")
        return None, None

# تحميل البيانات
observers, campaigns = load_data()

# عرض الواجهة في حال نجاح الاتصال
if observers is not None and campaigns is not None:
    st.success("تم الربط بنجاح مع Google Sheets ✅")
    
    # القائمة الجانبية للتنقل
    st.sidebar.title("القائمة الرئيسية")
    page = st.sidebar.radio("انتقل إلى:", ["لوحة التحكم", "بيانات المراقبين", "بيانات الحملات"])

    if page == "لوحة التحكم":
        st.title("📊 ملخص النظام")
        col1, col2 = st.columns(2)
        col1.metric("عدد المراقبين المسجلين", len(observers))
        col2.metric("عدد الحملات المخططة", len(campaigns))
        
        st.divider()
        st.subheader("آخر التحديثات من الجداول")
        st.write("بيانات الحملات الأخيرة:")
        st.table(campaigns.head(3))

    elif page == "بيانات المراقبين":
        st.title("👥 دليل المراقبين")
        st.dataframe(observers, use_container_width=True)

    elif page == "بيانات الحملات":
        st.title("📅 تفاصيل الحملات")
        st.dataframe(campaigns, use_container_width=True)

else:
    st.warning("تأكدي من تفعيل خيار 'Anyone with the link can view' في ملفات Google Sheets.")
