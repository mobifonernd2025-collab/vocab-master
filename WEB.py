import streamlit as st
import random
import time
import uuid
from streamlit_mic_recorder import mic_recorder

# --- IMPORT TỪ CÁC FILE BÊN CẠNH ---
from config import AUTHOR, COL_ENG, COL_VIE, get_theme, FILE_ID # <--- Nhớ import FILE_ID ở đây
from styles import apply_css
from utils import get_audio_base64, recognize_speech, get_gspread_client, load_data

st.set_page_config(page_title=f"Vocab Master - {AUTHOR}", page_icon="🌸", layout="centered")

# --- KHỞI TẠO STATE (Giữ nguyên) ---
if 'theme_mode' not in st.session_state: st.session_state.theme_mode = "Sakura (Hồng)"
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
if 'quiz_state' not in st.session_state: st.session_state.quiz_state = "ANSWERING" 
if 'user_choice' not in st.session_state: st.session_state.user_choice = None

# --- ÁP DỤNG THEME & CSS ---
current_theme = get_theme(st.session_state.theme_mode)
apply_css(current_theme)

def reset_quiz():
    st.session_state.quiz = None
    st.session_state.last_result_msg = None
    st.session_state.combo = 0

# --- [QUAN TRỌNG] HÀM LẤY TÊN SHEET (CÓ CACHE) ---
@st.cache_data(ttl=3600)
def get_sheet_names():
    try:
        # Gọi client bên trong hàm để đảm bảo hoạt động tốt với cache
        client = get_gspread_client()
        if client:
            spreadsheet = client.open_by_key(FILE_ID)
            return [ws.title for ws in spreadsheet.worksheets()]
        return []
    except Exception as e:
        # st.error(f"Lỗi tải danh sách sheet: {e}") # Bật lên nếu cần debug
        return []

# --- GỌI HÀM ĐỂ LẤY DANH SÁCH ---
sheet_names = get_sheet_names()

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Cài đặt")
    
    # 1. Chọn Theme
    theme_choice = st.selectbox("Chọn màu:", ["Sakura (Hồng)", "Mint (Xanh Dịu)", "Ocean (Xanh Dương)", "Sunset (Cam Ấm)", "Lavender (Tím Nhạt)", "Midnight (Chế độ Tối)"], index=0 if st.session_state.theme_mode == "Sakura (Hồng)" else ["Sakura (Hồng)", "Mint (Xanh Dịu)", "Ocean (Xanh Dương)", "Sunset (Cam Ấm)", "Lavender (Tím Nhạt)", "Midnight (Chế độ Tối)"].index(st.session_state.theme_mode))
    if theme_choice != st.session_state.theme_mode:
        st.session_state.theme_mode = theme_choice
        st.rerun() 
    
    st.divider()
    
    # 2. Chọn Chủ đề (Nếu list có dữ liệu thì mới hiện)
    if sheet_names:
        # Mặc định chọn cái đầu tiên nếu chưa chọn
        current_idx = 0
        if st.session_state.get('selected_sheet_name') in sheet_names:
            current_idx = sheet_names.index(st.session_state.selected_sheet_name)
            
        new_sheet = st.selectbox("Chủ đề:", sheet_names, index=current_idx)
        
        if new_sheet != st.session_state.get('selected_sheet_name'):
            st.session_state.selected_sheet_name = new_sheet
            reset_quiz() 
            st.session_state.recent_history = [] 
            st.rerun()
    else:
        st.warning("⚠️ Không tải được danh sách chủ đề (hoặc Google chặn). Hãy thử tải lại trang!")

    # 3. Các cài đặt khác
    st.radio("Chế độ:", ["Anh ➔ Việt", "Việt ➔ Anh", "🗣️ Luyện Phát Âm (Beta)"], key="mode", on_change=reset_quiz)
    auto_play = st.toggle("🔊 Tự động phát âm", value=True)
    use_smart_review = st.checkbox("🧠 Ôn tập thông minh", value=True)
    
    if st.button("Reset điểm & Thuật toán"):
        st.session_state.score = 0; st.session_state.total = 0; st.session_state.word_weights = {} 
        st.session_state.recent_history = []; st.session_state.last_audio_bytes = None; st.session_state.combo = 0
        st.session_state.ignored_words = []
        reset_quiz(); st.rerun()
        
    st.divider()
    st.markdown(f"<div style='text-align: center; color: gray; font-size: 0.9em;'><b>{AUTHOR} MobiFone HighTech</b><br><i>Phiên bản này được viết ra nhờ sự stress khi học từ vựng 😅</i></div>", unsafe_allow_html=True)

# --- LOAD DATA (ĐOẠN SAU GIỮ NGUYÊN) ---
# Lưu ý sửa dòng gọi hàm load_data bên dưới cho đúng logic mới
current_sheet = st.session_state.get('selected_sheet_name', sheet_names[0] if sheet_names else None)
data = load_data(current_sheet)

# --- LOGIC ---
def generate_new_question():
    # 1. Reset trạng thái về chế độ trả lời
    st.session_state.quiz_state = "ANSWERING"
    st.session_state.user_choice = None
    
    if len(data) < 2: return
    
    pool_after_ignore = [d for d in data if d[COL_ENG] not in st.session_state.ignored_words]
    if not pool_after_ignore: st.warning("Bạn đã ẩn hết sạch từ rồi!"); return

    if len(pool_after_ignore) > 8:
        available_pool = [d for d in pool_after_ignore if d[COL_ENG] not in st.session_state.recent_history]
        if not available_pool: available_pool = pool_after_ignore 
    else: available_pool = pool_after_ignore

    target = None
    if use_smart_review:
        weights = [st.session_state.word_weights.get(d[COL_ENG], 50) for d in available_pool]
        weights = [w if w > 0 else 1 for w in weights] # Fix lỗi weight = 0
        target = random.choices(available_pool, weights=weights, k=1)[0]
    else: target = random.choice(available_pool)

    others = random.sample([d for d in data if d != target], min(3, len(data)-1))
    
    if st.session_state.mode == "Anh ➔ Việt":
        q, a = target[COL_ENG], target[COL_VIE]; opts = [d[COL_VIE] for d in others] + [a]
    elif st.session_state.mode == "Việt ➔ Anh":
        q, a = target[COL_VIE], target[COL_ENG]; opts = [d[COL_ENG] for d in others] + [a]
    else: q, a = target[COL_ENG], target[COL_VIE]; opts = []

    if st.session_state.mode != "🗣️ Luyện Phát Âm (Beta)": random.shuffle(opts)
    st.session_state.quiz = {'q': q, 'a': a, 'opts': opts, 'raw_en': target[COL_ENG]}
    st.session_state.current_audio_b64 = get_audio_base64(target[COL_ENG])
    st.session_state.start_time = time.time()

def handle_answer(selected_opt):
    quiz = st.session_state.quiz
    target_word = quiz['raw_en']
    current_weight = st.session_state.word_weights.get(target_word, 10)
    
    # 1. LƯU LẠI LỰA CHỌN VÀ CHUYỂN SANG CHẾ ĐỘ "REVIEW"
    st.session_state.user_choice = selected_opt
    st.session_state.quiz_state = "REVIEW" # <-- Quan trọng
    st.session_state.total += 1

    if selected_opt == quiz['a']:
        st.session_state.score += 1; st.session_state.combo += 1 
        fire_icon = "🔥" * min(st.session_state.combo, 5) if st.session_state.combo > 1 else "🎉"
        st.session_state.last_result_msg = ("success", f"{fire_icon} Chính xác! {quiz['q']} = {quiz['a']}")
        
        if use_smart_review:
            st.session_state.word_weights[target_word] = max(1, current_weight - 5)
    else:
        st.session_state.combo = 0 
        st.session_state.last_result_msg = ("error", f"❌ Sai rồi! Đáp án là: {quiz['a']}")
        st.session_state.word_weights[target_word] = min(100, current_weight + 15)

    st.session_state.recent_history.append(target_word)
    if len(st.session_state.recent_history) > 5: st.session_state.recent_history.pop(0)
def ignore_current_word():
    if st.session_state.quiz:
        current_word = st.session_state.quiz['raw_en']
        st.session_state.ignored_words.append(current_word)
        st.toast(f"Đã ẩn từ: {current_word} 🙈", icon="✅")
        st.session_state.combo = 0; generate_new_question()

# --- GIAO DIỆN CHÍNH ---
st.markdown(f'<h1 class="main-title">Chủ đề {st.session_state.get("selected_sheet_name", "Loading...")}</h1>', unsafe_allow_html=True)

@st.fragment
def show_quiz_area():
    if not data: return
    if st.session_state.quiz is None: generate_new_question(); st.rerun()

    quiz = st.session_state.quiz
    
    # 1. Header
    c1, c2, c3 = st.columns([2, 1, 2])
    with c1: st.caption(f"🏆 Điểm: **{st.session_state.score}/{st.session_state.total}**")
    with c2: 
        if st.session_state.combo > 1: st.markdown(f'<div class="combo-text">🔥 x{st.session_state.combo}</div>', unsafe_allow_html=True)
    score_val = st.session_state.score / (st.session_state.total if st.session_state.total > 0 else 1)
    st.progress(score_val)

    if st.session_state.last_result_msg:
        mstype, msg = st.session_state.last_result_msg
        if mstype == "success": st.markdown(f'<div class="result-box result-success">{msg}</div>', unsafe_allow_html=True)
        else: st.markdown(f'<div class="result-box result-error">{msg}</div>', unsafe_allow_html=True)
        st.session_state.last_result_msg = None

    # 2. KHUNG CÂU HỎI (Full Width)
    st.markdown(f'<div class="main-card"><h1>{quiz["q"]}</h1></div>', unsafe_allow_html=True)
    
    # 3. HÀNG: AUDIO + NÚT BỎ QUA (Nằm cạnh nhau)
    col_audio, col_skip = st.columns([7, 3], vertical_alignment="center")
    
    with col_audio:
        if st.session_state.get('current_audio_b64'):
            unique_id = f"audio_{uuid.uuid4()}"
            autoplay_attr = "autoplay" if auto_play else ""
            html_audio = f"""
                <div style="display: flex; align-items: center; width: 100%;">
                    <audio id="{unique_id}" src="{st.session_state.current_audio_b64}" {autoplay_attr} controls 
                    style="width: 100%; height: 40px;"></audio>
                </div>
            """
            st.components.v1.html(html_audio, height=50)
            
    with col_skip:
        if st.button("Bỏ qua", key="btn_ignore_side", use_container_width=True, help="Tạm ẩn từ này"):
            ignore_current_word(); st.rerun()

    st.write("") 

    # 4. ĐÁP ÁN
    if st.session_state.mode == "🗣️ Luyện Phát Âm (Beta)":
        # ... (Phần code Luyện Phát Âm giữ nguyên không sửa gì) ...
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2: 
            audio = mic_recorder(start_prompt="🎙️ Nói", stop_prompt="⏹️ Dừng", key="static_mic_recorder", format="wav")
        if audio and audio['bytes'] != st.session_state.last_audio_bytes:
             # (Logic cũ của phần mic...)
             st.session_state.last_audio_bytes = audio['bytes']
             spoken = recognize_speech(audio['bytes'])
             if spoken == quiz['raw_en'].lower().strip():
                 st.balloons(); time.sleep(1); generate_new_question(); st.rerun()
             else: st.error(f"Bạn nói: {spoken}")
        if st.button("Câu khác ➡️"): generate_new_question(); st.rerun()

    else:
        # --- LOGIC MỚI CHO TRẮC NGHIỆM ---
        
        # TRƯỜNG HỢP 1: ĐANG TRẢ LỜI (Hiện nút bấm để chọn)
        if st.session_state.quiz_state == "ANSWERING":
            col_1, col_2 = st.columns(2)
            for idx, opt in enumerate(quiz['opts']):
                with (col_1 if idx % 2 == 0 else col_2): 
                    # Nút bấm bình thường
                    st.button(opt, key=f"btn_{uuid.uuid4()}", on_click=handle_answer, args=(opt,), use_container_width=True)
        
        # TRƯỜNG HỢP 2: ĐÃ CHỌN XONG (Hiện màu sắc + Tự động chuyển)
        else:
            col_1, col_2 = st.columns(2)
            correct_answer = quiz['a']
            user_choice = st.session_state.user_choice
            
            # Vẽ các ô màu
            for idx, opt in enumerate(quiz['opts']):
                with (col_1 if idx % 2 == 0 else col_2):
                    if opt == correct_answer:
                        # Đáp án đúng -> Màu Xanh
                        st.markdown(f'<div class="btn-fake btn-correct-visual">✅ {opt}</div>', unsafe_allow_html=True)
                    elif opt == user_choice and opt != correct_answer:
                        # Chọn sai -> Màu Đỏ
                        st.markdown(f'<div class="btn-fake btn-wrong-visual">❌ {opt}</div>', unsafe_allow_html=True)
                    else:
                        # Các cái khác -> Màu Xám
                        st.markdown(f'<div class="btn-fake btn-neutral-visual">{opt}</div>', unsafe_allow_html=True)
            
            # Dừng 1.5 giây để nhìn kết quả rồi tự chuyển
            time.sleep(1.5) 
            generate_new_question()
            st.rerun()

show_quiz_area()
st.markdown(f'<div class="author-text">Made by đại ca {AUTHOR}</div>', unsafe_allow_html=True)
