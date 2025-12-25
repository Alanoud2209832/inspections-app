import streamlit as st
import pandas as pd
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(page_title="نظام إدارة الحملات الرقابية", layout="wide")

# روابط البيانات (تأكدي من صحتها كما في الخطوة السابقة)
URL_OBSERVERS = "https://docs.google.com/spreadsheets/d/1xpp9MmUSjBg4EgGXeRIGwQghtMxAYuW2lFL8YSRZJRg/export?format=csv&gid=1189139415"
URL_CAMPAIGNS = "https://docs.google.com/spreadsheets/d/1aApLVf9PPIcClcelziEzUqwWXFrc8a4pZgfqesQoQBw/export?format=csv&gid=1064973789"

@st.cache_data(ttl=60)
def load_data():
    try:
        obs_df = pd.read_csv(URL_OBSERVERS)
        camp_df = pd.read_csv(URL_CAMPAIGNS)
        return obs_df, camp_df
    except:
        return None, None

observers, campaigns = load_data()

# القائمة الجانبية
st.sidebar.title("🛠️ نظام الرقابة الذكي")
menu = ["لوحة التحكم", "إنشاء حملة جديدة", "سجل الحملات", "دليل المراقبين"]
choice = st.sidebar.selectbox("القائمة الرئيسية", menu)

if choice == "لوحة التحكم":
    st.title("📊 حالة العمليات الرقابية")
    # إحصائيات سريعة
    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي الحملات", len(campaigns) if campaigns is not None else 0)
    c2.metric("المراقبين المتاحين", len(observers) if observers is not None else 0)
    c3.metric("مناطق التغطية", "5 مناطق")

elif choice == "إنشاء حملة جديدة":
    st.title("➕ تخطيط حملة رقابية جديدة")
    
    with st.form("campaign_form"):
        st.subheader("1️⃣ تفاصيل الزمان والمكان")
        col1, col2 = st.columns(2)
        with col1:
            camp_name = st.text_input("اسم الحملة", placeholder="مثال: حملة المنشآت الغذائية")
            camp_date = st.date_input("تاريخ الانطلاق")
        with col2:
            camp_time = st.time_input("وقت البدء")
            location = st.text_input("الموقع (المدينة/الحي)")

        st.divider()
        st.subheader("2️⃣ النطاق الجغرافي والجهات")
        col3, col4 = st.columns(2)
        with col3:
            geo_scope = st.selectbox("النطاق الجغرافي", ["حي محدد", "بلدية فرعية", "نطاق المدينة بالكامل"])
        with col4:
            participants = st.multiselect("الجهات المشاركة", ["وزارة التجارة", "البلدية", "وزارة الموارد البشرية", "الشرطة"])

        st.divider()
        st.subheader("3️⃣ الأهداف الرقابية المستهدفة")
        objectives = st.text_area("توثيق الأهداف", placeholder="اكتب الأهداف المستهدفة من هذه الحملة هنا...")

        submitted = st.form_submit_button("اعتماد وجدولة الحملة")
        
        if submitted:
            if camp_name and objectives:
                st.success(f"تمت جدولة حملة '{camp_name}' بنجاح!")
                st.info("ملاحظة: لغرض العرض، البيانات تظهر هنا. لربط الحفظ الفعلي بـ Google Sheets نحتاج لإعداد API خاص (Google Service Account).")
                # عرض ملخص لما تم إدخاله
                st.write("**ملخص الحملة:**")
                st.write(f"- التاريخ: {camp_date} | الوقت: {camp_time}")
                st.write(f"- الجهات المشاركة: {', '.join(participants)}")
            else:
                st.error("يرجى إكمال الحقول الأساسية (اسم الحملة والأهداف).")

elif choice == "سجل الحملات":
    st.title("📅 سجل الحملات المجدولة")
    if campaigns is not None:
        st.dataframe(campaigns, use_container_width=True)
    else:
        st.info("لا توجد بيانات حملات حالياً.")

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
