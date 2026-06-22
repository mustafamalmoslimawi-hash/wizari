import streamlit as st
import sqlite3

# --- إعدادات الصفحة ---
st.set_page_config(page_title="منصة وزاريات العراق", page_icon="📚", layout="wide")

# --- الاتصال بقاعدة البيانات وتحديث الهيكل الحقول ---
def init_db():
    # تغيير الاسم إلى v2 لإنشاء قاعدة بيانات نظيفة تحتوي على عمود branch
    conn = sqlite3.connect('wuzari_v2.db')
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
    
    # إضافة بيانات تجريبية متكاملة تشمل الأدوار المختلفة
    cursor.execute("SELECT COUNT(*) FROM questions")
    if cursor.fetchone()[0] == 0:
        sample_data = [
            ("السادس الاحيائي", "كيمياء", "2018", "الدور الاول", "الفصل الثاني", "ما تأثير تغير الضغط على تفاعل متزن يعادل فيه عدد مولات الغازات؟ وضّح وفق قاعدة لوشاتيليه.", "https://example.com/sol1.pdf"),
            ("السادس الاحيائي", "كيمياء", "2018", "الدور الثاني", "الفصل الأول", "احسب قيمة المسعر الحراري للتفاعل التالي...", "https://example.com/sol2.pdf"),
            ("السادس الاحيائي", "كيمياء", "2019", "التمهيدي", "الفصل الثالث", "ما هي ذوبانية ملح كبريتات الباريوم؟", "https://example.com/sol3.pdf"),
            ("الثالث المتوسط", "رياضيات", "2018", "الدور الثالث", "الفصل الاول", "حل المتباينة المركبة التالية ومثل الحل على خط الأعداد...", "https://example.com/sol4.pdf")
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
    conn = sqlite3.connect('wuzari_v2.db')
    cursor = conn.cursor()
    cursor.execute(sql, params)
    results = cursor.fetchall()
    conn.close()
    return results

# --- واجهة المستخدم (Streamlit UI) ---
st.title("📚 تصفح الأرشيف الوزاري")
st.write("اختر المرحلة، المادة، السنة، والدور للوصول إلى الأجوبة النموذجية.")

tab1, tab2 = st.tabs(["📂 تصفح حسب الفلاتر", "🔍 البحث الذكي المباشر"])

# --- التبويب الأول: التصفح المنظم والمعدل ---
with tab1:
    # تقسيم الخيارات إلى 4 أعمدة متناسقة لتشمل (المرحلة، المادة، السنة، الدور)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        branch_choice = st.selectbox(
            "اختر المرحلة / الفرع:", 
            ["السادس الاحيائي", "السادس التطبيقي", "السادس الادبي", "السادس الابتدائي", "الثالث المتوسط"]
        )
        
    with col2:
        if "السادس" in branch_choice and "الابتدائي" not in branch_choice:
            if branch_choice == "السادس الادبي":
                subjects = ["تاريخ", "جغرافيا", "اقتصاد", "عربي", "انكليزي", "رياضيات", "اسلامية"]
            else:
                subjects = ["كيمياء", "فيزياء", "احياء", "رياضيات", "عربي", "اسلامية", "انكليزي"]
        elif branch_choice == "الثالث المتوسط":
            subjects = ["رياضيات", "كيمياء", "فيزياء", "احياء", "عربي", "انكليزي", "اسلامية", "اجتماعيات"]
        else:
            subjects = ["رياضيات", "علوم", "عربي", "انكليزي", "اسلامية", "اجتماعيات"]
            
        subject_choice = st.selectbox("اختر المادة:", subjects)
        
    with col3:
        year_choice = st.selectbox("السنة:", ["الكل", "2024", "2023", "2022", "2021", "2019", "2018"])
        
    with col4:
        # إضافة فلتر الأدوار المطلبوبة
        role_choice = st.selectbox("الدور:", ["الكل", "الدور الاول", "الدور الثاني", "الدور الثالث", "التمهيدي"])

    # بناء الاستعلام بناءً على الفلاتر المختارة ديناميكياً
    sql = "SELECT year, role, chapter, question_text, answer_path FROM questions WHERE branch = ? AND subject = ?"
    params = [branch_choice, subject_choice]
    
    if year_choice != "الكل":
        sql += " AND year = ?"
        params.append(year_choice)
        
    if role_choice != "الكل":
        sql += " AND role = ?"
        params.append(role_choice)
        
    results = query_db(sql, tuple(params))
    
    # عرض النتائج
    st.write("---")
    if results:
        st.success(f"تم العثور على {len(results)} سؤال وزاري مطابِق لخياراتك:")
        for res in results:
            with st.container():
                st.info(f"📅 السنة: {res[0]} | 🛑 {res[1]} | 📖 {res[2]}")
                st.write(f"**السؤال:** {res[3]}")
                st.markdown(f"[📥 تحميل الحل النموذجي المعتمد (PDF)]({res[4]})")
                st.write("---")
    else:
        st.warning("⚠️ لا توجد أسئلة مضافة تطابق هذا التحديد حالياً في قاعدة البيانات.")

# --- التبويب الثاني: محرك البحث ---
with tab2:
    st.subheader("ابحث بكلمة مفتاحية في كل الوزاريات")
    search_query = st.text_input("اكتب كلمة مفتاحية (مثال: دي موافر، متسعة، لوشاتيليه):")
    
    if search_query:
        sql_search = "SELECT branch, subject, year, role, chapter, question_text, answer_path FROM questions WHERE question_text LIKE ?"
        search_results = query_db(sql_search, (f'%{search_query}%',))
        
        if search_results:
            for res in search_results:
                with st.expander(f"📍 {res[0]} | {res[1]} - {res[2]} ({res[3]})"):
                    st.write(f"**السؤال:** {res[5]}")
                    st.markdown(f"[🔗 رابط الحل النموذجي]({res[6]})")
        else:
            st.write("❌ لم يتم العثور على نتائج.")
