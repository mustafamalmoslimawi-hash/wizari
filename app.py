import streamlit as st
import sqlite3
import os

# --- إعدادات الصفحة الشاملة ---
st.set_page_config(page_title="منصة وزاريات العراق", page_icon="📚", layout="wide")

# --- التنبيهات العلوية الملونة (الجداول العاجلة) ---
st.markdown("""
    <style>
    .alert-banner-red {
        background-color: #c92a2a;
        color: white;
        padding: 12px;
        border-radius: 6px;
        text-align: right;
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 8px;
        direction: rtl;
    }
    .alert-banner-blue {
        background-color: #0085cd;
        color: white;
        padding: 12px;
        border-radius: 6px;
        text-align: right;
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 20px;
        direction: rtl;
    }
    .btn-click {
        background-color: white;
        color: black !important;
        padding: 2px 12px;
        border-radius: 4px;
        text-decoration: none;
        font-size: 14px;
        margin-right: 15px;
        display: inline-block;
        font-weight: bold;
    }
    </style>
    <div class="alert-banner-red">
        🔔 هام: جدول ثالث متوسط دور أول 2026 <a class="btn-click" href="#schedules_section">اضغط هنا للمشاهدة</a>
    </div>
    <div class="alert-banner-blue">
        🔔 هام: جدول سادس إعدادي دور أول 2026 <a class="btn-click" href="#schedules_section">اضغط هنا للمشاهدة</a>
    </div>
""", unsafe_allow_html=True)


# --- اسم قاعدة البيانات (wuzari_v6.db) ---
DB_NAME = 'wuzari_v6.db'

# --- الاتصال بقاعدة البيانات وتحديث الهيكل البرمجي ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. جدول الأسئلة الوزارية والحلول النموذجية (تم إبقاء اسم answer_path لحفظ النص دون مشاكل)
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
    
    # 2. جدول الجداول الامتحانية الرسمية
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        branch TEXT,
        year TEXT,
        role TEXT,
        schedule_path TEXT
    )
    ''')
    
    # 3. جدول الكتب الدراسية الجديد
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS textbooks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stage TEXT,
        grade TEXT,
        book_name TEXT,
        download_url TEXT
    )
    ''')
    
    # إدخال بيانات تجريبية أولية للأسئلة في حال كان الجدول فارغاً تماماً
    cursor.execute("SELECT COUNT(*) FROM questions")
    if cursor.fetchone()[0] == 0:
        sample_questions = [
            ("السادس الاحيائي", "كيمياء", "2018", "الدور الاول", "الفصل الثاني", "ما تأثير تغير الضغط على تفاعل متزن يعادل فيه عدد مولات الغازات؟ وضّح وفق قاعدة لوشاتيليه.", "الجواب النموذجي: يرجح التفاعل نحو اتجاه عدد المولات الأقل عند زيادة الضغط..."),
            ("السادس الاحيائي", "كيمياء", "2018", "الدور الثاني", "الفصل الأول", "احسب قيمة المسعر الحراري للتفاعل التالي...", "الجواب النموذجي: نستخدم قانون السعة الحرارية q = mcΔT..."),
        ]
        cursor.executemany('''
        INSERT INTO questions (branch, subject, year, role, chapter, question_text, answer_path)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', sample_questions)
        
    conn.commit()
    conn.close()

# تشغيل التهيئة تلقائياً
init_db()

# --- دالة الاستعلام من قاعدة البيانات ---
def query_db(sql, params=()):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(sql, params)
    results = cursor.fetchall()
    conn.close()
    return results

# --- دالة الإدخال والكتابة في قاعدة البيانات ---
def modify_db(sql, params=()):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(sql, params)
    conn.commit()
    conn.close()


# --- واجهة المستخدم الرئيسية (Streamlit UI) ---
st.title("📚 منصة الأرشيف الأكاديمي العراقي الشامل")
st.write("المنصة الموحدة للطلاب: تصفح الأسئلة الوزارية، الجداول الامتحانية الرسمية، والكتب المنهجية المعتمدة.")

# إنشاء التبويبات الأربعة المتناسقة بالإضافة إلى لوحة التحكم
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📂 تصفح الأسئلة والوزاريات", 
    "📅 أرشيف الجداول الامتحانية", 
    "📘 الكتب الدراسية المنهجية",
    "🔍 محرك البحث الذكي",
    "🔐 لوحة التحكم (رفع الأسئلة)"
])


# --- التبويب الأول: تصفح الأسئلة والأجوبة النموذجية النصية ---
with tab1:
    st.subheader("🗂️ تصفح الأرشيف الوزاري للمواد والحلول")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        branch_choice = st.selectbox(
            "اختر المرحلة / الفرع:", 
            ["السادس الاحيائي", "السادس التطبيقي", "السادس الادبي", "السادس الابتدائي", "الثالث المتوسط"]
        )
        
    with col2:
        if "السادس" in branch_choice and "الابتدائي" not in branch_choice:
            if branch_choice == "السادس الادبي":
                subjects = ["عربي", "انكليزي", "رياضيات", "تاريخ", "جغرافيا", "اقتصاد", "اسلامية"]
            else:
                subjects = ["احياء", "كيمياء", "فيزياء", "رياضيات", "عربي", "انكليزي", "اسلامية"]
        elif branch_choice == "الثالث المتوسط":
            subjects = ["رياضيات", "كيمياء", "فيزياء", "احياء", "عربي", "انكليزي", "اسلامية", "اجتماعيات"]
        else:
            subjects = ["رياضيات", "علوم", "عربي", "انكليزي", "اسلامية", "اجتماعيات"]
            
        subject_choice = st.selectbox("اختر المادة:", subjects, key="subject_main")
        
    with col3:
        year_choice = st.selectbox(
            "السنة:", 
            ["الكل", "2027", "2026", "2025", "2024", "2023", "2022", "2021", "2020", "2019", "2018", "2013"],
            key="year_main"
        )
        
    with col4:
        role_choice = st.selectbox(
            "الدور:", 
            ["الكل", "الدور الاول", "الدور الثاني", "الدور الثالث", "التمهيدي"],
            key="role_main"
        )

    # بناء استعلام الفلاتر للأسئلة
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
        st.success(f"✅ تم العثور على {len(results)} سؤال وزاري مطابق لخياراتك:")
        for res in results:
            with st.container():
                st.info(f"📅 السنة: {res[0]} | 🛑 {res[1]} | 📖 {res[2]}")
                st.write(f"**السؤال:**")
                st.code(res[3], language="text") # عرض السؤال في قالب واضح ومميز
                
                # عرض الحل مباشرة هنا بشكل نص منسدل ومريح للطالب
                with st.expander("✨ اضغط هنا لمشاهدة حل السؤال النموذجي مباشرة"):
                    st.write(res[4])
                st.write("---")
    else:
        st.warning("⚠️ لا توجد أسئلة مضافة تطابق هذا التحديد حالياً.")


# --- التبويب الثاني: أرشيف الجداول الامتحانية ---
with tab2:
    st.markdown('<div id="schedules_section"></div>', unsafe_allow_html=True)
    st.subheader("📋 القوائم المنسدلة للجداول الامتحانية الرسمية")
    
    col_sch1, col_sch2, col_sch3 = st.columns(3)
    with col_sch1:
        sch_branch = st.selectbox("اختر المرحلة (للجدول):", ["السادس الاحيائي", "السادس التطبيقي", "السادس الادبي", "السادس الابتدائي", "الثالث المتوسط"], key="sb")
    with col_sch2:
        sch_year = st.selectbox("سنة الجدول:", ["الكل", "2026", "2025", "2024", "2023"], key="sy")
    with col_sch3:
        sch_role = st.selectbox("دور الجدول:", ["الكل", "الدور الاول", "الدور الثاني", "التمهيدي"], key="sr")
        
    sql_sch = "SELECT year, role, schedule_path FROM schedules WHERE branch = ?"
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
        for sch in sch_results:
            st.warning(f"📅 الجدول الرسمي لعام {sch[0]} - {sch[1]} ({sch_branch})")
            st.markdown(f"[🔗 اضغط هنا لفتح أو تحميل الجدول الوزاري المعتمد]({sch[2]})")
            st.write("---")


# --- التبويب الثالث: أرشيف وقائمة الكتب الدراسية المنهجية ---
with tab3:
    st.subheader("📘 الحقيبة المدرسية - تحميل الكتب الدراسية الرسمية")
    col_bk1, col_bk2 = st.columns(2)
    with col_bk1:
        stage_choice = st.selectbox("اختر المرحلة العامة:", ["المرحلة الابتدائية", "المرحلة المتوسطة", "المرحلة الاعدادية"], key="stage_bk")
    with col_bk2:
        if stage_choice == "المرحلة الابتدائية":
            grades = ["الصف السادس الابتدائي"]
        elif stage_choice == "المرحلة المتوسطة":
            grades = ["الصف الثالث المتوسط"]
        else:
            grades = ["الصف السادس العلمي", "الصف السادس الادبي"]
        grade_choice = st.selectbox("اختر الصف الدراسي المحدّد:", grades, key="grade_bk")
        
    sql_books = "SELECT book_name, download_url FROM textbooks WHERE stage = ? AND grade = ?"
    book_results = query_db(sql_books, (stage_choice, grade_choice))
    st.write("---")
    if book_results:
        for bk in book_results:
            col_b1, col_b2 = st.columns([3, 1])
            with col_b1:
                st.markdown(f"📖 **{bk[0]}** - الطبعة الرسمية المعتمدة لوزارة التربية")
            with col_b2:
                st.markdown(f"[📥 تحميل الكتاب (PDF)]({bk[1]})")


# --- التبويب الرابع: محرك البحث الذكي المباشر ---
with tab4:
    st.subheader("🔍 محرك البحث الشامل في نصوص الأسئلة")
    search_query = st.text_input("اكتب كلمة مفتاحية للبحث السريع:", placeholder="ابدأ الكتابة هنا...", key="search_bar")
    if search_query:
        sql_search = "SELECT branch, subject, year, role, chapter, question_text, answer_path FROM questions WHERE question_text LIKE ?"
        search_results = query_db(sql_search, (f'%{search_query}%',))
        if search_results:
            for res in search_results:
                with st.expander(f"📍 {res[0]} | {res[1]} - السنة: {res[2]} ({res[3]})"):
                    st.write(f"**السؤال:** {res[5]}")
                    st.write(f"**الحـل:** {res[6]}")


# --- التبويب الخامس: لوحة التحكم لرفع الأسئلة كـ نصوص ---
with tab5:
    st.subheader("🔐 لوحة إدارة وإضافة الأسئلة الوزارية")
    password = st.text_input("الرجاء إدخال كلمة مرور الإدارة للاستمرار:", type="password")
    
    if password == "admin123":
        st.success("🔓 تم تسجيل الدخول بنجاح بصفتك مديراً للموقع. يمكنك الآن إضافة الأسئلة الجديدة:")
        
        with st.form("add_question_form"):
            st.write("📝 **استمارة إضافة سؤال وجواب وزاري بنص مباشر:**")
            
            new_branch = st.selectbox("المرحلة / الفرع:", ["السادس الاحيائي", "السادس التطبيقي", "السادس الادبي", "الثالث المتوسط", "السادس الابتدائي"])
            new_subject = st.selectbox("المادة:", ["احياء", "كيمياء", "فيزياء", "رياضيات", "عربي", "انكليزي", "اسلامية"])
            new_year = st.text_input("السنة الدراسية (مثال: 2013):", placeholder="2013")
            new_role = st.selectbox("الدور:", ["الدور الاول", "الدور الثاني", "الدور الثالث", "التمهيدي"])
            new_chapter = st.text_input("الفصل / الجزء (مثال: الفصل الثالث):", "شامل لكافة الفصول")
            
            # الصناديق الكبيرة المناسبة لكتابة وتعديل النصوص مباشرة
            new_text = st.text_area("✍️ نص السؤال الوزاري بالكامل:")
            new_answer_text = st.text_area("✍️ نص الإجابة النموذجية للسؤال بالكامل:")
            
            submit_btn = st.form_submit_button("🚀 حفظ واعتماد السؤال في الموقع")
            
            if submit_btn:
                if new_year and new_text and new_answer_text:
                    sql_insert = """
                    INSERT INTO questions (branch, subject, year, role, chapter, question_text, answer_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """
                    modify_db(sql_insert, (new_branch, new_subject, new_year, new_role, new_chapter, new_text, new_answer_text))
                    st.success(f"🎉 تم بنجاح حفظ السؤال والجواب لعام {new_year} مادة {new_subject} وعرضهما في الموقع!")
                else:
                    st.error("❌ يرجى ملء حقول السنة، نص السؤال، ونص الإجابة لإتمام عملية الحفظ.")
    elif password != "":
        st.error("❌ كلمة المرور غير صحيحة.")
