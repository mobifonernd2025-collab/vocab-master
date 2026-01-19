# styles.py
import streamlit as st

def apply_css(theme):
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');

        /* --- GLOBAL & ANIMATIONS --- */
        html, body, [class*="css"], button, input, textarea, p, h1, h2, h3 {{
            font-family: 'Nunito', sans-serif !important;
        }}
        
        /* 1. Animation xuất hiện của khung câu hỏi */
        @keyframes quickFadeZoom {{
            0% {{ opacity: 0; transform: scale(0.96) translateY(5px); }}
            100% {{ opacity: 1; transform: scale(1) translateY(0); }}
        }}

        /* 2. [MỚI] Animation BIẾN HÌNH sang ĐÚNG (Trắng -> Xanh) */
        @keyframes turnGreen {{
            0% {{ background-color: {theme['btn_bg']}; color: {theme['text']}; transform: scale(1); border-color: {theme['border']}; }}
            50% {{ transform: scale(1.02); }} /* Hơi phình ra một chút */
            100% {{ background-color: #D4EDDA; color: #155724; transform: scale(1); border-color: #C3E6CB; }}
        }}

        /* 3. [MỚI] Animation BIẾN HÌNH sang SAI (Trắng -> Đỏ) */
        @keyframes turnRed {{
            0% {{ background-color: {theme['btn_bg']}; color: {theme['text']}; transform: scale(1); border-color: {theme['border']}; }}
            20% {{ transform: translateX(-5px); }} /* Rung lắc nhẹ */
            40% {{ transform: translateX(5px); }}
            60% {{ transform: translateX(-5px); }}
            100% {{ background-color: #F8D7DA; color: #721C24; transform: scale(1); border-color: #F5C6CB; }}
        }}

        /* --- CẤU HÌNH GIAO DIỆN CHÍNH --- */
        .stApp {{ background-color: {theme['bg']}; transition: background-color 0.5s ease; }}
        div[data-testid="stVerticalBlock"] {{ gap: 0.5rem !important; }}
        div[data-testid="stStatusWidget"] {{ visibility: hidden; }}

        .main-title {{ 
            font-size: 26px !important; font-weight: 800 !important; color: {theme['text']} !important; 
            text-align: center; margin-bottom: 0px; text-transform: uppercase; letter-spacing: 1px;
        }}
        
        .main-card {{ 
            background-color: {theme['card_bg']}; border-radius: 20px; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.08); border-top: 5px solid {theme['border']}; 
            padding: 1px 10px !important; text-align: center;
            margin-bottom: 10px; margin-top: 5px;
            animation: quickFadeZoom 0.4s cubic-bezier(0.2, 0.8, 0.2, 1);
        }}
        
        .main-card h1 {{ 
            color: {theme['text']} !important; font-size: 2.5em !important; 
            margin: 0 !important; font-weight: 800 !important; line-height: 1.2 !important;
        }}

        /* --- RESULT BOX --- */
        .result-box {{
            min-height: 60px; display: flex; align-items: center; justify-content: center;
            padding: 5px 15px; border-radius: 12px; font-weight: 700; font-size: 1.1rem; text-align: center; margin-bottom: 10px;
            transition: all 0.3s ease;
        }}
        .result-success {{ background-color: #D1E7DD; color: #0f5132; border: 1px solid #badbcc; }}
        .result-error {{ background-color: #F8D7DA; color: #842029; border: 1px solid #f5c2c7; }}
        .result-hidden {{ background-color: transparent; color: transparent; border: 1px solid transparent; user-select: none; }}

        /* --- NÚT BẤM (BUTTON) --- */
        div.stButton > button {{ 
            min-height: 3.2em !important; 
            border-radius: 15px !important; 
            font-weight: 700 !important; 
            background-color: {theme['btn_bg']}; 
            border: 2px solid {theme['border']} !important; 
            color: {theme['btn_text']} !important; 
            width: 100%; transition: all 0.2s ease;
            box-shadow: 0 2px 0px rgba(0,0,0,0.05); /* Bóng nhẹ giả lập độ nổi */
        }}
        div.stButton > button:hover {{ transform: translateY(-2px); box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        div.stButton > button:active {{ transform: scale(0.98); }}
        div.stButton > button p {{ font-size: 20px !important; margin: 0 !important; }}

        /* Nút Sidebar nhỏ lại */
        section[data-testid="stSidebar"] div.stButton > button {{
            min-height: auto !important; padding: 0.5em 1em !important; font-size: 16px !important; margin-top: 10px !important;
        }}

        /* --- THANH TIẾN ĐỘ CẦU VỒNG --- */
        @keyframes rainbow-move {{ 0% {{ background-position: 0% 50%; }} 50% {{ background-position: 100% 50%; }} 100% {{ background-position: 0% 50%; }} }}
        div[data-testid="stProgress"] > div > div > div > div {{
            background: linear-gradient(90deg, #FF0000, #FF7F00, #FFFF00, #00FF00, #0000FF, #4B0082, #9400D3, #FF0000) !important;
            background-size: 400% 400% !important; border-radius: 10px !important;
            animation: rainbow-move 4s linear infinite !important;
            box-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
        }}
        div[data-testid="stProgress"] {{ background-color: rgba(0,0,0,0.05) !important; border-radius: 10px !important; padding: 2px !important; }}
        
        /* --- [QUAN TRỌNG] CLASS CHO HIỆU ỨNG ĐÁP ÁN MỀM MẠI --- */
        .btn-fake {{
            display: block; width: 100%; padding: 12px; margin: 5px 0;
            border-radius: 15px; font-weight: 700; text-align: center;
            font-size: 20px; /* Khớp size với nút thật */
            cursor: default; 
            border: 2px solid transparent;
            box-shadow: 0 2px 0px rgba(0,0,0,0.05);
        }}
        
        /* Khi ĐÚNG: Chuyển từ trắng sang xanh từ từ trong 0.5s */
        .btn-correct-visual {{
            animation: turnGreen 0.5s ease forwards; /* Chạy animation turnGreen */
        }}
        
        /* Khi SAI: Chuyển từ trắng sang đỏ + rung lắc nhẹ */
        .btn-wrong-visual {{
            animation: turnRed 0.5s ease forwards; /* Chạy animation turnRed */
            opacity: 0.9;
        }}
        
        /* Nút còn lại: Mờ đi nhẹ nhàng */
        .btn-neutral-visual {{
            background-color: #f0f2f6 !important; color: #aaa !important;
            border-color: #eee !important;
            transition: all 0.5s ease; /* Mờ dần thay vì bụp phát mờ luôn */
            opacity: 0.6;
        }}

        /* Text phụ */
        .combo-text {{ text-align: center; font-size: 1.1em; font-weight: 800; color: #FF4500; margin-bottom: 5px; }}
        .author-text {{ text-align: center; color: {theme['sub_text']}; font-size: 0.85em; margin-top: 15px; opacity: 0.6; font-style: italic; }}
        p, label {{ color: {theme['text']} !important; margin-bottom: 0px !important; }}
        .stCaption {{ color: {theme['sub_text']} !important; }}

        </style>
        """, unsafe_allow_html=True)
