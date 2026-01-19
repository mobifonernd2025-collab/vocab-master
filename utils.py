# utils.py
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import io
import base64
from gtts import gTTS
import speech_recognition as sr
from config import FILE_ID, COL_ENG, COL_VIE # <--- Đã sửa dòng này

# Hàm tạo audio
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

# Hàm nhận diện giọng nói
def recognize_speech(audio_bytes):
    r = sr.Recognizer()
    try:
        audio_file = io.BytesIO(audio_bytes)
        with sr.AudioFile(audio_file) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data, language="en-US")
            return text.lower()
    except: return "kém_chất_lượng"

# Hàm kết nối Google Sheet
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

# Hàm tải dữ liệu
@st.cache_data(ttl=300) # <--- Thêm dòng này: Lưu dữ liệu trong 10 phút (600s)
def load_data(sheet_name): # <--- Thêm tham số sheet_name vào đây
    try:
        # Không dùng st.session_state ở trong này nữa để tránh lỗi cache
        client = get_gspread_client()
        if not client: return []
        spreadsheet = client.open_by_key(FILE_ID)
        if sheet_name: 
            ws = spreadsheet.worksheet(sheet_name)
        else: 
            ws = spreadsheet.get_worksheet(0)
        return [r for r in ws.get_all_records() if r.get(COL_ENG) and r.get(COL_VIE)]
    except Exception as e:
        # st.error(f"Lỗi tải data: {e}") # Có thể bỏ comment để debug
        return []

# --- THÊM VÀO CUỐI FILE utils.py ---

def add_vocabulary(sheet_name, en_word, vi_word):
    """Thêm cặp từ mới vào sheet chỉ định"""
    try:
        client = get_gspread_client()
        if not client: return False
        
        spreadsheet = client.open_by_key(FILE_ID)
        ws = spreadsheet.worksheet(sheet_name)
        
        # Thêm dòng mới vào cuối
        ws.append_row([en_word, vi_word])
        return True
    except Exception as e:
        print(f"Lỗi thêm từ: {e}")
        return False

def create_new_topic(new_topic_name):
    """Tạo sheet chủ đề mới và điền Header chuẩn"""
    try:
        client = get_gspread_client()
        if not client: return False
        
        spreadsheet = client.open_by_key(FILE_ID)
        
        # Kiểm tra xem tên đã tồn tại chưa
        existing_sheets = [ws.title for ws in spreadsheet.worksheets()]
        if new_topic_name in existing_sheets:
            return False
            
        # Tạo sheet mới
        new_ws = spreadsheet.add_worksheet(title=new_topic_name, rows=100, cols=5)
        
        # QUAN TRỌNG: Thêm header chuẩn để App đọc được
        new_ws.append_row([COL_ENG, COL_VIE]) 
        return True
    except Exception as e:
        print(f"Lỗi tạo sheet: {e}")
        return False# --- THÊM VÀO CUỐI FILE utils.py ---

def add_vocabulary(sheet_name, en_word, vi_word):
    """Thêm cặp từ mới vào sheet chỉ định"""
    try:
        client = get_gspread_client()
        if not client: return False
        
        spreadsheet = client.open_by_key(FILE_ID)
        ws = spreadsheet.worksheet(sheet_name)
        
        # Thêm dòng mới vào cuối
        ws.append_row([en_word, "", vi_word, "", ""])
        return True
    except Exception as e:
        print(f"Lỗi thêm từ: {e}")
        return False

def create_new_topic(new_topic_name):
    """Tạo sheet chủ đề mới và điền Header chuẩn"""
    try:
        client = get_gspread_client()
        if not client: return False
        
        spreadsheet = client.open_by_key(FILE_ID)
        
        # Kiểm tra xem tên đã tồn tại chưa
        existing_sheets = [ws.title for ws in spreadsheet.worksheets()]
        if new_topic_name in existing_sheets:
            return False
            
        # Tạo sheet mới
        new_ws = spreadsheet.add_worksheet(title=new_topic_name, rows=100, cols=5)
        
        # QUAN TRỌNG: Thêm header chuẩn để App đọc được
        new_ws.append_row(["Từ vựng", "Loại từ", "Nghĩa", "Cụm từ hay gặp", "Ghi chú"]) 
        return True
    except Exception as e:
        print(f"Lỗi tạo sheet: {e}")
        return False
