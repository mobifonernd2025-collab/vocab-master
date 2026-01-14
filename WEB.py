import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random
import io
import uuid
import time
import base64
from gtts import gTTS

# --- KIỂM TRA THƯ VIỆN LUYỆN NÓI ---
try:
    import speech_recognition as sr
    from streamlit_mic_recorder import mic_recorder
except ImportError:
    st.error("⚠️ Thiếu thư viện! Vui lòng chạy: pip install SpeechRecognition streamlit-mic-recorder")
    st.stop()

# ==================== CẤU HÌNH ====================
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
    
    .main-card { 
        background-color: #ffffff; 
        padding: 15px; 
        border-radius: 20px; 
        text-align: center; 
        box-shadow: 0 5px 15px rgba(0,0,0,0.05); 
        border-top: 8px solid #FFB6C1; 
        margin-bottom: 20px; 
    }
    
    div[data-testid="stAlert"] {
        font-size: 1.3rem !important; 
        font-weight: 700 !important;
        padding: 1rem !important;
    }

    /* Style nút chung */
    div.stButton > button { 
        height: 3.2em !important; font-size: 22px !important; 
        border-radius: 12px !important; font-weight: 600 !important; 
        background-color: #ffffff; border: 2px solid #FFB6C1 !important; 
        color: #C71585 !important; width: 100%; margin-bottom: 8px;
        transition: transform 0.1s;
        -webkit-tap-highlight-color: transparent; 
        outline: none !important;
    }

    @media (hover: hover) {
        div.stButton > button:hover { background-color: #FFB6C1 !important; color: white !important; }
    }

    @media (hover: none) {
        div.stButton > button:hover, 
        div.stButton > button:focus { 
            background-color: #ffffff !important; 
            color: #C71585 !important; 
            border-color: #FFB6C1 !important;
            box-shadow: none !important;
        }
        div.stButton > button:active { 
            background-color: #FFB6C1 !important; 
            color: white !important; 
            transform: scale(0.96); 
        }
    }
    
    /* Style cho Combo */
    .combo-text {
        text-align: center;
        font-size: 1.2em;
        font-weight: bold;
        color: #FF4500;
        margin-bottom: 10px;
        animation: pulse 0.5s infinite alternate;
    }

    .author-text { text-align: center; color: #C71585; font-size: 0.9em; margin-top: 20px; opacity: 0.7; }
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

def recognize_speech(audio_bytes):
    r = sr.Recognizer()
    try:
        audio_file = io.BytesIO(audio_bytes)
        with sr.AudioFile(audio_file) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data, language="en-US")
            return text.lower()
    except: return "kém_chất_lượng"

@st.cache_resource(ttl=60)
def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        key_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Lỗi kết nối: {e}")
        return None

def load_data():
    try:
        client = get_gspread_client()
        if not client: return []
        spreadsheet = client.open_by_key(FILE_ID)
        sheet_name = st.session_state.get('selected_sheet_name')
        if sheet_name: ws = spreadsheet.worksheet(sheet_name)
        else: ws = spreadsheet.get_worksheet(0)
        return [r for r in ws.get_all_records() if r.get(COL_ENG) and r.get(COL_VIE)]
    except: return []

# --- QUẢN LÝ TRẠNG THÁI ---
if 'score' not in st.session_state: st.session_state.score = 0
if 'total' not in st.session_state: st.session_state.total = 0
if 'quiz' not in st.session_state: st.session_state.quiz = None
if 'current_audio_b64' not in st.session_state: st.session_state.current_audio_b64 = None 
if 'last_result_msg' not in st.session_state: st.session_state.last_result_msg = None
if 'word_weights' not in st.session_state: st.session_state.word_weights = {} 
if 'recent_history' not in st.session_state: st.session_state.recent_history = [] 
if 'start_time' not in st.session_state: st.session_state.start_time = 0 
if 'mode' not in st.session_state: st.session_state.mode = "Anh ➔ Việt" 
if 'last_audio_bytes' not in st.session_state: st.session_state.last_audio_bytes = None
# BIẾN MỚI: Combo
if 'combo' not in st.session_state: st.session_state.combo = 0

def reset_quiz():
    st.session_state.quiz = None
    st.session_state.last_result_msg = None
    st.session_state.combo = 0 # Reset combo khi đổi chế độ

# --- SIDEBAR ---
client = get_gspread_client()
try:
    if client:
        spreadsheet = client.open_by_key(FILE_ID)
        sheet_names = [ws.title for ws in spreadsheet.worksheets()]
    else: sheet_names = []
except: sheet_names = []

with st.sidebar:
    st.title("⚙️ Cài đặt")
    if sheet_names:
        new_sheet = st.selectbox("Chủ đề:", sheet_names)
        if new_sheet != st.session_state.get('selected_sheet_name'):
            st.session_state.selected_sheet_name = new_sheet
            reset_quiz() 
            st.session_state.recent_history = [] 
            st.rerun()
    
    st.radio("Chế độ:", ["Anh ➔ Việt", "Việt ➔ Anh", "🗣️ Luyện Phát Âm (Beta)"], key="mode", on_change=reset_quiz)
    
    # NÚT BẬT/TẮT AUDIO
    auto_play = st.toggle("🔊 Tự động phát âm", value=True)
    
    use_smart_review = st.checkbox("🧠 Ôn tập thông minh", value=True)
    
    if st.button("Reset điểm & Thuật toán"):
        st.session_state.score = 0
        st.session_state.total = 0
        st.session_state.word_weights = {} 
        st.session_state.recent_history = []
        st.session_state.last_audio_bytes = None
        st.session_state.combo = 0
        reset_quiz()
        st.rerun()

data = load_data()

# --- LOGIC ---
def generate_new_question():
    if len(data) < 2: return
    
    available_pool = data
    if len(data) > 8:
        available_pool = [d for d in data if d[COL_ENG] not in st.session_state.recent_history]
        if not available_pool: available_pool = data 

    target = None
    if use_smart_review:
        weights = [st.session_state.word_weights.get(d[COL_ENG], 10) for d in available_pool]
        target = random.choices(available_pool, weights=weights, k=1)[0]
    else:
        target = random.choice(available_pool)

    others = random.sample([d for d in data if d != target], min(3, len(data)-1))
    
    if st.session_state.mode == "Anh ➔ Việt":
        q, a = target[COL_ENG], target[COL_VIE]
        opts = [d[COL_VIE] for d in others] + [a]
    elif st.session_state.mode == "Việt ➔ Anh":
        q, a = target[COL_VIE], target[COL_ENG]
        opts = [d[COL_ENG] for d in others] + [a]
    else:
        q, a = target[COL_ENG], target[COL_VIE]
        opts = []

    if st.session_state.mode != "🗣️ Luyện Phát Âm (Beta)": random.shuffle(opts)
        
    st.session_state.quiz = {'q': q, 'a': a, 'opts': opts, 'raw_en': target[COL_ENG]}
    st.session_state.current_audio_b64 = get_audio_base64(target[COL_ENG])
    st.session_state.start_time = time.time()

def handle_answer(selected_opt):
    quiz = st.session_state.quiz
    target_word = quiz['raw_en']
    duration = time.time() - st.session_state.start_time
    st.session_state.total += 1
    current_weight = st.session_state.word_weights.get(target_word, 10)

    if selected_opt == quiz['a']:
        st.session_state.score += 1
        st.session_state.combo += 1 # Tăng combo
        
        # Thêm icon lửa vào thông báo nếu combo cao
        fire_icon = "🔥" * min(st.session_state.combo, 5) if st.session_state.combo > 1 else "🎉"
        st.session_state.last_result_msg = ("success", f"{fire_icon} Chính xác: {quiz['q']} - {quiz['a']}")
        
        if use_smart_review:
            if duration < 2.0: new_weight = max(1, current_weight - 3)
            elif duration > 3.5: new_weight = min(100, current_weight + 3)
            else: new_weight = max(1, current_weight - 1)
            st.session_state.word_weights[target_word] = new_weight
    else:
        st.session_state.combo = 0 # Reset combo
        st.session_state.last_result_msg = ("error", f"❌ Sai rồi: '{quiz['q']}' là '{quiz['a']}' chứ không phải '{selected_opt}'")
        st.session_state.word_weights[target_word] = min(100, current_weight + 10)

    st.session_state.recent_history.append(target_word)
    if len(st.session_state.recent_history) > 5:
        st.session_state.recent_history.pop(0)

    generate_new_question()

# --- GIAO DIỆN ---
st.markdown(f'<h1 class="main-title">🌸 {st.session_state.get("selected_sheet_name", "Loading...")}</h1>', unsafe_allow_html=True)

@st.fragment
def show_quiz_area():
    if not data: return
    if st.session_state.quiz is None:
        generate_new_question()
        st.rerun()

    quiz = st.session_state.quiz
    
    # HIỂN THỊ COMBO
    if st.session_state.combo > 1:
        st.markdown(f'<div class="combo-text">🔥 COMBO x{st.session_state.combo} 🔥</div>', unsafe_allow_html=True)
    
    if st.session_state.last_result_msg:
        mstype, msg = st.session_state.last_result_msg
        if mstype == "success": st.success(msg, icon="✅")
        else: st.error(msg, icon="⚠️")
        st.session_state.last_result_msg = None

    # Card Câu Hỏi
    st.markdown(f'<div class="main-card"><h1 style="color: #333; font-size: 1.8em; margin: 0;">{quiz["q"]}</h1></div>', unsafe_allow_html=True)
    
    # AUDIO VỚI TÙY CHỌN BẬT/TẮT
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.session_state.get('current_audio_b64'):
            unique_id = f"audio_{uuid.uuid4()}"
            # Nếu auto_play = True thì thêm thuộc tính autoplay, ngược lại thì không
            autoplay_attr = "autoplay" if auto_play else ""
            st.components.v1.html(f"""<audio id="{unique_id}" src="{st.session_state.current_audio_b64}" {autoplay_attr} controls style="width:100%"></audio>""", height=50)

    if st.session_state.mode == "🗣️ Luyện Phát Âm (Beta)":
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2: 
            audio = mic_recorder(start_prompt="🎙️ Bấm để nói", stop_prompt="⏹️ Dừng", key="static_mic_recorder", format="wav")
            
        if audio and audio['bytes'] != st.session_state.last_audio_bytes:
            st.session_state.last_audio_bytes = audio['bytes']
            spoken = recognize_speech(audio['bytes'])
            if spoken == quiz['raw_en'].lower().strip():
                st.session_state.combo += 1 # Tăng combo khi nói đúng
                st.balloons(); time.sleep(1); generate_new_question(); st.rerun()
            else: 
                st.session_state.combo = 0 # Reset combo khi nói sai
                st.error(f"Bạn nói: {spoken}")
            
        if st.button("Bỏ qua"): 
            st.session_state.combo = 0 # Bỏ qua cũng mất combo
            generate_new_question(); st.rerun()
    else:
        for opt in quiz['opts']: 
            st.button(opt, key=uuid.uuid4(), on_click=handle_answer, args=(opt,), use_container_width=True)
        
        # Thanh progress
        score_val = st.session_state.score / (st.session_state.total if st.session_state.total > 0 else 1)
        st.progress(score_val)
        
        # Thống kê nhỏ bên dưới
        c1, c2 = st.columns(2)
        with c1: st.caption(f"Điểm số: **{st.session_state.score}/{st.session_state.total}**")
        with c2: st.caption(f"Chuỗi đúng: **{st.session_state.combo}**")

show_quiz_area()
st.markdown(f'<div class="author-text">Made by {AUTHOR} 🌸</div>', unsafe_allow_html=True)
