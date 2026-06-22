import streamlit as st
import sqlite3

# --- إعدادات الصفحة ---
st.set_page_config(page_title="منصة وزاريات العراق", page_icon="📚", layout="wide")

# --- دالة مخصصة لعمل نافذة معاينة الملفات (PDF / الصور) ---
def iframe_preview(url):
    # استخدام مستعرض جوجل الرسمي للمعاينة لضمان فتح الملف داخل المتصفح دون تحميل إجباري
    preview_url = f"https://docs.google.com/gview?url={url}&embedded=true"
    st.markdown(f'<iframe src="{preview_url}" width="100%" height="500px" style="border:none; border-radius:8px;"></iframe>', unsafe_allow_html=True)

# --- التنبيهات العلوية (كما في الصورة المطلوبة تماماً) ---
st.markdown("""
    <style>
    .alert-banner-red {
        background-color: #c92a2a;
        color: white;
        padding: 10px;
        border-radius: 5px;
        text-align: right;
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 8px;
    }
    .alert-banner-blue {
        background-color: #0085cd;
        color: white;
        padding: 10px;
        border-radius: 5px;
        text-align: right;
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .btn-click {
        background-color: white;
        color: black;
        padding: 2px 10px;
        border-radius: 3px;
        text-decoration: none;
        font-size: 14px;
        margin-right: 15px;
        display: inline-block;
    }
    </style>
    <div class="alert-banner-red">
        🚨 هام: جدول ثالث متوسط دور أول 2026 <a class="btn-click" href="#jdwl">اضغط هنا للمعاينة</a>
    </div>
    <div class="alert-banner-blue">
        🔔 هام: جدول سادس إعدادي دور أول 2026 <a class="btn-click" href="#jdwl">اضغط هنا للمعاينة</a>
    </div>
""", unsafe_allow_html=True)


# --- الاتصال بقاعدة البيانات وتحديث الهيكل ---
def init_db():
    conn = sqlite3.connect('wuzari_v5.db') # إصدار جديد v5 نظيف
    cursor = conn.cursor()
    
    # 1. جدول الأسئلة الوزارية
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        branch TEXT,
        subject TEXT,
        year TEXT,
        role TEXT,
        chapter TEXT,
        question_text TEXT,
        answer_path TEXT
    )
    ''')
    
    # 2. جدول الجداول الامتحانية
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        branch TEXT,
        year TEXT,
        role TEXT,
        image_or_pdf_path TEXT
    )
    ''')
    
    # إضافة روابط ملفات افتراضية حقيقية صالحة للمعاينة كمثال لتجربتها بنفسك
    cursor.execute("SELECT COUNT(*) FROM questions")
    if cursor.fetchone()[0] == 0:
        sample_questions = [
            ("السادس الاحيائي", "كيمياء", "2018", "الدور الاول", "الفصل الثاني", "ما تأثير تغير الضغط على تفاعل متزن يعادل فيه عدد مولات الغازات؟ وضّح وفق قاعدة لوشاتيليه.", "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"),
            ("السادس الاحيائي", "كيمياء", "2024", "الدور الاول", "الفصل الأول", "احسب قيمة انثالبي التفاعل القياسية باستخدام قانون هيس...", "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"),
            ("الثالث المتوسط", "رياضيات", "2024", "التمهيدي", "الفصل الاول", "حل المتباينة المركبة التالية ومثل الحل على خط الأعداد...", "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf")
        ]
        cursor.executemany('''
        INSERT INTO questions (branch, subject, year, role, chapter, question_text, answer_path)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', sample_questions)
        
    cursor.execute("SELECT COUNT(*) FROM schedules")
    if cursor.fetchone()[0] == 0:
        sample_schedules = [
            ("السادس الاحيائي", "2026", "الدور الاول", "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"),
            ("الثالث المتوسط", "2026", "الدور الاول", "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"),
            ("السادس الاحيائي", "2024", "الدور الاول", "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf")
        ]
        cursor.executemany('''
        INSERT INTO schedules (branch, year, role, image_or_pdf_path)
        VALUES (?, ?, ?, ?)
        ''', sample_schedules)
        
    conn.commit()
    conn.close()

init_db()

# --- دالة الاستعلام ---
def query_db(sql, params=()):
    conn = sqlite3.connect('wuzari_v5.db')
    cursor = conn.cursor()
    cursor.execute(sql, params)
    results = cursor.fetchall()
    conn.close()
    return results


# --- واجهة المستخدم الرئيسية ---
st.title("🏠 منصة الأرشيف الوزاري العراقي المتكاملة")
st.write("تصفح الأسئلة الوزارية، الجداول والحلول النموذجية مع ميزة المعاينة المباشرة قبل التحميل.")

tab1, tab2, tab3 = st.tabs(["📂 تصفح الأسئلة الوزارية", "📅 أرشيف الجداول الامتحانية", "🔍 محرك البحث الذكي"])

# --- التبويب الأول: تصفح الأسئلة والحلول مع خيار المعاينة ---
with tab1:
    st.subheader("🗂️ تصفح الأرشيف الوزاري للمواد")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        branch_choice = st.selectbox("اختر المرحلة / الفرع:", ["السادس الاحيائي", "السادس التطبيقي", "السادس الادبي", "السادس الابتدائي", "الثالث المتوسط"])
    with col2:
        if "السادس" in branch_choice and "الابتدائي" not in branch_choice:
            if branch_choice == "السادس الادبي":
                subjects = ["عربي", "انكليزي", "رياضيات", "تاريخ", "جغرافيا", "اقتصاد", "اسلامية"]
            else:
                subjects = ["كيمياء", "فيزياء", "احياء", "رياضيات", "عربي", "انكليزي", "اسلامية"]
        elif branch_choice == "الثالث المتوسط":
            subjects = ["رياضيات", "كيمياء", "فيزياء", "احياء", "عربي", "انكليزي", "اسلامية", "اجتماعيات"]
        else:
            subjects = ["رياضيات", "علوم", "عربي", "انكليزي", "اسلامية", "اجتماعيات"]
        subject_choice = st.selectbox("اختر المادة:", subjects)
    with col3:
        year_choice = st.selectbox("السنة:", ["الكل", "2027", "2026", "2025", "2024", "2023", "2022", "2021", "2020", "2019", "2018"])
    with col4:
        role_choice = st.selectbox("الدور:", ["الكل", "الدور الاول", "الدور الثاني", "الدور الثالث", "التمهيدي"])

    # بناء الاستعلام
    sql = "SELECT year, role, chapter, question_text, answer_path FROM questions WHERE branch = ? AND subject = ?"
    params = [branch_choice, subject_choice]
    
    if year_choice != "الكل":
        sql += " AND year = ?"
        params.append(year_choice)
    if role_choice != "الكل":
        sql += " AND role = ?"
        params.append(role_choice)
        
    results = query_db(sql, tuple(params))
    
    st.write("---")
    if results:
        st.success(f"✅ تم العثور على {len(results)} سؤال وزارى:")
        for idx, res in enumerate(results):
            st.info(f"📅 السنة: {res[0]} | 🛑 {res[1]} | 📖 {res[2]}")
            st.write(f"**السؤال:** {res[3]}")
            
            # زر منسدل مخصص لمعاينة الأجوبة دون تحميل إجباري
            with st.expander(f"👁️ اضغط هنا لمعاينة الحل النموذجي للسؤال رقم ({idx+1})"):
                iframe_preview(res[4])
                st.markdown(f"[📥 تحميل الملف مباشرة للجهاز كـ PDF]({res[4]})")
            st.write("---")
    else:
        st.warning("⚠️ لا توجد أسئلة مضافة تطابق الخيارات المحددة حالياً.")


# --- التبويب الثاني: أرشيف الجداول الامتحانية مع المعاينة المباشرة ---
with tab2:
    st.markdown('<div id="jdwl"></div>', unsafe_allow_html=True)
    st.subheader("📅 القائمة المنسدلة للجداول الامتحانية")
    
    col_sch1, col_sch2, col_sch3 = st.columns(3)
    with col_sch1:
        sch_branch = st.selectbox("المرحلة (للجدول):", ["السادس الاحيائي", "السادس التطبيقي", "السادس الادبي", "السادس الابتدائي", "الثالث المتوسط"], key="sch_b")
    with col_sch2:
        sch_year = st.selectbox("سنة الجدول:", ["الكل", "2027", "2026", "2025", "2024", "2023", "2022", "2021", "2020", "2019", "2018"], key="sch_y")
    with col_sch3:
        sch_role = st.selectbox("دور الجدول:", ["الكل", "الدور الاول", "الدور الثاني", "الدور الثالث", "التمهيدي"], key="sch_r")
        
    sql_sch = "SELECT year, role, image_or_pdf_path FROM schedules WHERE branch = ?"
    params_sch = [sch_branch]
    
    if sch_year != "الكل":
        sql_sch += " AND year = ?"
        params_sch.append(sch_year)
    if sch_role != "الكل":
        sql_sch += " AND role = ?"
        params_sch.append(sch_role)
        
    sch_results = query_db(sql_sch, tuple(params_sch))
    
    st.write("---")
    if sch_results:
        for idx, sch in enumerate(sch_results):
            st.warning(f"📋 جدول الامتحانات الرسمية لعام {sch[0]} - {sch[1]} ({sch_branch})")
            
            # فتح قائمة منسدلة للمعاينة الفورية للجدول داخل الموقع
            with st.expander(f"👁️ معاينة الجدول المعتمد لـ {sch_branch} ({sch[0]})"):
                iframe_preview(sch[2])
                st.markdown(f"[📥 تحميل الجدول كاملاً]({sch[2]})")
            st.write("---")
    else:
        st.info("⚠️ لم يتم رفع الجدول الخاص بهذه الاختيارات بعد في الأرشيف.")


# --- التبويب الثالث: محرك البحث الذكي المباشر ---
with tab3:
    st.subheader("🔍 محرك البحث الشامل")
    search_query = st.text_input("اكتب كلمة مفتاحية للبحث المباشر:")
    if search_query:
        sql_search = "SELECT branch, subject, year, role, chapter, question_text, answer_path FROM questions WHERE question_text LIKE ?"
        search_results = query_db(sql_search, (f'%{search_query}%',))
        if search_results:
            for res in search_results:
                with st.expander(f"📍 {res[0]} | {res[1]} - السنة: {res[2]} ({res[3]})"):
                    st.write(f"**السؤال:** {res[5]}")
                    iframe_preview(res[6])
        else:
            st.warning("❌ لم يتم العثور على أي نتائج.")
