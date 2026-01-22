# styles.py
import streamlit as st

def apply_css(theme):
    st.markdown(f"""
        <style>
        /* --- 1. IMPORT FONT --- */
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');

        /* --- 2. CÀI ĐẶT BIẾN KÍCH THƯỚC CHUNG (CHÌA KHÓA CHỐNG GIẬT) --- */
        :root {{
            --btn-h: 56px;           /* Chiều cao cố định */
            --btn-radius: 15px;      /* Bo tròn */
            --btn-font: 20px;        /* Cỡ chữ */
            --btn-padding: 0px 5px;  /* Khoảng cách lề */
        }}

        /* --- 3. ANIMATION --- */
        
        /* Hiệu ứng zoom nhẹ khi hiện thẻ */
        @keyframes quickFadeZoom {{
            0% {{ opacity: 0; }}
            100% {{ opacity: 1; }}
        }}

        /* ĐÚNG: Chỉ đổi màu (Tuyệt đối không phóng to) */
        @keyframes turnGreen {{
            from {{ background-color: {theme['btn_bg']}; color: {theme['text']}; border-color: {theme['border']}; }}
            to {{ background-color: #D4EDDA; color: #155724; border-color: #C3E6CB; }}
        }}

        /* SAI: Đổi màu + RUNG LẮC (Shake) */
        @keyframes turnRed {{
            0% {{ background-color: {theme['btn_bg']}; transform: translateX(0); }}
            25% {{ transform: translateX(-5px); }}
            50% {{ transform: translateX(5px); }} 
            75% {{ transform: translateX(-5px); }}
            100% {{ background-color: #F8D7DA; color: #721C24; border-color: #F5C6CB; transform: translateX(0); }}
        }}

        /* --- 4. GIAO DIỆN CHUNG --- */
        html, body, [class*="css"], button, input, textarea, p, h1, h2, h3 {{
            font-family: 'Nunito', sans-serif !important;
        }}
        .stApp {{ background-color: {theme['bg']}; transition: background-color 0.5s ease; }}
        div[data-testid="stVerticalBlock"] {{ gap: 0.5rem !important; }}

        /* --- 5. NÚT BẤM THẬT (st.button) --- */
        div.stButton > button {{ 
            /* Ép kích thước theo biến chung */
            height: var(--btn-h) !important;
            min-height: var(--btn-h) !important;
            max-height: var(--btn-h) !important;
            border-radius: var(--btn-radius) !important;
            padding: var(--btn-padding) !important;
            
            /* Font chữ & Màu sắc */
            font-size: var(--btn-font) !important;
            font-weight: 700 !important;
            background-color: {theme['btn_bg']}; 
            border: 2px solid {theme['border']} !important; 
            color: {theme['btn_text']} !important; 
            
            width: 100%;
            box-shadow: 0 2px 0px rgba(0,0,0,0.05);
            transition: all 0.1s ease;
            outline: none !important;
        }}
        
        div.stButton > button p {{ 
            font-size: var(--btn-font) !important; 
            line-height: 1.2 !important; 
            margin: 0 !important; 
        }}

        /* --- 6. XỬ LÝ HOVER (GIỮ TÍNH NĂNG FIX ĐIỆN THOẠI) --- */
        
        /* Trên máy tính (Có chuột) -> Có hiệu ứng nổi lên */
        @media (hover: hover) {{
            div.stButton > button:hover {{ 
                background-color: {theme['btn_hover']} !important; 
                transform: translateY(-2px); 
                box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
            }}
        }}

        /* Trên điện thoại (Cảm ứng) -> Fix lỗi dính màu */
        @media (hover: none) {{
            div.stButton > button:hover, div.stButton > button:focus {{ 
                background-color: {theme['btn_bg']} !important; 
                color: {theme['btn_text']} !important; 
                border-color: {theme['border']} !important; 
                transform: none !important;
                box-shadow: 0 2px 0px rgba(0,0,0,0.05) !important;
            }}
            div.stButton > button:active {{ 
                background-color: {theme['btn_hover']} !important; 
                transform: scale(0.96); 
            }}
        }}

        /* --- 7. NÚT GIẢ (BTN FAKE) - ÉP GIỐNG HỆT NÚT THẬT --- */
        .btn-fake {{
            /* Ép kích thước y hệt biến chung */
            height: var(--btn-h) !important;
            min-height: var(--btn-h) !important;
            border-radius: var(--btn-radius) !important;
            padding: var(--btn-padding) !important;
            
            /* Flexbox để căn giữa chữ giống hệt st.button */
            display: flex; align-items: center; justify-content: center;
            
            /* Style khác */
            width: 100%;
            margin-top: 5px; /* Khớp margin mặc định của st.button */
            margin-bottom: 0px;
            font-size: var(--btn-font);
            font-weight: 700;
            line-height: 1.2;
            cursor: default;
            
            background-color: {theme['btn_bg']};
            color: {theme['text']};
            border: 2px solid {theme['border']}; /* Viền khớp nút thật */
            box-shadow: 0 2px 0px rgba(0,0,0,0.05);
            box-sizing: border-box !important; /* Tính cả viền vào kích thước */
        }}

        /* Animation cho nút giả */
        .btn-correct-visual {{ animation: turnGreen 0.3s ease forwards !important; }}
        .btn-wrong-visual {{ animation: turnRed 0.4s ease forwards !important; opacity: 0.9; }}
        .btn-neutral-visual {{ opacity: 0.5; filter: grayscale(100%); }}

        /* --- 8. CÁC THÀNH PHẦN KHÁC (GIỮ NGUYÊN) --- */
        
        /* Sidebar nút nhỏ */
        section[data-testid="stSidebar"] div.stButton > button {{
            height: auto !important; min-height: auto !important; padding: 5px 15px !important; font-size: 16px !important;
        }}

        .main-title {{ font-size: 26px !important; font-weight: 800; color: {theme['text']}; text-align: center; text-transform: uppercase; }}
        
        .main-card {{ 
            background-color: {theme['card_bg']}; border-radius: 20px; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.08); border-top: 5px solid {theme['border']}; 
            padding: 10px !important; text-align: center; margin-bottom: 10px; margin-top: 5px;
            animation: quickFadeZoom 0.3s;
        }}
        .main-card h1 {{ color: {theme['text']}; font-size: 2.2em; margin: 0; font-weight: 800; }}

        .result-box {{
            min-height: 50px; display: flex; align-items: center; justify-content: center;
            padding: 5px 15px; border-radius: 12px; font-weight: 700; margin-bottom: 10px;
        }}
        .result-success {{ background-color: #D1E7DD; color: #0f5132; }}
        .result-error {{ background-color: #F8D7DA; color: #842029; }}
        .result-hidden {{ opacity: 0; }}

        /* Cầu vồng */
        @keyframes rainbow-move {{ 0% {{ background-position: 0% 50%; }} 100% {{ background-position: 100% 50%; }} }}
        div[data-testid="stProgress"] > div > div > div > div {{
            background: linear-gradient(90deg, #FF0000, #FFFF00, #00FF00, #0000FF, #FF0000) !important;
            background-size: 200% 100% !important; animation: rainbow-move 3s linear infinite !important;
        }}
        
        .combo-text {{ text-align: center; font-size: 1.1em; font-weight: 800; color: #FF4500; margin-bottom: 5px; }}
        .author-text {{ text-align: center; color: {theme['sub_text']}; font-size: 0.8em; opacity: 0.6; margin-top: 20px; }}
        p, label {{ color: {theme['text']} !important; margin-bottom: 0px !important; }}
        
        </style>
        """, unsafe_allow_html=True)
