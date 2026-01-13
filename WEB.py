import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random
import io
import uuid
import time
import base64
from gtts import gTTS

# --- THƯ VIỆN MỚI CHO TÍNH NĂNG 4 ---
try:
    import speech_recognition as sr
    from streamlit_mic_recorder import mic_recorder
except ImportError:
    st.error("⚠️ Thiếu thư viện! Vui lòng chạy: pip install SpeechRecognition streamlit-mic-recorder")
    st.stop()

# ==================== CẤU HÌNH ====================
JSON_FILE = 'credentials.json'
FILE_ID = '1xWdc8hmymvKn4bPzi8-YEy5hd_cVXdq22dVnwzB4Id0' 
COL_ENG = 'Từ vựng'
COL_VIE = 'Nghĩa'
AUTHOR = "Thanh Xuân"

st.set_page_config(page_title=f"Vocab Master - {AUTHOR}", page_icon="🌸", layout="centered")

# --- CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #FFF0F5; }
    div[data-testid="stVerticalBlock"] { opacity: 1 !important; transition: none !important; }
    .element-container { opacity: 1 !important; transition: none !important; }
    div[data-testid="stStatusWidget"] { visibility: hidden; }

    .main-title { font-size: 30px !important; font-weight: 800 !important; color: #C71585 !important; text-align: center; margin-bottom: 5px; }
    .main-card { background-color: #ffffff; padding: 20px; border-radius: 20px; text-align: center; box-shadow: 0 5px 15px rgba(0,0,0,0.05); border-top: 8px solid #FFB6C1; margin-bottom: 20px; }
    
    div.stButton > button { 
        height: 3.2em !important; font-size: 22px !important; 
        border-radius: 12px !important; font-weight: 600 !important; 
        background-color: #ffffff; border: 2px solid #FFB6C1 !important; 
        color: #C71585 !important; width: 100%; margin-bottom: 8px;
        transition: transform 0.1s;
    }
    div.stButton > button:hover { background-color: #FFB6C1 !important; color: white !important; }
    div.stButton > button:active { transform: scale(0.96); }
    
    .author-text { text-align: center; color: #C71585; font-size: 0.9em; margin-top: 20px; opacity: 0.7; }
    
    /* Style cho kết quả luyện nói */
    .speech-result-success { color: green; font-weight: bold; font-size: 1.2em; text-align: center; }
    .speech-result-fail { color: red; font-weight: bold; font-size: 1.2em; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- HÀM HỖ TRỢ ---
def get_audio_base64(text):
    if not text: return None
    try:
        tts = gTTS(text=text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        return f"data:audio/mp3;base64,{b64}"
    except: return None

# Hàm xử lý nhận diện giọng nói (Feature 4)
def recognize_speech(audio_bytes):
    r = sr.Recognizer()
    try:
        audio_file = io.BytesIO(audio_bytes)
        with sr.AudioFile(audio_file) as source:
            audio_data = r.record(source)
            # Dùng Google Speech API (miễn phí, có giới hạn nhưng đủ dùng cho học tập)
            text = r.recognize_google(audio_data, language="en-US")
            return text.lower()
    except sr.UnknownValueError:
        return "kém_chất_lượng"  # Không nghe rõ
    except Exception as e:
        return f"lỗi: {str(e)}"

@st.cache_resource(ttl=60)
def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_FILE, scope)
    return gspread.authorize(creds)

def load_data():
    try:
        client = get_gspread_client()
        spreadsheet = client.open_by_key(FILE_ID)
        # Tự động lấy sheet đang chọn hoặc sheet đầu tiên
        sheet_name = st.session_state.get('selected_sheet_name')
        if sheet_name:
            ws = spreadsheet.worksheet(sheet_name)
        else:
            ws = spreadsheet.get_worksheet(0)
        
        records = ws.get_all_records()
        return [r for r in records if r.get(COL_ENG) and r.get(COL_VIE)]
    except: return []

# --- STATE MANAGEMENT ---
if 'score' not in st.session_state: st.session_state.score = 0
if 'total' not in st.session_state: st.session_state.total = 0
if 'quiz' not in st.session_state: st.session_state.quiz = None
if 'last_q' not in st.session_state: st.session_state.last_q = None
if 'current_audio_b64' not in st.session_state: st.session_state.current_audio_b64 = None 
if 'last_result_msg' not in st.session_state: st.session_state.last_result_msg = None
# Feature 2: Theo dõi từ sai
if 'mistakes' not in st.session_state: st.session_state.mistakes = {} 

# --- SIDEBAR ---
client = get_gspread_client() # Lấy client để load danh sách sheet
try:
    spreadsheet = client.open_by_key(FILE_ID)
    sheet_names = [ws.title for ws in spreadsheet.worksheets()]
except:
    sheet_names = []

with st.sidebar:
    st.title("⚙️ Cài đặt")
    if sheet_names:
        # Khi đổi sheet, reset quiz
        new_sheet = st.selectbox("Chủ đề:", sheet_names)
        if new_sheet != st.session_state.get('selected_sheet_name'):
            st.session_state.selected_sheet_name = new_sheet
            st.session_state.quiz = None
            st.rerun()
    else:
        st.error("Lỗi kết nối Sheet!"); st.stop()

    # Thêm chế độ mới cho Feature 4
    st.session_state.mode = st.radio("Chế độ:", ["Anh ➔ Việt", "Việt ➔ Anh", "🗣️ Luyện Phát Âm (Beta)"])
    
    # Feature 2: Toggle
    use_smart_review = st.checkbox("🧠 Ôn tập thông minh", value=True, help="Ưu tiên xuất hiện lại các từ bạn hay làm sai.")

    if st.button("Reset điểm & Dữ liệu sai"):
        st.session_state.score = 0
        st.session_state.total = 0
        st.session_state.mistakes = {} # Reset bộ nhớ thông minh
        st.rerun()
    
    if st.session_state.mistakes:
        st.caption(f"📝 Đã ghi nhớ {len(st.session_state.mistakes)} từ khó.")

data = load_data()

# --- LOGIC ---
def generate_new_question():
    if len(data) < 2: return
    
    # --- LOGIC FEATURE 2: SMART REVIEW ---
    if use_smart_review and st.session_state.mistakes:
        # Tính trọng số: Từ sai nhiều có trọng số cao hơn
        weights = []
        for d in data:
            word = d[COL_ENG]
            mistake_count = st.session_state.mistakes.get(word, 0)
            # Công thức: Mặc định 1 + (số lần sai * 10) -> Sai 1 lần thì khả năng gặp lại gấp 11 lần
            weights.append(1 + mistake_count * 10)
        
        # Chọn ngẫu nhiên dựa trên trọng số (Weighted Random)
        target = random.choices(data, weights=weights, k=1)[0]
        
        # Tránh lặp lại câu hỏi vừa xong nếu có thể
        if target[COL_ENG] == st.session_state.last_q and len(data) > 5:
             target = random.choices(data, weights=weights, k=1)[0]
    else:
        # Chế độ ngẫu nhiên thường
        available = [d for d in data if d[COL_ENG] != st.session_state.last_q]
        target = random.choice(available if available else data)

    others = random.sample([d for d in data if d != target], min(3, len(data)-1))
    
    # Setup cho chế độ trắc nghiệm
    if st.session_state.mode == "Anh ➔ Việt":
        q, a = target[COL_ENG], target[COL_VIE]
        opts = [d[COL_VIE] for d in others] + [a]
    elif st.session_state.mode == "Việt ➔ Anh":
        q, a = target[COL_VIE], target[COL_ENG]
        opts = [d[COL_ENG] for d in others] + [a]
    else: 
        # Chế độ Luyện Phát Âm
        q, a = target[COL_ENG], target[COL_VIE] # Hiện tiếng Anh
        opts = [] # Không cần options

    if st.session_state.mode != "🗣️ Luyện Phát Âm (Beta)":
        random.shuffle(opts)
        
    st.session_state.quiz = {'q': q, 'a': a, 'opts': opts, 'raw_en': target[COL_ENG], 'raw_vn': target[COL_VIE]}
    st.session_state.last_q = target[COL_ENG]
    st.session_state.current_audio_b64 = get_audio_base64(target[COL_ENG])
    # Reset biến cho Luyện Nói
    st.session_state.speech_feedback = None 

def handle_answer(selected_opt):
    quiz = st.session_state.quiz
    st.session_state.total += 1
    
    target_word = quiz['raw_en']
    
    if selected_opt == quiz['a']:
        st.session_state.score += 1
        st.session_state.last_result_msg = ("success", "🎉 Chính xác!")
        # Nếu trả lời đúng, giảm "độ khó" của từ này trong bộ nhớ (nếu có)
        if target_word in st.session_state.mistakes:
            st.session_state.mistakes[target_word] = max(0, st.session_state.mistakes[target_word] - 1)
            if st.session_state.mistakes[target_word] == 0:
                del st.session_state.mistakes[target_word]
    else:
        st.session_state.last_result_msg = ("error", f"❌ Sai rồi! Đáp án là: {quiz['a']}")
        # FEATURE 2: Ghi nhận lỗi sai
        st.session_state.mistakes[target_word] = st.session_state.mistakes.get(target_word, 0) + 1
        
    generate_new_question()

# --- GIAO DIỆN FRAGMENT ---
st.markdown(f'<h1 class="main-title">🌸 Học gói từ vựng {st.session_state.selected_sheet_name}</h1>', unsafe_allow_html=True)

@st.fragment
def show_quiz_area():
    if not data:
        st.warning("Sheet này chưa có từ vựng!")
        return

    if st.session_state.quiz is None:
        generate_new_question()
        st.rerun()

    quiz = st.session_state.quiz
    
    # Hiển thị thông báo (Toast style)
    if st.session_state.last_result_msg:
        mstype, msg = st.session_state.last_result_msg
        if mstype == "success": st.success(msg, icon="✅")
        else: st.error(msg, icon="⚠️")
        st.session_state.last_result_msg = None

    # Card hiển thị từ vựng
    st.markdown(f'<div class="main-card"><h1 style="color: #333; font-size: 2.8em; margin: 0;">{quiz["q"]}</h1></div>', unsafe_allow_html=True)
    
    # Audio Player (Chỉ hiện ở chế độ trắc nghiệm hoặc gợi ý)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.session_state.get('current_audio_b64'):
            unique_id = f"audio_{uuid.uuid4()}"
            audio_html = f"""
                <div id="container_{unique_id}">
                    <audio id="{unique_id}" controls autoplay style="width: 100%;">
                        <source src="{st.session_state.current_audio_b64}" type="audio/mp3">
                    </audio>
                </div>
                <script>
                    var audio = document.getElementById("{unique_id}");
                    if (audio) {{ audio.load(); audio.play().catch(e => console.log(e)); }}
                </script>
            """
            st.components.v1.html(audio_html, height=50)

    # --- CHIA GIAO DIỆN THEO CHẾ ĐỘ ---
    
    # 1. GIAO DIỆN LUYỆN NÓI (FEATURE 4)
    if st.session_state.mode == "🗣️ Luyện Phát Âm (Beta)":
        st.markdown(f"<div style='text-align:center; margin-bottom:10px'>Hãy đọc to từ: <b>{quiz['raw_en']}</b></div>", unsafe_allow_html=True)
        
        # Cột canh giữa cho nút Mic
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            # Thu âm: trả về định dạng wav để xử lý dễ nhất
            audio = mic_recorder(start_prompt="🎙️ Bấm để nói", stop_prompt="⏹️ Dừng", key=f"mic_{quiz['raw_en']}", format="wav")
            
        if audio:
            # Xử lý khi có file ghi âm
            with st.spinner("Đang nghe..."):
                spoken_text = recognize_speech(audio['bytes'])
            
            target_word = quiz['raw_en'].lower().strip()
            
            if spoken_text == "kém_chất_lượng":
                st.warning("🙉 Không nghe rõ, bạn thử lại nhé!")
            elif spoken_text.startswith("lỗi"):
                st.error(f"Lỗi kỹ thuật: {spoken_text}")
            else:
                st.write(f"Bạn nói: **{spoken_text}**")
                # So sánh (chấp nhận sai lệch nhỏ nếu cần, ở đây so sánh chính xác)
                if spoken_text == target_word:
                    st.markdown('<div class="speech-result-success">🎯 Tuyệt vời! Chính xác 100%</div>', unsafe_allow_html=True)
                    st.balloons()
                    time.sleep(1.5)
                    generate_new_question() # Tự động qua câu mới
                    st.rerun()
                else:
                     st.markdown(f'<div class="speech-result-fail">😅 Gần đúng rồi! (Target: {target_word})</div>', unsafe_allow_html=True)

        if st.button("Bỏ qua từ này ➡️"):
            generate_new_question()
            st.rerun()

    # 2. GIAO DIỆN TRẮC NGHIỆM (CŨ)
    else:
        for opt in quiz['opts']:
            st.button(opt, key=f"btn_{uuid.uuid4()}", on_click=handle_answer, args=(opt,), use_container_width=True)

        # Thanh điểm số
        score_val = st.session_state.score / (st.session_state.total if st.session_state.total > 0 else 1)
        st.progress(score_val)
        st.caption(f"Điểm số: **{st.session_state.score} / {st.session_state.total}**")

show_quiz_area()
st.markdown(f'<div class="author-text">Made by {AUTHOR} 🌸</div>', unsafe_allow_html=True)