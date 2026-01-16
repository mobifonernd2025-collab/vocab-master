# styles.py
import streamlit as st

def apply_css(theme):
    st.markdown(f"""
        <style>
        /* --- 1. IMPORT FONT --- */
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');

        /* --- 2. KEYFRAMES (ĐỊNH NGHĨA CHUYỂN ĐỘNG) --- */
        
        /* Hiệu ứng Fade In (Hiện ra từ từ + trượt lên) */
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        /* Hiệu ứng Shake (Rung lắc khi sai) */
        @keyframes shake {{
            0% {{ transform: translateX(0); }}
            25% {{ transform: translateX(-5px); }}
            50% {{ transform: translateX(5px); }}
            75% {{ transform: translateX(-5px); }}
            100% {{ transform: translateX(0); }}
        }}

        /* Hiệu ứng Pop (Nảy lên khi đúng) */
        @keyframes pop {{
            0% {{ transform: scale(0.8); opacity: 0; }}
            50% {{ transform: scale(1.05); opacity: 1; }}
            100% {{ transform: scale(1); }}
        }}

        /* --- 3. GLOBAL STYLES --- */
        html, body, [class*="css"], button, input, textarea, p, h1, h2, h3 {{
            font-family: 'Nunito', sans-serif !important;
        }}

        .stApp {{ background-color: {theme['bg']}; transition: background-color 0.5s ease; }}
        div[data-testid="stVerticalBlock"] {{ gap: 0.5rem !important; }}
        div[data-testid="stStatusWidget"] {{ visibility: hidden; }}

        .main-title {{ 
            font-size: 26px !important; 
            font-weight: 800 !important; 
            color: {theme['text']} !important; 
            text-align: center; margin-bottom: 0px; 
            text-transform: uppercase; letter-spacing: 1px;
            animation: pop 0.8s ease-out; /* Tiêu đề nảy ra khi load */
        }}
        
        /* --- CARD CÂU HỎI --- */
        .main-card {{ 
            background-color: {theme['card_bg']}; 
            border-radius: 20px; 
            box-shadow: 0 8px 20px rgba(0,0,0,0.08); 
            border-top: 5px solid {theme['border']}; 
            padding: 1px 10px !important; 
            text-align: center;
            margin-bottom: 10px; margin-top: 5px;
            margin-left: auto !important; margin-right: auto !important;
            
            /* Animation: Mỗi lần hiện câu mới sẽ trượt lên nhẹ nhàng */
            animation: fadeInUp 0.5s ease-out; 
        }}
        
        .main-card h1 {{ 
            color: {theme['text']} !important; 
            font-size: 2.5em !important; 
            margin: 0 !important; font-weight: 800 !important;
            line-height: 1.2 !important;
        }}

        /* --- THÔNG BÁO KẾT QUẢ (CUSTOM) --- */
        .result-box {{
            padding: 15px;
            border-radius: 12px;
            font-weight: 700;
            font-size: 1.1rem;
            text-align: center;
            margin-bottom: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .result-success {{
            background-color: #D1E7DD; color: #0f5132; border: 1px solid #badbcc;
            animation: pop 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); /* Hiệu ứng nảy đàn hồi */
        }}
        .result-error {{
            background-color: #F8D7DA; color: #842029; border: 1px solid #f5c2c7;
            animation: shake 0.4s ease-in-out; /* Hiệu ứng rung lắc */
        }}

        /* --- NÚT BẤM --- */
        div.stButton > button {{ 
            min-height: 3.2em !important; 
            border-radius: 15px !important; 
            font-weight: 700 !important; 
            background-color: {theme['btn_bg']}; 
            border: 2px solid {theme['border']} !important; 
            color: {theme['btn_text']} !important; 
            width: 100%; 
            transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1); /* Chuyển động mượt */
            outline: none !important;
            white-space: normal !important;
            padding: 5px !important;
            position: relative; top: 0;
        }}

        div.stButton > button p {{
            font-size: 22px !important;
            line-height: 1.1 !important;
            margin: 0 !important;
        }}

        /* Hover trên PC: Nút nổi lên và bóng đổ đậm hơn */
        @media (hover: hover) {{
            div.stButton > button:hover {{ 
                background-color: {theme['btn_hover']} !important; 
                color: {theme['text']} !important; 
                transform: translateY(-4px); 
                box-shadow: 0 6px 12px rgba(0,0,0,0.15);
            }}
        }}

        /* Active trên Mobile: Nút lún xuống */
        div.stButton > button:active {{ 
            background-color: {theme['btn_hover']} !important; 
            transform: translateY(2px) scale(0.98) !important; 
            box-shadow: none !important;
        }}
        
        .combo-text {{ 
            text-align: center; font-size: 1.2em; font-weight: 800; color: #FF4500; margin-bottom: 5px; 
            animation: pop 0.5s infinite alternate; /* Combo nhảy liên tục */
        }}
        
        .author-text {{ text-align: center; color: {theme['sub_text']}; font-size: 0.85em; margin-top: 15px; opacity: 0.8; font-style: italic; }}
        
        p, label {{ color: {theme['text']} !important; margin-bottom: 0px !important; }}
        .stCaption {{ color: {theme['sub_text']} !important; font-size: 0.95em !important; font-weight: 600; }}
        .stProgress > div > div > div > div {{ 
            background-color: {theme['progress']} !important; 
            border-radius: 10px;
            transition: width 0.5s ease-in-out; /* Thanh tiến độ chạy mượt */
        }}
        </style>
        """, unsafe_allow_html=True)
