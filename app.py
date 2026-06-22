import streamlit as st
import sqlite3
import os

# --- إعدادات الصفحة ---
st.set_page_config(page_title="وزاريات السادس العلمي", page_icon="📚", layout="centered")

# --- الاتصال بقاعدة البيانات وإنشاء الجداول ---
def init_db():
    conn = sqlite3.connect('wuzari.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT,
        year TEXT,
        role TEXT,
        chapter TEXT,
        question_text TEXT,
        answer_path TEXT
    )
    ''')
    
    # إضافة بيانات تجريبية إذا كانت قاعدة البيانات فارغة تماماً
    cursor.execute("SELECT COUNT(*) FROM questions")
    if cursor.fetchone()[0] == 0:
        sample_data = [
            ("كيمياء", "2023", "الدور الأول", "الفصل الثاني", "ما تأثير تغير الضغط على تفاعل متزن يعادل فيه عدد مولات الغازات؟ وضّح وفق قاعدة لوشاتيليه.", "https://example.com/chem_sol.pdf"),
            ("فيزياء", "2024", "التمهيدي", "الفصل الأول", "متسعة ذات الصفيحتين المتوازيتين مشحونة ومفصولة عن المصدر، ماذا يحصل لشحنتها وفرق الجهد عند إدخال عازل؟", "https://example.com/phys_sol.pdf"),
            ("رياضيات", "2023", "الدور الثاني", "الفصل الأول", "جد الجذور التربيعية للعدد المركب c = -8i باستخدام نتيجة مبرهنة دي موافر.", "https://example.com/math_sol.pdf")
        ]
        cursor.executemany('''
        INSERT INTO questions (subject, year, role, chapter, question_text, answer_path)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', sample_data)
        conn.commit()
    conn.close()

init_db()

# --- دالات الاستعلام من قاعدة البيانات ---
def query_db(sql, params=()):
    conn = sqlite3.connect('wuzari.db')
    cursor = conn.cursor()
    cursor.execute(sql, params)
    results = cursor.fetchall()
    conn.close()
    return results

# --- واجهة المستخدم (Streamlit UI) ---
st.title("📚 منصة وزاريات السادس العلمي")
st.write("أهلاً بك يا بطل، هنا تجد كل الأسئلة الوزارية مع حلولها النموذجية لكل المواد.")

# تصميم التبويبات (Tabs) لفصل محرك البحث عن التصفح العادي
tab1, tab2 = st.tabs(["🔍 البحث الذكي", "📂 تصفح حسب المواد"])

# --- التبويب الأول: محرك البحث ---
with tab1:
    st.subheader("ابحث عن أي فكرة أو سؤال وزاري")
    search_query = st.text_input("اكتب كلمة مفتاحية (مثلاً: لوشاتيليه، دي موافر، متسعة):", placeholder="ابحث هنا...")
    
    if search_query:
        # البحث باستخدام LIKE في نصوص الأسئلة
        sql = "SELECT subject, year, role, chapter, question_text, answer_path FROM questions WHERE question_text LIKE ?"
        results = query_db(sql, (f'%{search_query}%',))
        
        if results:
            st.success(f"تم العثور على {len(results)} سؤال مرتبط بـ '{search_query}'")
            for res in results:
                with st.expander(f"📍 {res[0]} - {res[1]} ({res[2]}) | {res[3]}"):
                    st.write(f"**السؤال:** {res[4]}")
                    st.markdown(f"[🔗 اضغط هنا لمشاهدة الحل النموذجي]({res[5]})")
        else:
            st.warning("لم يتم العثور على أسئلة تحتوي هذه الكلمة. تأكد من الإملاء.")

# --- التبويب الثاني: التصفح المنظم ---
with tab2:
    st.subheader("اختر المادة والتفاصيل لعرض الأسئلة")
    
    col1, col2 = st.columns(2)
    with col1:
        subject_choice = st.selectbox("المادة:", ["كيمياء", "فيزياء", "احياء", "رياضيات", "عربي", "اسلامية", "انكليزي"])
    with col2:
        # جلب الفصول المتاحة لهذه المادة ديناميكياً من قاعدة البيانات
        chapters_available = query_db("SELECT DISTINCT chapter FROM questions WHERE subject = ?", (subject_choice,))
        chapters_list = [ch[0] for ch in chapters_available] if chapters_available else ["كل الفصول"]
        chapter_choice = st.selectbox("الفصل:", ["الكل"] + chapters_list)

    # بناء الاستعلام بناءً على خيارات المستخدم
    if chapter_choice == "الكل":
        sql = "SELECT year, role, chapter, question_text, answer_path FROM questions WHERE subject = ?"
        params = (subject_choice,)
    else:
        sql = "SELECT year, role, chapter, question_text, answer_path FROM questions WHERE subject = ? AND chapter = ?"
        params = (subject_choice, chapter_choice)
        
    results = query_db(sql, params)
    
    if results:
        for res in results:
            st.info(f"📅 السنة: {res[0]} | {res[1]} | {res[2]}")
            st.write(f"**السؤال:** {res[3]}")
            st.markdown(f"[📥 تحميل الحل النموذجي (PDF)]({res[4]})")
            st.write("---")
    else:
        st.write("⚠️ لا توجد أسئلة مضافة لهذه المادة أو الفصل حالياً.")
