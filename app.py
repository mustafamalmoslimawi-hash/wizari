import streamlit as st
import sqlite3

# --- إعدادات الصفحة ---
st.set_page_config(page_title="منصة وزاريات العراق", page_icon="📚", layout="wide")

# --- الاتصال بقاعدة البيانات وتحديث الهيكل الحقول ---
def init_db():
    # نستخدم اسم قاعدة بيانات جديد wuzari_v3 لضمان تطبيق التحديثات بشكل نظيف
    conn = sqlite3.connect('wuzari_v3.db')
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
    
    # إضافة بيانات تجريبية متكاملة تشمل السنوات الجديدة والأدوار المختلفة
    cursor.execute("SELECT COUNT(*) FROM questions")
    if cursor.fetchone()[0] == 0:
        sample_data = [
            ("السادس الاحيائي", "كيمياء", "2018", "الدور الاول", "الفصل الثاني", "ما تأثير تغير الضغط على تفاعل متزن يعادل فيه عدد مولات الغازات؟ وضّح وفق قاعدة لوشاتيليه.", "https://example.com/sol1.pdf"),
            ("السادس الاحيائي", "كيمياء", "2018", "الدور الثاني", "الفصل الأول", "احسب قيمة المسعر الحراري للتفاعل التالي...", "https://example.com/sol2.pdf"),
            ("السادس الاحيائي", "فيزياء", "2024", "التمهيدي", "الفصل الأول", "ماذا يحصل لفرق الجهد بين صفيحتي متسعة عند إدخال عازل؟", "https://example.com/sol3.pdf"),
            ("السادس الاحيائي", "فيزياء", "2026", "الدور الاول", "الفصل الثاني", "سؤال وزاري افتراضي للتأكد من عمل الفلتر لعام 2026...", "https://example.com/sol4.pdf"),
            ("الثالث المتوسط", "رياضيات", "2018", "الدور الثالث", "الفصل الاول", "حل المتباينة المركبة التالية ومثل الحل على خط الأعداد...", "https://example.com/sol5.pdf")
        ]
        cursor.executemany('''
        INSERT INTO questions (branch, subject, year, role, chapter, question_text, answer_path)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', sample_data)
        conn.commit()
    conn.close()

init_db()

# --- دالة الاستعلام من قاعدة البيانات ---
def query_db(sql, params=()):
    conn = sqlite3.connect('wuzari_v3.db')
    cursor = conn.cursor()
    cursor.execute(sql, params)
    results = cursor.fetchall()
    conn.close()
    return results

# --- واجهة المستخدم (Streamlit UI) ---
st.title("📚 منصة الأرشيف الوزاري العراقي المطور")
st.write("أهلاً بك يا بطل، ابحث أو تصفح كل الأسئلة الوزارية مع الأجوبة النموذجية الصادرة عن مركز الفحص.")

tab1, tab2 = st.tabs(["📂 تصفح حسب الفلاتر والمواد", "🔍 محرك البحث الذكي المباشر"])

# --- التبويب الأول: التصفح المنظم والمعدل ---
with tab1:
    st.subheader("تصفح الأرشيف")
    
    # تقسيم الخيارات إلى 4 أعمدة متناسقة لتشمل (المرحلة، المادة، السنة، الدور)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # 1. قائمة المراحل/الفروع كاملة
        branch_choice = st.selectbox(
            "اختر المرحلة / الفرع:", 
            ["السادس الاحيائي", "السادس التطبيقي", "السادس الادبي", "السادس الابتدائي", "الثالث المتوسط"]
        )
        
    with col2:
        # 2. تغيير المواد تلقائياً لتناسب الفرع المختار
        if "السادس" in branch_choice and "الالابتدائي" not in branch_choice:
            if branch_choice == "السادس الادبي":
                subjects = ["عربي", "انكليزي", "رياضيات", "تاريخ", "جغرافيا", "اقتصاد", "اسلامية"]
            else:
                subjects = ["كيمياء", "فيزياء", "احياء", "رياضيات", "عربي", "انكليزي", "اسلامية"]
        elif branch_choice == "الثالث المتوسط":
            subjects = ["رياضيات", "كيمياء", "فيزياء", "احياء", "عربي", "انكليزي", "اسلامية", "اجتماعيات"]
        else: # السادس الابتدائي
            subjects = ["رياضيات", "علوم", "عربي", "انكليزي", "اسلامية", "اجتماعيات"]
            
        subject_choice = st.selectbox("اختر المادة:", subjects)
        
    with col3:
        # 3. قائمة السنوات المحدثة بالكامل حتى عام 2027 تنازلياً
        year_choice = st.selectbox(
            "السنة:", 
            ["الكل", "2027", "2026", "2025", "2024", "2023", "2022", "2021", "2020", "2019", "2018"]
        )
        
    with col4:
        # 4. قائمة الأدوار كاملة
        role_choice = st.selectbox(
            "الدور:", 
            ["الكل", "الدور الاول", "الدور الثاني", "الدور الثالث", "التمهيدي"]
        )

    # بناء الاستعلام بشكل مرن بناءً على الفلاتر المختارة
    sql = "SELECT year, role, chapter, question_text, answer_path FROM questions WHERE branch = ? AND subject = ?"
    params = [branch_choice, subject_choice]
    
    if year_choice != "الكل":
        sql += " AND year = ?"
        params.append(year_choice)
        
    if role_choice != "الكل":
        sql += " AND role = ?"
        params.append(role_choice)
        
    results = query_db(sql, tuple(params))
    
    # عرض النتائج في واجهة الموقع
    st.write("---")
    if results:
        st.success(f"✅ تم العثور على {len(results)} سؤال وزاري مطابِق لخياراتك:")
        for res in results:
            with st.container():
                st.info(f"📅 السنة: {res[0]} | 🛑 {res[1]} | 📖 {res[2]}")
                st.write(f"**السؤال:** {res[3]}")
                st.markdown(f"[📥 تحميل الحل النموذجي المعتمد (PDF)]({res[4]})")
                st.write("---")
    else:
        st.warning("⚠️ لا توجد أسئلة مضافة تطابق هذا التحديد حالياً في قاعدة البيانات.")

# --- التبويب الثاني: محرك البحث الذكي المباشر ---
with tab2:
    st.subheader("محرك البحث الشامل في نصوص الأسئلة")
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
            st.warning("❌ لم يتم العثور على أي سؤال يحتوي على هذه الكلمة.")
