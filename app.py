import streamlit as st
import sqlite3
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="منصة وزاريات العراق", page_icon="📚", layout="wide")

# --- CUSTOM CSS FOR RTL AND HIDING STREAMLIT ELEMENTS ---
st.markdown("""
    <style>
    .stApp, div, p, span, h1, h2, h3, h4, h5, h6, label {
        direction: rtl !important;
        text-align: right !important;
    }
    input, textarea, select, .stSelectbox, .stTextInput, .stTextArea {
        direction: rtl !important;
        text-align: right !important;
    }
    div[data-baseweb="select"] * {
        text-align: right !important;
        direction: rtl !important;
    }
    div[data-testid="stTabs"] button {
        direction: rtl !important;
        text-align: right !important;
    }
    div[data-testid="stTabs"] {
        direction: rtl !important;
    }
    button[data-testid="baseButton-secondary"], button[data-testid="baseButton-formSubmit"] {
        float: right !important;
        direction: rtl !important;
    }
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
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden !important; display: none !important;}
    div[data-testid="stStatusWidget"] {visibility: hidden;}
    [data-testid="stDecoration"] {display: none;}
    .viewerBadge_container__1QSob {display: none !important;}
    div[data-testid="stFooter"] {display: none !important;}
    footer a {display:none !important;}
    </style>
    <div class="alert-banner-red">
        🔔 هام: جدول ثالث متوسط دور أول 2026 <a class="btn-click" href="#schedules_section">اضغط هنا للمشاهدة</a>
    </div>
    <div class="alert-banner-blue">
        🔔 هام: جدول سادس إعدادي دور أول 2026 <a class="btn-click" href="#schedules_section">اضغط هنا للمشاهدة</a>
    </div>
""", unsafe_allow_html=True)

# --- DATABASE CONFIGURATION ---
DB_NAME = 'wuzari_v6.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
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
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        branch TEXT,
        year TEXT,
        role TEXT,
        schedule_path TEXT
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS textbooks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stage TEXT,
        grade TEXT,
        book_name TEXT,
        download_url TEXT
    )
    ''')
    conn.commit()
    conn.close()

init_db()

def query_db(sql, params=()):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(sql, params)
    results = cursor.fetchall()
    conn.close()
    return results

def modify_db(sql, params=()):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(sql, params)
    conn.commit()
    conn.close()

# --- MAIN USER INTERFACE ---
st.title("📚 منصة الأرشيف الأكاديمي العراقي الشامل")
st.write("المنصة الموحدة للطلاب: تصفح الأسئلة الوزارية، الجداول الامتحانية الرسمية، والكتب المنهجية المعتمدة.")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📂 تصفح الأسئلة والوزاريات", 
    "📅 أرشيف الجداول الامتحانية", 
    "📘 الكتب الدراسية المنهجية",
    "🔍 محرك البحث الذكي",
    "🔐 لوحة التحكم (رفع وتعديل الأسئلة)"
])

# --- TAB 1: BROWSE ---
with tab1:
    st.subheader("🗂️ تصفح الأرشيف الوزاري للمواد والحلول")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        branch_choice = st.selectbox("اختر المرحلة / الفرع:", ["السادس الاحيائي", "السادس التطبيقي", "السادس الادبي", "السادس الابتدائي", "الثالث المتوسط"])
    with col2:
        if "السادس" in branch_choice and "الابتدائي" not in branch_choice:
            subjects = ["عربي", "انكليزي", "رياضيات", "تاريخ", "جغرافيا", "اقتصاد", "اسلامية"] if branch_choice == "السادس الادبي" else ["احياء", "كيمياء", "فيزياء", "رياضيات", "عربي", "انكليزي", "اسلامية"]
        elif branch_choice == "الثالث المتوسط":
            subjects = ["رياضيات", "كيمياء", "فيزياء", "احياء", "عربي", "انكليزي", "اسلامية", "اجتماعيات"]
        else:
            subjects = ["رياضيات", "علوم", "عربي", "انكليزي", "اسلامية", "اجتماعيات"]
        subject_choice = st.selectbox("اختر المادة:", subjects, key="subject_main")
    with col3:
        year_choice = st.selectbox("السنة:", ["الكل", "2030", "2029", "2028", "2027", "2026", "2025", "2024", "2023", "2022", "2021", "2020", "2019", "2018", "2017", "2016", "2015", "2014", "2013"], key="year_main")
    with col4:
        role_choice = st.selectbox("الدور:", ["الكل", "الدور الاول", "الدور الثاني", "الدور الثالث", "التمهيدي"], key="role_main")

    sql = "SELECT year, role, chapter, question_text, answer_path FROM questions WHERE branch = ? AND subject = ?"
    params = [branch_choice, subject_choice]
    if year_choice != "الكل":
        sql += " AND year = ?"; params.append(year_choice)
    if role_choice != "الكل":
        sql += " AND role = ?"; params.append(role_choice)
    results = query_db(sql, tuple(params))
    
    st.write("---")
    if results:
        st.success(f"✅ تم العثور على {len(results)} سؤال وزاري مطابق لخياراتك:")
        for res in results:
            with st.container():
                st.info(f"📅 السنة: {res[0]} | 🛑 {res[1]} | 📖 {res[2]}")
                st.write(f"**السؤال:**")
                st.info(res[3])
                if res[4]:
                    with st.expander("✨ اضغط هنا لمشاهدة حل السؤال النموذجي"):
                        st.write(res[4])
                st.write("---")
    else:
        st.warning("⚠️ لا توجد أسئلة مضافة تطابق هذا التحديد حالياً.")

# --- TAB 2, 3, 4 (Schedules, Books, Search retained as standard) ---
with tab2:
    st.markdown('<div id="schedules_section"></div>', unsafe_allow_html=True)
    st.subheader("📋 القوائم المنسدلة للجداول الامتحانية الرسمية")
    col_sch1, col_sch2, col_sch3 = st.columns(3)
    with col_sch1: sch_branch = st.selectbox("اختر المرحلة (للجدول):", ["السادس الاحيائي", "السادس التطبيقي", "السادس الادبي", "السادس الابتدائي", "الثالث المتوسط"], key="sb")
    with col_sch2: sch_year = st.selectbox("سنة الجدول:", ["الكل", "2030", "2029", "2028", "2027", "2026", "2025", "2024", "2023", "2022", "2021", "2020", "2019", "2018", "2017", "2016", "2015", "2014", "2013"], key="sy")
    with col_sch3: sch_role = st.selectbox("دور الجدول:", ["الكل", "الدور الاول", "الدور الثاني", "التمهيدي"], key="sr")
    sql_sch = "SELECT year, role, schedule_path FROM schedules WHERE branch = ?"
    params_sch = [sch_branch]
    if sch_year != "الكل": sql_sch += " AND year = ?"; params_sch.append(sch_year)
    if sch_role != "الكل": sql_sch += " AND role = ?"; params_sch.append(sch_role)
    sch_results = query_db(sql_sch, tuple(params_sch))
    st.write("---")
    if sch_results:
        for sch in sch_results:
            st.warning(f"📅 الجدول الرسمي لعام {sch[0]} - {sch[1]} ({sch_branch})")
            st.markdown(f"[🔗 اضغط هنا لفتح أو تحميل الجدول الوزاري المعتمد]({sch[2]})")
            st.write("---")
    else: st.info("⚠️ لم يتم رفع الجدول الخاص بهذه الاختيارات بعد.")

with tab3:
    st.subheader("📘 الحقيبة المدرسية - تحميل الكتب الدراسية الرسمية")
    col_bk1, col_bk2 = st.columns(2)
    with col_bk1: stage_choice = st.selectbox("اختر المرحلة العامة:", ["المرحلة الابتدائية", "المرحلة المتوسطة", "المرحلة الاعدادية"], key="stage_bk")
    with col_bk2:
        grades = ["الصف السادس الابتدائي"] if stage_choice == "المرحلة الابتدائية" else (["الصف الثالث المتوسط"] if stage_choice == "المرحلة المتوسطة" else ["الصف السادس العلمي", "الصف السادس الادبي"])
        grade_choice = st.selectbox("اختر الصف الدراسي المحدّد:", grades, key="grade_bk")
    book_results = query_db("SELECT book_name, download_url FROM textbooks WHERE stage = ? AND grade = ?", (stage_choice, grade_choice))
    st.write("---")
    if book_results:
        for bk in book_results:
            col_b1, col_b2 = st.columns([3, 1])
            with col_b1: st.markdown(f"📖 **{bk[0]}** - الطبعة الرسمية المعتمدة لوزارة التربية")
            with col_b2: st.markdown(f"[📥 تحميل الكتاب (PDF)]({bk[1]})")
            st.write("<hr style='margin:0.5em 0; border:0; border-top:1px dashed #ddd;' />", unsafe_allow_html=True)

with tab4:
    st.subheader("🔍 محرك البحث الشامل في نصوص الأسئلة")
    search_query = st.text_input("اكتب كلمة مفتاحية للبحث السريع:", placeholder="ابدأ الكتابة هنا...", key="search_bar")
    if search_query:
        search_results = query_db("SELECT branch, subject, year, role, chapter, question_text, answer_path FROM questions WHERE question_text LIKE ?", (f'%{search_query}%',))
        if search_results:
            for res in search_results:
                with st.expander(f"📍 {res[0]} | {res[1]} - السنة: {res[2]} ({res[3]})"):
                    st.write(f"**السؤال:** {res[5]}")
                    if res[6]: st.write(f"**الإجابة:** {res[6]}")

# --- TAB 5: ADMIN CONTROL PANEL (WITH EDIT/DELETE MODULE) ---
with tab5:
    st.subheader("🔐 لوحة إدارة وإضافة الأسئلة والحلول الوزارية")
    password = st.text_input("الرجاء إدخال كلمة مرور الإدارة للاستمرار:", type="password")
    
    if password == "admin123":
        st.success("🔓 تم تسجيل الدخول بنجاح بصفتك مديراً للموقع.")
        
        # نموذج الإضافة
        with st.form("add_question_form"):
            st.write("📝 **استمارة إضافة سؤال وزاري وحل نصي جديد:**")
            new_branch = st.selectbox("المرحلة / الفرع:", ["السادس الاحيائي", "السادس التطبيقي", "السادس الادبي", "الثالث المتوسط", "السادس الابتدائي"])
            new_subject = st.selectbox("المادة:", ["احياء", "كيمياء", "فيزياء", "رياضيات", "عربي", "انكليزي", "اسلامية", "تاريخ", "جغرافيا", "اقتصاد", "علوم", "اجتماعيات"])
            new_year = st.text_input("السنة الدراسية (مثال: 2026):")
            new_role = st.selectbox("الدور:", ["الدور الاول", "الدور الثاني", "الدور الثالث", "التمهيدي"])
            new_chapter = st.text_input("الفصل / الجزء:", "شامل لكافة الفصول")
            new_text = st.text_area("نص السؤال الوزاري بالكامل:")
            new_answer_text = st.text_area("نص الإجابة النموذجية للسؤال:")
            
            if st.form_submit_button("🚀 حفظ واعتماد السؤال"):
                if new_year and new_text and new_answer_text:
                    modify_db("INSERT INTO questions (branch, subject, year, role, chapter, question_text, answer_path) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                              (new_branch, new_subject, new_year, new_role, new_chapter, new_text, new_answer_text))
                    st.success("🎉 تم حفظ السؤال بنجاح!")
                else: st.error("❌ يرجى ملء الحقول المطلوبة.")
        
        # قسم التعديل والحذف الجديد ذكي جداً
        st.write("---")
        st.subheader("✏️ إدارة وتعديل الأسئلة المضافة حالياً")
        all_qs = query_db("SELECT id, branch, subject, year, role, question_text, answer_path FROM questions ORDER BY id DESC")
        
        if all_qs:
            for q_id, b, s, y, r, q_txt, a_txt in all_qs:
                with st.expander(f"⚙️ تعديل: {b} - {s} ({y} / {r}) | معرف: #{q_id}"):
                    edit_txt = st.text_area(f"تعديل نص السؤال #{q_id}:", value=q_txt, key=f"q_{q_id}")
                    edit_ans = st.text_area(f"تعديل الإجابة النموذجية #{q_id}:", value=a_txt, key=f"a_{q_id}")
                    
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("💾 حفظ التعديلات", key=f"save_{q_id}"):
                            modify_db("UPDATE questions SET question_text = ?, answer_path = ? WHERE id = ?", (edit_txt, edit_ans, q_id))
                            st.success("✅ تم تحديث السؤال بنجاح! يرجى إعادة تحديث الصفحة.")
                    with col_btn2:
                        if st.button("🗑️ حذف السؤال نهائياً", key=f"del_{q_id}"):
                            modify_db("DELETE FROM questions WHERE id = ?", (q_id,))
                            st.warning("🗑️ تم حذف السؤال من قاعدة البيانات.")
        else:
            st.info("💡 لا توجد أسئلة مضافة حالياً لتعديلها.")
            
    elif password != "": st.error("❌ كلمة المرور غير صحيحة.")
