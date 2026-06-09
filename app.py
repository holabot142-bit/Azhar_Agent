import streamlit as st
from groq import Groq
from pypdf import PdfReader
from gtts import gTTS
import io

# 1. جلب مفتاح Groq بأمان من ملف الأسرار (يعمل محلياً أو سحابياً على الاستضافة)
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error("🔒 خطأ: لم يتم العثور على مفتاح Groq الآمن. تأكد من إضافته في Secrets على منصة الاستضافة أو في ملف .streamlit/secrets.toml محلياً.")
    st.stop()

# إعداد عميل Groq للاتصال بالسيرفرات الصاروخية
client = Groq(api_key=GROQ_API_KEY)

# 2. إعدادات واجهة التطبيق لتكون متناسقة ومريحة للعين
st.set_page_config(page_title="وكيل الأزهريين", page_icon="🕌", layout="centered")

# التوجيهات النظامية الصارمة (System Instruction) لتوجيه نموذج GPT OSS 120B المستقل والخارق
SYSTEM_PROMPT = """
أنت الآن "وكيل الأزهريين" (Deputy of Al-Azhar)، خبير تعليمي ومدرس متمكن متخصص في مناهج ومواد الأزهر الشريف بالكامل.
- مهمتك: مساعدة الطلاب والمعلمين بناءً على النصوص المرفوعة من كتب المعهد المرفقة.
- في العلوم الشرعية والعربية (فقه، توحيد، نحو، إلخ): التزم بالدقة الفقهية والمصطلحات التراثية المعتمدة مع تبسيط الشرح وذكر الأدلة من القرآن والسنة.
- في المواد العلمية (رياضيات، فيزياء، كيمياء): قم بحل المسائل خطوة بخطوة مع توضيح القوانين المستخرجة بدقة.
- طريقة العرض: استخدم التنسيق المنظم (Markdown)، البولد للعناوين، والنقاط ليكون النص مريحاً وممتعاً للقراءة وسهلاً للحفظ.
"""

# دالة استدعاء الموديل المستقل عبر Groq وسحب الإجابة في أجزاء من الثانية
def get_groq_answer(user_query, text_context, user_mode, model_name="gpt-oss-120b"):
    # دمج وضع الحساب، السياق، والسؤال في نص واحد منظم يذهب للموديل
    full_user_message = f"[بوابة الاستخدام الحالية: {user_mode}]\n\nنص كتاب المعهد المرفوع:\n{text_context}\n\nطلب المستخدم وسؤاله:\n{user_query}"
    
    completion = client.chat.completions.create(
        model=model_name, # استخدام النموذج المستقل والذكي المتواجد في حسابك
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": full_user_message}
        ],
        temperature=0.4, # حرارة منخفضة لضمان الالتزام بالنص الفقهي والعلمي وعدم التأليف والهلوسة
    )
    return completion.choices[0].message.content

# دالة قراءة الـ PDF الفعلي واستخراج النصوص منه صفحة تلو الأخرى
def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    extracted_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            extracted_text += text + "\n"
    return extracted_text

# دالة توليد المشغل الصوتي المسموع (TTS) لمنع الملل ومساعدة الطالب على الاستماع لشرح المادة
def text_to_speech_player(text_to_speak):
    try:
        # تحويل النص المستلم إلى صوت ناطق باللغة العربية الفصحى المبسطة
        tts = gTTS(text=text_to_speak, lang='ar', slow=False)
        
        # حفظ الملف الصوتي مؤقتاً في ذاكرة الرام دون استهلاك مساحة جهاز الطالب
        sound_file = io.BytesIO()
        tts.write_to_fp(sound_file)
        
        # عرض مشغل الصوت الأنيق في الواجهة
        st.audio(sound_file, format='audio/mp3')
    except Exception as e:
        st.warning("⚠️ لم نتمكن من تشغيل الصوت التلقائي حالياً، يمكنك قراءة النص المكتوب.")

# --- تصميم واجهة المستخدم (Streamlit UI) ---

# العنوان الرئيسي الأنيق
st.markdown("<h1 style='text-align: center; color: #1e4620;'>🕌 وكيل الأزهريين الذكي</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #555; font-weight: bold;'>Deputy of Al-Azhar</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #777;'>مبادرة خيرية لخدمة طلاب ومدرسي الأزهر الشريف عبر نموذج التفكير المنطقي GPT OSS 120B</p>", unsafe_allow_html=True)
st.write("---")

# القائمة الجانبية لتحديد الحساب وضمان الأمان
with st.sidebar:
    st.markdown("<h3 style='text-align: center; color: #1e4620;'>🔐 بوابة التحكم</h3>", unsafe_allow_html=True)
    user_mode = st.selectbox("اختر نوع الحساب للدخول:", ["👤 بوابة الطالب الأزهري", "👨‍🏫 بوابة معلم أزهري"])
    st.write("---")
    st.success("الوكيل متصل بنموذج GPT OSS 120B المفتوح 🔓")

# صندوق رفع ملف كتاب المعهد (PDF)
uploaded_file = st.file_uploader("ارفع كتاب المعهد، المذكرة الرسمية، أو منهج المادة (PDF):", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("📄 jاري قراءة وتحليل صفحات كتاب المعهد بدقة..."):
        book_context = extract_text_from_pdf(uploaded_file)
    st.toast("تمت قراءة الكتاب وحفظ سياق المادة بنجاح! 🎉")
else:
    book_context = ""

# --- تشغيل وتخصيص البوابات بناءً على نوع الحساب المختار ---

if user_mode == "👤 بوابة الطالب الأزهري":
    st.subheader("📚 رفيـقك الذكي للمذاكـرة وتوقعـات البوكلـيت")
    student_query = st.text_input("اكتب سؤالك، أو النقطة الصعبة التي لا تفهمها في هذا الدرس:")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💡 اشرح لي الدرس ببساطة"):
            if book_context and student_query:
                with st.spinner("🤖 الوكيل يكتب لك الشرح والتوضيح الفوري..."):
                    reply = get_groq_answer(f"اشرح لي ببساطة الدرس وأجب عن هذا السؤال بالتفصيل: {student_query}", book_context, user_mode)
                    
                    # عرض الإجابة المكتوبة
                    st.success(reply)
                    
                    # تشغيل الميزة الصوتية لقراءة الإجابة للطالب
                    st.markdown("### 🎧 استمع إلى الشرح الصوتي للوكيل:")
                    text_to_speech_player(reply)
            else:
                st.warning("رجاءً ارفع كتاب الـ PDF أولاً واكتب سؤالك في الصندوق.")
                
    with col2:
        if st.button("📝 توليد أسئلة بوكليت متوقعة"):
            if book_context:
                with st.spinner("🤖 جاري استخراج وصياغة أسئلة امتحانات أزهرية..."):
                    reply = get_groq_answer("استخرج من هذا النص 3 أسئلة امتحانات متوقعة بنظام البوكليت الأزهري الرسمي (مثل: ما الحكم مع التعليل، علل لما يأتي، اذكر الدليل) متبوعة بالإجابات النموذجية لكل سؤال.", book_context, user_mode)
                    
                    # عرض الأسئلة المكتوبة
                    st.info(reply)
                    
                    # تشغيل الميزة الصوتية لقراءة الأسئلة للطالب للحفظ والاستماع
                    st.markdown("### 🎧 استمع إلى الأسئلة المتوقعة:")
                    text_to_speech_player(reply)
            else:
                st.warning("رجاءً ارفع ملف الـ PDF أولاً لتوليد أسئلة الامتحان منه.")

elif user_mode == "👨‍🏫 بوابة معلم أزهري":
    st.subheader("👨‍🏫 مساعدك التربوي لتنظيم المنهج وبنوك الأسئلة")
    teacher_query = st.text_input("ما الدرس أو الجزئية التي ترغب في تحضيرها وتوزيعها اليوم يا مولانا؟")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗺️ وضع خطة تحضير وتوزيع للدرس"):
            if book_context:
                with st.spinner("🤖 جاري صياغة خطة التحضير التربوية النموذجية..."):
                    reply = get_groq_answer("قم بعمل تحضير دراسي نموذجي تربوي مفصل لهذا النص يحتوي على الأهداف الثلاثة (معرفية، وجدانية، مهارية)، واقترح وسيلة أو فكرة مبتكرة ومبسطة لتوصيل المعلومة للطلاب.", book_context, user_mode)
                    
                    # عرض التحضير المكتوب للمعلم
                    st.success(reply)
                    
                    # تشغيل الصوت لكي يستمع المعلم للتحضير أثناء انشغاله
                    st.markdown("### 🎧 استمع إلى التحضير الصوتي:")
                    text_to_speech_player(reply)
            else:
                st.warning("رجاءً ارفع ملف نص المنهج بصيغة PDF أولاً.")
                
    with col2:
        if st.button("🔍 ابتكار اختبار شهري للمادة"):
            if book_context:
                with st.spinner("🤖 جاري إنشاء أسئلة الاختبار الشامل..."):
                    reply = get_groq_answer("اصنع لي اختباراً شهرياً مفاجئاً ومنوعاً لتقييم استيعاب وفهم الطلاب لهذا النص، على أن يكون مقسماً إلى أسئلة مقالية موضوعية وأسئلة اختيارية مع كتابة نموذج الإجابة ومفتاح الحل لكل سؤال.", book_context, user_mode)
                    
                    # عرض الاختبار المكتوب
                    st.info(reply)
                    
                    # قراءة الاختبار صوتياً
                    st.markdown("### 🎧 استمع إلى بنك الأسئلة:")
                    text_to_speech_player(reply)
            else:
                st.warning("رجاءً ارفع ملف المنهج أولاً لصياغة الاختبار منه.")
    
