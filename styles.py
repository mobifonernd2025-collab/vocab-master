# styles.py
import streamlit as st

def apply_css(theme):
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {theme['bg']}; }}
        div[data-testid="stVerticalBlock"] {{ opacity: 1 !important; transition: none !important; gap: 0.5rem !important; }}
        .element-container {{ opacity: 1 !important; transition: none !important; }}
        div[data-testid="stStatusWidget"] {{ visibility: hidden; }}

        .main-title {{ font-size: 24px !important; font-weight: 800 !important; color: {theme['text']} !important; text-align: center; margin-bottom: 0px; }}
        
        /* --- CARD CÂU HỎI (TO TỰ NHIÊN) --- */
        .main-card {{ 
            background-color: {theme['card_bg']}; 
            border-radius: 15px; 
            box-shadow: 0 4px 10px rgba(0,0,0,0.05); 
            border-top: 5px solid {theme['border']}; /* Viền trên dày tạo điểm nhấn */
            
            /* Để chiều cao tự động (auto) và tăng padding để khung to ra */
            padding: 5px 10px; 
            text-align: center;
            margin-bottom: 10px;
            margin-top: 5px;
            margin-left: auto !important;  /* Tự động căn giữa trái */
            margin-right: auto !important; /* Tự động căn giữa phải */
        }}
        
        .main-card h1 {{ 
            color: {theme['text']} !important; 
            font-size: 2.2em !important; /* Chữ to rõ ràng */
            margin: 0 !important; 
            font-weight: 800 !important;
        }}

        div[data-testid="stAlert"] {{ padding: 0.5rem 1rem !important; margin-bottom: 0.5rem !important; font-size: 1.1rem !important; }}

        /* --- NÚT BẤM --- */
        div.stButton > button {{ 
            min-height: 3.2em !important; 
            font-size: 18px !important; 
            border-radius: 12px !important; 
            font-weight: 600 !important; 
            background-color: {theme['btn_bg']}; 
            border: 2px solid {theme['border']} !important; 
            color: {theme['btn_text']} !important; 
            width: 100%; 
            transition: transform 0.1s;
            -webkit-tap-highlight-color: transparent; 
            outline: none !important;
            white-space: normal !important;
            padding: 5px !important;
        }}

        @media (hover: hover) {{
            div.stButton > button:hover {{ background-color: {theme['btn_hover']} !important; color: {theme['text']} !important; }}
        }}

        @media (hover: none) {{
            div.stButton > button:hover, div.stButton > button:focus {{ 
                background-color: {theme['btn_bg']} !important; color: {theme['btn_text']} !important; border-color: {theme['border']} !important; box-shadow: none !important;
            }}
            div.stButton > button:active {{ background-color: {theme['btn_hover']} !important; transform: scale(0.96); }}
        }}
        
        .combo-text {{ text-align: center; font-size: 1em; font-weight: bold; color: #FF4500; margin-bottom: 5px; animation: pulse 0.5s infinite alternate; }}
        .author-text {{ text-align: center; color: {theme['sub_text']}; font-size: 0.8em; margin-top: 10px; opacity: 0.7; }}
        
        p, label {{ color: {theme['text']} !important; margin-bottom: 0px !important; }}
        .stCaption {{ color: {theme['sub_text']} !important; font-size: 0.9em !important; }}
        .stProgress > div > div > div > div {{ background-color: {theme['progress']} !important; }}
        </style>
        """, unsafe_allow_html=True)
