import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random
import io
import uuid
import time
import base64
from gtts import gTTS

# --- KIỂM TRA THƯ VIỆN ---
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

# --- QUẢN LÝ THEME ---
if 'theme_mode' not in st.session_state: st.session_state.theme_mode = "Sakura (Hồng)"

if st.session_state.theme_mode == "Mint (Xanh Dịu)":
    THEME = {
        "bg": "#E0F7FA", "card_bg": "#ffffff", "text": "#00695C", "sub_text": "#00897B",
        "border": "#4DB6AC", "btn_bg": "#ffffff", "btn_hover": "#B2DFDB", "btn_text": "#00695C", "progress": "#009688"
    }
else:
    THEME = {
        "bg": "#FFF0F5", "card_bg": "#ffffff", "text": "#C71585", "sub_text": "#C71585",
        "border": "#FFB6C1", "btn_bg": "#ffffff", "btn_hover": "#FFB6C1", "btn_text": "#C71585", "progress": "#FF69B4"
    }

# --- CSS TỐI ƯU ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {THEME['bg']}; }}
    div[data-testid="stVerticalBlock"] {{ opacity: 1 !important; transition: none !important; gap: 0.5rem !important; }}
    .element-container {{ opacity: 1 !important; transition: none !important; }}
    div[data-testid="stStatusWidget"] {{ visibility: hidden; }}

    .main-title {{ font-size: 24px !important; font-weight: 800 !important; color: {THEME['text']} !important; text-align: center; margin-bottom: 0px; }}
    
    .main-card {{ 
        background-color: {THEME['card_bg']}; 
        padding: 10px; 
        border-radius: 15px; 
        text-align: center; 
        box-shadow: 0 2px 10px rgba(0,0,0,0.05); 
        border-top: 5px solid {THEME['border']}; 
        margin-bottom: 5px; 
        margin-top: 5px;
    }}
    
    .main-card h1 {{ color: {THEME['text']} !important; font-size: 1.8em !important; margin: 0 !important; }}

    div[data-testid="stAlert"] {{
        padding: 0.5rem 1rem !important;
        margin-bottom: 0.5rem !important;
        font-size: 1.1rem !important;
    }}

    div.stButton > button {{ 
        height: 3.2em !important; 
        font-size: 18px !important; 
        border-radius: 10px !important; font-weight: 600 !important; 
        background-color: {THEME['btn_bg']}; 
        border: 2px solid {THEME['border']} !important; 
        color: {THEME['btn_text']} !important; 
        width: 100%; margin-bottom: 5px;
        transition: transform 0.1s;
        -webkit-tap-highlight-color: transparent; 
        outline: none !important;
        white-space: normal !important;
        padding: 2px 5px !important;
    }}

    @media (hover: hover) {{
        div.stButton > button:hover {{ background-color: {THEME['btn_hover']} !important; color: {THEME['text']} !important; }}
    }}

    @media (hover: none) {{
        div.stButton > button:hover, div.stButton > button:focus {{ 
            background-color: {THEME['btn_bg']} !important; color: {THEME['btn_text']} !important; border-color: {THEME['border']} !important; box-shadow: none !important;
        }}
        div.stButton > button:active {{ background-color: {THEME['btn_hover']} !important; transform: scale(0.96); }}
    }}
    
    .combo-text {{ text-align: center; font-size: 1em; font-weight: bold; color: #FF4500; margin-bottom: 5px; animation: pulse 0.5s infinite alternate; }}
    .author-text {{ text-align: center; color: {THEME['sub_text']}; font-size: 0.8em; margin-top: 10px; opacity: 0.7; }}
    
    p, label {{ color: {THEME['text']} !important; margin-bottom: 0px !important; }}
    .stCaption {{ color: {THEME['sub_text']} !important; font-size: 0.9em !important; }}
    .stProgress > div > div > div > div {{ background-color: {THEME['progress']} !important; }}
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
if 'combo' not in st.session_state: st.session_state.combo = 0
if 'ignored_words' not in st.session_state: st.session_state.ignored_words = []

def reset_quiz():
    st.session_state.quiz = None
    st.session_state.last_result_msg = None
    st.session_state.combo = 0

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
    theme_choice = st.selectbox("Chọn màu:", ["Sakura (Hồng)", "Mint (Xanh Dịu)"], index=0 if st.session_state.theme_mode == "Sakura (Hồng)" else 1)
    if theme_choice != st.session_state.theme_mode:
        st.session_state.theme_mode = theme_choice
        st.rerun() 
    st.divider()
    if sheet_names:
        new_sheet = st.selectbox("Chủ đề:", sheet_names)
        if new_sheet != st.session_state.get('selected_sheet_name'):
            st.session_state.selected_sheet_name = new_sheet
            reset_quiz() 
            st.session_state.recent_history = [] 
            st.rerun()
    st.radio("Chế độ:", ["Anh ➔ Việt", "Việt ➔ Anh", "🗣️ Luyện Phát Âm (Beta)"], key="mode", on_change=reset_quiz)
    auto_play = st.toggle("🔊 Tự động phát âm", value=True)
    use_smart_review = st.checkbox("🧠 Ôn tập thông minh", value=True, help="Ưu tiên từ mới và từ bạn suy nghĩ lâu.")
    
    if st.button("Reset điểm & Thuật toán"):
        st.session_state.score = 0; st.session_state.total = 0; st.session_state.word_weights = {} 
        st.session_state.recent_history = []; st.session_state.last_audio_bytes = None; st.session_state.combo = 0
        st.session_state.ignored_words = []
        reset_quiz(); st.rerun()
        
    st.divider()
    st.markdown("""
        <div style='text-align: center; color: gray; font-size: 0.9em;'>
            <b>Thanh Xuân MobiFone HighTech</b><br>
            <i>Phiên bản này được viết ra nhờ sự stress khi học từ vựng 😅</i>
        </div>
    """, unsafe_allow_html=True)

data = load_data()

# --- LOGIC THÔNG MINH ---
def generate_new_question():
    if len(data) < 2: return
    
    # 1. Lọc bỏ các từ bị ẩn
    pool_after_ignore = [d for d in data if d[COL_ENG] not in st.session_state.ignored_words]
    
    if not pool_after_ignore:
        st.warning("Bạn đã ẩn hết sạch từ rồi! Hãy bấm Reset hoặc tải lại trang.")
        return

    # 2. Lọc bỏ các từ vừa mới gặp
    if len(pool_after_ignore) > 8:
        available_pool = [d for d in pool_after_ignore if d[COL_ENG] not in st.session_state.recent_history]
        if not available_pool: available_pool = pool_after_ignore 
    else:
        available_pool = pool_after_ignore

    target = None
    if use_smart_review:
        weights = []
        for d in available_pool:
            word = d[COL_ENG]
            if word not in st.session_state.word_weights:
                weights.append(50) 
            else:
                weights.append(st.session_state.word_weights[word])
        
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
        st.session_state.score += 1; st.session_state.combo += 1 
        fire_icon = "🔥" * min(st.session_state.combo, 5) if st.session_state.combo > 1 else "🎉"
        st.session_state.last_result_msg = ("success", f"{fire_icon} Chính xác: {quiz['q']} - {quiz['a']}")
        
        if use_smart_review:
            if duration < 2.0: new_weight = max(1, current_weight - 5)
            elif duration > 3.5: new_weight = min(100, current_weight + 5)
            else: new_weight = max(1, current_weight - 2)
            st.session_state.word_weights[target_word] = new_weight
    else:
        st.session_state.combo = 0 
        st.session_state.last_result_msg = ("error", f"❌ Sai rồi: '{quiz['q']}' là '{quiz['a']}' chứ không phải '{selected_opt}'")
        st.session_state.word_weights[target_word] = min(100, current_weight + 15)

    st.session_state.recent_history.append(target_word)
    if len(st.session_state.recent_history) > 5: st.session_state.recent_history.pop(0)
    generate_new_question()

# HÀM XỬ LÝ NÚT ẨN
def ignore_current_word():
    if st.session_state.quiz:
        current_word = st.session_state.quiz['raw_en']
        st.session_state.ignored_words.append(current_word)
        st.toast(f"Đã ẩn từ: {current_word} 🙈", icon="✅")
        st.session_state.combo = 0 
        generate_new_question()

# --- GIAO DIỆN CHÍNH ---
st.markdown(f'<h1 class="main-title">🌸 {st.session_state.get("selected_sheet_name", "Loading...")}</h1>', unsafe_allow_html=True)

@st.fragment
def show_quiz_area():
    if not data: return
    if st.session_state.quiz is None: generate_new_question(); st.rerun()

    quiz = st.session_state.quiz
    
    # Header
    c1, c2, c3 = st.columns([2, 1, 2])
    with c1: st.caption(f"🏆 Điểm: **{st.session_state.score}/{st.session_state.total}**")
    with c2: 
        if st.session_state.combo > 1: st.markdown(f'<div class="combo-text">🔥 x{st.session_state.combo}</div>', unsafe_allow_html=True)
    score_val = st.session_state.score / (st.session_state.total if st.session_state.total > 0 else 1)
    st.progress(score_val)

    if st.session_state.last_result_msg:
        mstype, msg = st.session_state.last_result_msg
        if mstype == "success": st.success(msg, icon="✅")
        else: st.error(msg, icon="⚠️")
        st.session_state.last_result_msg = None

    # --- KHU VỰC CÂU HỎI VÀ NÚT ẨN (ĐÃ UPDATE LAYOUT NGANG) ---
    col_q, col_btn = st.columns([8, 2]) # Chia 8 phần cho câu hỏi, 2 phần cho nút
    with col_q:
        st.markdown(f'<div class="main-card"><h1>{quiz["q"]}</h1></div>', unsafe_allow_html=True)
    with col_btn:
        st.write("") # Spacer để nút không bị dính lên trên
        # Nút ẩn nhỏ gọn bên phải
        if st.button("🙈 Ẩn", key="btn_ignore_top", help="Tạm ẩn từ này khỏi phiên học"):
            ignore_current_word()
            st.rerun()
    
    # Audio
    col1, col2, col3 = st.columns([0.5, 9, 0.5]) 
    with col2:
        if st.session_state.get('current_audio_b64'):
            unique_id = f"audio_{uuid.uuid4()}"
            autoplay_attr = "autoplay" if auto_play else ""
            html_audio = f"""
                <div style="display: flex; justify-content: center; align-items: center; margin-top: 5px; margin-bottom: 25px;">
                    <audio id="{unique_id}" src="{st.session_state.current_audio_b64}" {autoplay_attr} controls 
                    style="width: 100%; max-width: 400px; height: 45px;"></audio>
                </div>
            """
            st.components.v1.html(html_audio, height=80)

    st.write("") 

    if st.session_state.mode == "🗣️ Luyện Phát Âm (Beta)":
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2: 
            audio = mic_recorder(start_prompt="🎙️ Nói", stop_prompt="⏹️ Dừng", key="static_mic_recorder", format="wav")
            
        if audio and audio['bytes'] != st.session_state.last_audio_bytes:
            st.session_state.last_audio_bytes = audio['bytes']
            spoken = recognize_speech(audio['bytes'])
            if spoken == quiz['raw_en'].lower().strip():
                st.session_state.combo += 1; st.balloons(); time.sleep(1); generate_new_question(); st.rerun()
            else: st.session_state.combo = 0; st.error(f"Bạn nói: {spoken}")
        if st.button("Bỏ qua"): st.session_state.combo = 0; generate_new_question(); st.rerun()
        
    else:
        col_1, col_2 = st.columns(2)
        for idx, opt in enumerate(quiz['opts']):
            with (col_1 if idx % 2 == 0 else col_2): 
                st.button(opt, key=uuid.uuid4(), on_click=handle_answer, args=(opt,), use_container_width=True)

show_quiz_area()
st.markdown(f'<div class="author-text">Made by {AUTHOR} 🌸</div>', unsafe_allow_html=True)
