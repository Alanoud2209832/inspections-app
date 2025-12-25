import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="نظام الرقابة الذكي", layout="wide")

# إنشاء الاتصال بجداول بيانات جوجل باستخدام Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# روابط الملفات
URL_OBSERVERS = "https://docs.google.com/spreadsheets/d/1xpp9MmUSjBg4EgGXeRIGwQghtMxAYuW2lFL8YSRZJRg/edit?usp=sharing"
URL_CAMPAIGNS = "https://docs.google.com/spreadsheets/d/1aApLVf9PPIcClcelziEzUqwWXFrc8a4pZgfqesQoQBw/edit?usp=sharing"

# تنظيف الكاش وتحديث البيانات
st.sidebar.button("تحديث البيانات 🔄", on_click=lambda: st.cache_data.clear())

# القائمة الجانبية
menu = ["لوحة التحكم", "إنشاء حملة (الفورم)", "سجل الحملات"]
choice = st.sidebar.radio("القائمة الرئيسية", menu)

if choice == "لوحة التحكم":
    st.title("📊 نظام الرقابة - لوحة التحكم")
    st.info("استخدم القائمة الجانبية للتنقل بين إدخال البيانات وعرض السجلات.")

elif choice == "إنشاء حملة (الفورم)":
    st.title("➕ جدولة حملة رقابية جديدة")
    
    # جلب بيانات المراقبين لعرضها في الاختيارات
    observers_df = conn.read(spreadsheet=URL_OBSERVERS)
    
    with st.form("campaign_form"):
        col1, col2 = st.columns(2)
        with col1:
            camp_name = st.text_input("اسم الحملة")
            camp_date = st.date_input("تاريخ الحملة")
            location = st.text_input("الموقع الجغرافي")
        with col2:
            participants = st.multiselect("الجهات المشاركة", ["وزارة التجارة", "البلدية", "الشرطة", "الموارد البشرية"])
            scope = st.selectbox("النطاق الجغرافي", ["حي محدد", "منطقة كاملة", "بلدية فرعية"])
        
        objectives = st.text_area("الأهداف الرقابية المستهدفة")
        
        submit = st.form_submit_button("حفظ الحملة في Google Sheets")
        
        if submit:
            if camp_name and objectives:
                # قراءة البيانات الحالية لإضافة السطر الجديد
                existing_data = conn.read(spreadsheet=URL_CAMPAIGNS)
                
                new_row = pd.DataFrame([{
                    "اسم التجمع": camp_name,
                    "التاريخ": str(camp_date),
                    "الموقع": location,
                    "الجهات المشاركة": ", ".join(participants),
                    "النطاق": scope,
                    "الأهداف": objectives
                }])
                
                updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                
                # حفظ البيانات فعلياً في الجدول
                conn.update(spreadsheet=URL_CAMPAIGNS, data=updated_df)
                st.success("✅ تم حفظ البيانات بنجاح في الجدول!")
                st.balloons()
            else:
                st.error("يرجى ملء الحقول الأساسية.")

elif choice == "سجل الحملات":
    st.title("📅 سجل الحملات المجدولة")
    data = conn.read(spreadsheet=URL_CAMPAIGNS)
    st.dataframe(data, use_container_width=True)

elif choice == "دليل المراقبين":
    st.title("👥 بيانات المراقبين والجهات")
    if observers is not None:
        # إضافة خاصية البحث
        search = st.text_input("بحث عن مراقب...")
        if search:
            filtered_df = observers[observers.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.dataframe(observers, use_container_width=True)
            import streamlit as st
import pandas as pd
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(page_title="نظام الرقابة الذكي", layout="wide")

# الروابط (تأكدي أن الملفات "Anyone with the link can view")
URL_CAMPAIGNS = "https://docs.google.com/spreadsheets/d/1aApLVf9PPIcClcelziEzUqwWXFrc8a4pZgfqesQoQBw/export?format=csv&gid=1064973789"

# 1. مكان الفورم (الاستمارة)
def show_form():
    st.title("➕ إنشاء حملة رقابية جديدة")
    
    # بداية الفورم
    with st.form("new_campaign_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            camp_name = st.text_input("اسم الحملة")
            camp_date = st.date_input("تاريخ الحملة", datetime.now())
            participants = st.multiselect("الجهات المشاركة", ["وزارة التجارة", "البلدية", "الشرطة", "الموارد البشرية"])
        
        with col2:
            location = st.text_input("الموقع الجغرافي (الحي/المدينة)")
            scope = st.selectbox("نطاق الحملة", ["نطاق ضيق", "بلدية فرعية", "منطقة كاملة"])
            camp_time = st.time_input("وقت الانطلاق")

        objectives = st.text_area("الأهداف الرقابية المستهدفة")
        
        # زر الحفظ
        submit_button = st.form_submit_button("حفظ الحملة في قاعدة البيانات")
        
        if submit_button:
            if camp_name and objectives:
                # تجهيز البيانات الجديدة كسطر واحد
                new_data = {
                    "اسم التجمع": camp_name,
                    "التاريخ": str(camp_date),
                    "الموقع": location,
                    "الجهات المشاركة": ", ".join(participants),
                    "الأهداف": objectives
                }
                
                # إظهار رسالة نجاح (مؤقتة حتى يتم تفعيل الـ API الفعلي للكتابة)
                st.success(f"✅ تم إرسال بيانات حملة ({camp_name}) بنجاح!")
                st.balloons()
                
                # عرض البيانات التي تم حفظها
                st.info("سيتم تسجيل السطر التالي في Google Sheets:")
                st.write(new_data)
            else:
                st.warning("يرجى ملء اسم الحملة والأهداف قبل الحفظ.")

# 2. القائمة الجانبية للتنقل
menu = ["لوحة التحكم", "إنشاء حملة (الفورم)", "سجل الحملات"]
choice = st.sidebar.radio("انتقل إلى:", menu)

if choice == "لوحة التحكم":
    st.title("📊 لوحة المؤشرات")
    st.write("مرحباً بك في نظام الرقابة. اختر 'إنشاء حملة' من القائمة الجانبية للبدء.")

elif choice == "إنشاء حملة (الفورم)":
    show_form() # استدعاء الفورم هنا

elif choice == "سجل الحملات":
    st.title("📅 سجل الحملات")
    df = pd.read_csv(URL_CAMPAIGNS)
    st.dataframe(df)
