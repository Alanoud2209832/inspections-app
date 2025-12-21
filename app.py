import streamlit as st
import pandas as pd

# إعدادات الصفحة
st.set_page_config(page_title="نظام الرقابة الذكي", layout="wide")

# --- روابط Google Sheets ---
# انسخي الروابط الكاملة من المتصفح وضعيها هنا
URL_OBSERVERS = "https://docs.google.com/spreadsheets/d/1k-bUZ2OMPEUihzsP2g18GJFpbh7ja3Qc/edit?usp=sharing&ouid=109392900872958236563&rtpof=true&sd=true"
URL_CAMPAIGNS = "https://docs.google.com/spreadsheets/d/1l0G8LReiliMcdl6Dpeyg2NTsVK6sG711/edit?usp=sharing&ouid=109392900872958236563&rtpof=true&sd=true"

def get_csv_url(url):
    """دالة لتحويل رابط جوجل شيت العادي إلى رابط تحميل مباشر CSV"""
    if "edit" in url:
        return url.replace('/edit', '/export?format=csv') + "&gid=" + url.split('gid=')[-1]
    return url

@st.cache_data(ttl=60) # تحديث البيانات كل 60 ثانية إذا تغيرت في جوجل شيت
def load_data():
    try:
        obs_df = pd.read_csv(get_csv_url(URL_OBSERVERS))
        camp_df = pd.read_csv(get_csv_url(URL_CAMPAIGNS))
        return obs_df, camp_df
    except Exception as e:
        st.error(f"حدث خطأ أثناء جلب البيانات من Google Sheets: {e}")
        return None, None

# تحميل البيانات
observers, campaigns = load_data()

# واجهة التطبيق
if observers is not None and campaigns is not None:
    st.title("🚀 نظام تنظيم الحملات الرقابية")
    
    # القائمة الجانبية
    menu = ["لوحة التحكم", "تخطيط حملة جديدة", "دليل المراقبين"]
    choice = st.sidebar.selectbox("القائمة", menu)

    if choice == "لوحة التحكم":
        st.subheader("📊 ملخص الحملات الحالية")
        st.dataframe(campaigns, use_container_width=True)
        
    elif choice == "تخطيط حملة جديدة":
        st.subheader("📅 جدولة حملة إلكترونية")
        # هنا نستخدم بيانات "المدينة" و "المنطقة" من الشيت لعمل القوائم المنسدلة
        region = st.selectbox("اختر المنطقة", campaigns['المنطقة'].unique())
        st.info(f"سيتم تصفية المراقبين المتاحين في {region}")
        
    elif choice == "دليل المراقبين":
        st.subheader("👥 بيانات المراقبين المسجلة في Google Sheets")
        st.write("أحدث البيانات المحدثة:")
        st.dataframe(observers, use_container_width=True)

else:
    st.info("بانتظار ربط روابط Google Sheets الصحيحة في الكود.")
