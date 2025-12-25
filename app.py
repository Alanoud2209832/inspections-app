import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام الرقابة الذكي", layout="wide", page_icon="🚀")

# 2. إنشاء الاتصال بجداول جوجل
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. روابط الملفات
URL_OBSERVERS = "https://docs.google.com/spreadsheets/d/1xpp9MmUSjBg4EgGXeRIGwQghtMxAYuW2lFL8YSRZJRg/edit?usp=sharing"
URL_CAMPAIGNS = "https://docs.google.com/spreadsheets/d/1aApLVf9PPIcClcelziEzUqwWXFrc8a4pZgfqesQoQBw/edit?usp=sharing"

# 4. وظيفة جلب البيانات
def get_data(url):
    return conn.read(spreadsheet=url, ttl=0)

# 5. القائمة الجانبية
st.sidebar.title("🛠️ لوحة التحكم")
menu = ["📊 الإحصائيات", "➕ إنشاء حملة جديدة", "📅 سجل الحملات", "👥 دليل المراقبين"]
choice = st.sidebar.radio("التوجه إلى:", menu)

# --- محتوى الصفحات ---

if choice == "📊 الإحصائيات":
    st.title("📈 ملخص العمليات الرقابية")
    try:
        camp_df = get_data(URL_CAMPAIGNS)
        obs_df = get_data(URL_OBSERVERS)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("إجمالي الحملات", len(camp_df))
        c2.metric("عدد المراقبين", len(obs_df))
        c3.metric("حالة النظام", "متصل ✅")
        
        st.divider()
        st.subheader("أحدث البيانات المضافة")
        st.dataframe(camp_df.tail(5), use_container_width=True)
    except Exception as e:
        st.error(f"خطأ في جلب البيانات: {e}")

elif choice == "➕ إنشاء حملة جديدة":
    st.title("📝 إدخال بيانات حملة جديدة")
    
    with st.form("campaign_entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            day_date = st.text_input("اليوم والتاريخ", placeholder="مثال: الخميس 25-12-2025")
            region = st.selectbox("المنطقة", ["الرياض", "مكة المكرمة", "الشرقية", "عسير", "تبوك", "المدينة المنورة", "القصيم", "جازان", "نجران", "الباحة", "حائل", "الجوف", "الحدود الشمالية"])
            city = st.text_input("المدينة")
            group_name = st.text_input("اسم التجمع")
            
        with col2:
            survey_count = st.number_input("عدد المنشآت بناءً على المسح الميداني", min_value=0, step=1)
            inspectors = st.text_area("مأموري الضبط من وزارة التجارة")
            map_link = st.text_input("موقع التجمع على الخرائط (رابط Google Maps)")
            
        submitted = st.form_submit_button("حفظ البيانات في الجدول 💾")
        
        if submitted:
            if group_name and day_date:
                try:
                    # جلب البيانات الحالية
                    current_df = conn.read(spreadsheet=URL_CAMPAIGNS, ttl=0)
                    
                    # حساب الرقم التسلسلي الجديد (م)
                    if not current_df.empty:
                        # تحويل العمود "م" لرقم وأخذ أكبر قيمة وإضافة 1
                        next_id = pd.to_numeric(current_df['م'], errors='coerce').max() + 1
                        if pd.isna(next_id): next_id = 1
                    else:
                        next_id = 1

                    # إنشاء السطر الجديد بنفس ترتيب مسميات ملفك بالضبط
                    new_entry = pd.DataFrame([{
                        "م": int(next_id),
                        "اليوم والتاريخ": day_date,
                        "المنطقة": region,
                        "المدينة": city,
                        "اسم التجمع": group_name,
                        "عدد المنشآت بناءً على المسح الميداني": survey_count,
                        "مأموري الضبط من وزارة التجارة": inspectors,
                        "موقع التجمع على الخرائط": map_link
                    }])
                    
                    # دمج البيانات
                    updated_df = pd.concat([current_df, new_entry], ignore_index=True).fillna("")
                    
                    # الحفظ الفعلي
                    conn.update(spreadsheet=URL_CAMPAIGNS, data=updated_df)
                    
                    st.success(f"✅ تم حفظ بيانات التجمع رقم ({next_id}) بنجاح!")
                    st.balloons()
                except Exception as e:
                    st.error("⚠️ حدث خطأ أثناء الحفظ. تأكدي من تطابق مسميات الأعمدة.")
                    st.expander("تفاصيل تقنية للمطور").write(e)
            else:
                st.warning("⚠️ يرجى تعبئة الحقول الأساسية.")

elif choice == "📅 سجل الحملات":
    st.title("📋 سجل جميع الحملات الميدانية")
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
