import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام الرقابة الذكي", layout="wide", page_icon="🚀")

# 2. إنشاء الاتصال (يعتمد على [connections.gsheets] في Secrets)
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. روابط الملفات (روابط العرض العادية)
URL_OBSERVERS = "https://docs.google.com/spreadsheets/d/1xpp9MmUSjBg4EgGXeRIGwQghtMxAYuW2lFL8YSRZJRg/edit?usp=sharing"
URL_CAMPAIGNS = "https://docs.google.com/spreadsheets/d/1aApLVf9PPIcClcelziEzUqwWXFrc8a4pZgfqesQoQBw/edit?usp=sharing"

# 4. وظائف جلب البيانات
@st.cache_data(ttl=5) # تحديث سريع جداً لضمان رؤية النتائج
def get_data(url):
    return conn.read(spreadsheet=url)

# 5. القائمة الجانبية
st.sidebar.title("🛠️ لوحة التحكم")
menu = ["📊 الإحصائيات", "➕ إنشاء حملة جديدة", "📅 سجل الحملات", "👥 دليل المراقبين"]
choice = st.sidebar.radio("التوجه إلى:", menu)

# --- محتوى الصفحات ---

if choice == "📊 الإحصائيات":
    st.title("📈 ملخص العمليات الرقابية")
    try:
        obs_df = get_data(URL_OBSERVERS)
        camp_df = get_data(URL_CAMPAIGNS)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("إجمالي المراقبين", len(obs_df))
        c2.metric("إجمالي الحملات", len(camp_df))
        c3.metric("حالة النظام", "متصل بجوجل ✅")
        
        st.divider()
        st.subheader("أحدث الحملات المضافة")
        st.dataframe(camp_df.tail(5), use_container_width=True)
    except Exception as e:
        st.error(f"خطأ في جلب البيانات: {e}")

elif choice == "➕ إنشاء حملة جديدة":
    st.title("📝 جدولة حملة تفتيشية")
    st.info("قم بتعبئة النموذج التالي ليتم حفظه تلقائياً في Google Sheets.")

    with st.form("campaign_entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("اسم الحملة المستهدفة")
            date = st.date_input("تاريخ الانطلاق", datetime.now())
            loc = st.text_input("الموقع (المدينة/الحي)")
        with col2:
            time = st.time_input("الوقت")
            parts = st.multiselect("الجهات المشاركة", ["وزارة التجارة", "الأمانة", "الشرطة", "الموارد البشرية"])
            scope = st.selectbox("النطاق الجغرافي", ["نطاق محدد", "مدينة كاملة", "منطقة"])
            
        goals = st.text_area("الأهداف والتوثيق الرقابي")
        
        submitted = st.form_submit_button("حفظ وإرسال البيانات 💾")
        
        if submitted:
            if name and goals:
                try:
                    # جلب البيانات الحالية بدون كاش للتأكد من المزامنة
                    current_df = conn.read(spreadsheet=URL_CAMPAIGNS, ttl=0)
                    
                    # إنشاء السطر الجديد
                    new_entry = pd.DataFrame([{
                        "اسم التجمع": name,
                        "التاريخ": str(date),
                        "الوقت": str(time),
                        "الموقع": loc,
                        "الجهات المشاركة": ", ".join(parts),
                        "النطاق": scope,
                        "الأهداف": goals
                    }])
                    
                    # دمج البيانات
                    updated_df = pd.concat([current_df, new_entry], ignore_index=True)
                    
                    # الحفظ الفعلي في Google Sheets
                    # ملاحظة: تأكدي أن اسم الورقة في جوجل هو Sheet1
                    conn.update(spreadsheet=URL_CAMPAIGNS, data=updated_df, worksheet="Sheet1")
                    
                    st.success(f"✅ تم حفظ حملة ({name}) بنجاح!")
                    st.balloons()
                    st.cache_data.clear()
                except Exception as e:
                    st.error(f"حدث خطأ أثناء الاتصال: {e}")
                    st.info("تأكد من أن إيميل الخدمة مضاف كـ Editor في ملف جوجل شيت.")
            else:
                st.warning("⚠️ يرجى تعبئة الحقول الأساسية (الاسم والأهداف).")

elif choice == "📅 سجل الحملات":
    st.title("📋 سجل جميع الحملات")
    try:
        df = get_data(URL_CAMPAIGNS)
        st.dataframe(df, use_container_width=True)
    except:
        st.error("فشل تحميل سجل الحملات.")

elif choice == "👥 دليل المراقبين":
    st.title("👨‍✈️ قاعدة بيانات المراقبين")
    try:
        df = get_data(URL_OBSERVERS)
        st.dataframe(df, use_container_width=True)
    except:
        st.error("فشل تحميل بيانات المراقبين.")
