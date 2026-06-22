import streamlit as st
import sqlite3

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


# --- الاتصال بقاعدة البيانات وتحديث الهيكل البرمجي ---
def init_db():
    # نستخدم قاعدة بيانات محدثة بالكامل لضمان بناء الجداول بدون أي مشاكل تعارض
    conn = sqlite3.connect('wuzari_v5.db')
    cursor = conn.cursor()
    
    # 1. جدول الأسئلة الوزارية والحلول النموذجية
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
    
    # 3. جدول الكتب الدراسية الجديد (المرحلة الابتدائية، المتوسطة، الاعدادية)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS textbooks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stage TEXT,
        grade TEXT,
        book_name TEXT,
        download_url TEXT
    )
    ''')
    
    # إدخال بيانات تجريبية للأسئلة في حال كان الجدول فارغاً
    cursor.execute("SELECT COUNT(*) FROM questions")
    if cursor.fetchone()[0] == 0:
        sample_questions = [
            ("السادس الاحيائي", "كيمياء", "2018", "الدور الاول", "الفصل الثاني", "ما تأثير تغير الضغط على تفاعل متزن يعادل فيه عدد مولات الغازات؟ وضّح وفق قاعدة لوشاتيليه.", "https://example.com/sol1.pdf"),
            ("السادس الاحيائي", "كيمياء", "2018", "الدور الثاني", "الفصل الأول", "احسب قيمة المسعر الحراري للتفاعل التالي...", "https://example.com/sol2.pdf"),
            ("السادس الاحيائي", "فيزياء", "2024", "التمهيدي", "الفصل الأول", "ماذا يحصل لفرق الجهد بين صفيحتي متسعة عند إدخال عازل؟", "https://example.com/sol3.pdf"),
            ("السادس الاحيائي", "فيزياء", "2026", "الدور الاول", "الفصل الثاني", "سؤال وزاري افتراضي للتأكد من عمل الفلتر لعام 2026...", "https://example.com/sol4.pdf"),
            ("الثالث المتوسط", "رياضيات", "2024", "الدور الاول", "الفصل الاول", "حل المتباينة المركبة التالية ومثل الحل على خط الأعداد...", "https://example.com/sol5.pdf")
        ]
        cursor.executemany('''
        INSERT INTO questions (branch, subject, year, role, chapter, question_text, answer_path)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', sample_questions)
        
    # إدخال بيانات تجريبية للجداول الامتحانية
    cursor.execute("SELECT COUNT(*) FROM schedules")
    if cursor.fetchone()[0] == 0:
        sample_schedules = [
            ("السادس الاحيائي", "2026", "الدور الاول", "https://example.com/schedule_sads_2026_d1.pdf"),
            ("الثالث المتوسط", "2026", "الدور الاول", "https://example.com/schedule_thalth_2026_d1.pdf"),
            ("السادس الاحيائي", "2024", "الدور الثاني", "https://example.com/schedule_sads_2024_d2.pdf"),
            ("الثالث المتوسط", "2023", "التمهيدي", "https://example.com/schedule_thalth_2023_pre.pdf")
        ]
        cursor.executemany('''
        INSERT INTO schedules (branch, year, role, schedule_path)
        VALUES (?, ?, ?, ?)
        ''', sample_schedules)

    # إدخال بيانات تجريبية للكتب الدراسية لمختلف المراحل الثلاثة
    cursor.execute("SELECT COUNT(*) FROM textbooks")
    if cursor.fetchone()[0] == 0:
        sample_books = [
            ("المرحلة الابتدائية", "الصف السادس الابتدائي", "كتاب الرياضيات", "https://example.com/math_primary_6.pdf"),
            ("المرحلة الابتدائية", "الصف السادس الابتدائي", "كتاب العلوم", "https://example.com/science_primary_6.pdf"),
            ("المرحلة المتوسطة", "الصف الثالث المتوسط", "كتاب الرياضيات - الجزء الأول", "https://example.com/math_mid_3_p1.pdf"),
            ("المرحلة المتوسطة", "الصف الثالث المتوسط", "كتاب الكيمياء", "https://example.com/chemistry_mid_3.pdf"),
            ("المرحلة الاعدادية", "الصف السادس العلمي", "كتاب الفيزياء", "https://example.com/physics_high_6.pdf"),
            ("المرحلة الاعدادية", "الصف السادس العلمي", "كتاب الكيمياء", "https://example.com/chemistry_high_6.pdf")
        ]
        cursor.executemany('''
        INSERT INTO textbooks (stage, grade, book_name, download_url)
        VALUES (?, ?, ?, ?)
        ''', sample_books)
        
    conn.commit()
    conn.close()

init_db()

# --- دالة الاستعلام من قاعدة البيانات ---
def query_db(sql, params=()):
    conn = sqlite3.connect('wuzari_v5.db')
    cursor = conn.cursor()
    cursor.execute(sql, params)
    results = cursor.fetchall()
    conn.close()
    return results


# --- واجهة المستخدم الرئيسية (Streamlit UI) ---
st.title("📚 منصة الأرشيف الأكاديمي العراقي الشامل")
st.write("المنصة الموحدة للطلاب: تصفح الأسئلة الوزارية، الجداول الامتحانية الرسمية، والكتب المنهجية المعتمدة.")

# إنشاء التبويبات الأربعة المتناسقة والمنظمة
tab1, tab2, tab3, tab4 = st.tabs([
    "📂 تصفح الأسئلة والوزاريات", 
    "📅 أرشيف الجداول الامتحانية", 
    "📘 الكتب الدراسية المنهجية",
    "🔍 محرك البحث الذكي"
])


# --- التبويب الأول: تصفح الأسئلة والأجوبة النموذجية ---
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
                subjects = ["كيمياء", "فيزياء", "احياء", "رياضيات", "عربي", "انكليزي", "اسلامية"]
        elif branch_choice == "الثالث المتوسط":
            subjects = ["رياضيات", "كيمياء", "فيزياء", "احياء", "عربي", "انكليزي", "اسلامية", "اجتماعيات"]
        else:
            subjects = ["رياضيات", "علوم", "عربي", "انكليزي", "اسلامية", "اجتماعيات"]
            
        subject_choice = st.selectbox("اختر المادة:", subjects)
        
    with col3:
        year_choice = st.selectbox(
            "السنة:", 
            ["الكل", "2027", "2026", "2025", "2024", "2023", "2022", "2021", "2020", "2019", "2018"]
        )
        
    with col4:
        role_choice = st.selectbox(
            "الدور:", 
            ["الكل", "الدور الاول", "الدور الثاني", "الدور الثالث", "التمهيدي"]
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
                st.write(f"**السؤال:** {res[3]}")
                st.markdown(f"[📥 تحميل الحل النموذجي المعتمد (PDF)]({res[4]})")
                st.write("---")
    else:
        st.warning("⚠️ لا توجد أسئلة مضافة تطابق هذا التحديد حالياً.")


# --- التبويب الثاني: أرشيف الجداول الامتحانية (لكافة السنين والأدوار) ---
with tab2:
    st.markdown('<div id="schedules_section"></div>', unsafe_allow_html=True)
    st.subheader("📋 القوائم المنسدلة للجداول الامتحانية الرسمية")
    st.write("اختر تفاصيل السنة والدور للمرحلة المحددة للحصول على جدول الامتحانات الوزارية الرسمي الصادر من وزارة التربية:")
    
    col_sch1, col_sch2, col_sch3 = st.columns(3)
    
    with col_sch1:
        sch_branch = st.selectbox("اختر المرحلة (للجدول):", ["السادس الاحيائي", "السادس التطبيقي", "السادس الادبي", "السادس الابتدائي", "الثالث المتوسط"], key="sb")
    with col_sch2:
        sch_year = st.selectbox("سنة الجدول:", ["الكل", "2027", "2026", "2025", "2024", "2023", "2022", "2021", "2020", "2019", "2018"], key="sy")
    with col_sch3:
        sch_role = st.selectbox("دور الجدول:", ["الكل", "الدور الاول", "الدور الثاني", "الدور الثالث", "التمهيدي"], key="sr")
        
    # بناء استعلام البحث في جداول الامتحانات
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
            st.markdown(f"[🔗 اضغط هنا لفتح أو تحميل الجدول الوزاري المعتمد (PDF / صورة)]({sch[2]})")
            st.write("---")
    else:
        st.info("⚠️ لم يتم رفع الجدول الخاص بهذه الاختيارات في أرشيف قاعدة البيانات بعد.")


# --- التبويب الثالث: أرشيف وقائمة الكتب الدراسية المنهجية (الميزة الجديدة المضافة) ---
with tab3:
    st.subheader("📘 الحقيبة المدرسية - تحميل الكتب الدراسية الرسمية")
    st.write("تصفح وحمل كتب وزارة التربية العراقية الرسمية والحديثة المخصصة لمرحلتك الدراسية:")
    
    col_bk1, col_bk2 = st.columns(2)
    
    with col_bk1:
        stage_choice = st.selectbox("اختر المرحلة العامة:", ["المرحلة الابتدائية", "المرحلة المتوسطة", "المرحلة الاعدادية"])
        
    with col_bk2:
        if stage_choice == "المرحلة الابتدائية":
            grades = ["الصف الأول الابتدائي", "الصف الثاني الابتدائي", "الصف الثالث الابتدائي", "الصف الرابع الابتدائي", "الصف الخامس الابتدائي", "الصف السادس الابتدائي"]
        elif stage_choice == "المرحلة المتوسطة":
            grades = ["الصف الأول المتوسط", "الصف الثاني المتوسط", "الصف الثالث المتوسط"]
        else:
            grades = ["الصف الرابع الإعدادي", "الصف الخامس الإعدادي", "الصف السادس العلمي", "الصف السادس الادبي"]
            
        grade_choice = st.selectbox("اختر الصف الدراسي المحدّد:", grades)
        
    # الاستعلام عن الكتب بناءً على اختيارات القائمة المنسدلة لـ (المرحلة العامة والصف الدراسي)
    sql_books = "SELECT book_name, download_url FROM textbooks WHERE stage = ? AND grade = ?"
    book_results = query_db(sql_books, (stage_choice, grade_choice))
    
    st.write("---")
    if book_results:
        st.success(f"📚 تم العثور على {len(book_results)} كتاب منهجى متاح لـ {grade_choice}:")
        
        # عرض الكتب المكتشفة في جداول / شبكة منسقة وخفيفة
        for bk in book_results:
            col_b1, col_b2 = st.columns([3, 1])
            with col_b1:
                st.markdown(f"📖 **{bk[0]}** - الطبعة الرسمية المعتمدة لوزارة التربية")
            with col_b2:
                st.markdown(f"[📥 تحميل الكتاب (PDF)]({bk[1]})")
            st.write("<hr style='margin:0.5em 0; border:0; border-top:1px dashed #ddd;' />", unsafe_allow_html=True)
    else:
        st.info("⚠️ سيتم إضافة وتحديث روابط الكتب الخاصة بهذا الصف قريباً جداً في النظام.")


# --- التبويب الرابع: محرك البحث الذكي المباشر ---
with tab3 if 'tab4' not in locals() else tab4:
    st.subheader("🔍 محرك البحث الشامل في نصوص الأسئلة")
    search_query = st.text_input("اكتب كلمة مفتاحية (مثال: دي موافر، متسعة، لوشاتيليه):", placeholder="ابدأ الكتابة هنا...")
    
    if search_query:
        sql_search = "SELECT branch, subject, year, role, chapter, question_text, answer_path FROM questions WHERE question_text LIKE ?"
        search_results = query_db(sql_search, (f'%{search_query}%',))
        
        if search_results:
            st.success(f"تم العثور على {len(search_results)} نتيجة:")
            for res in search_results:
                with st.expander(f"📍 {res[0]} | {res[1]} - السنة: {res[2]} ({res[3]})"):
                    st.write(f"**السؤال:** {res[5]}")
                    st.markdown(f"[🔗 رابط الحل النموذجي المباشر]({res[6]})")
        else:
            st.warning("❌ لم يتم العثور على أي سؤال يحتوي على هذه الكلمة الكودية.")
