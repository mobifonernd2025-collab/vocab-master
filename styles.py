# styles.py
import streamlit as st

def apply_css(theme):
    st.markdown(f"""
        <style>
        /* --- 1. IMPORT FONT --- */
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');

        /* --- 2. CÁC ANIMATION (HIỆU ỨNG CHUYỂN ĐỘNG) --- */
        
        /* Hiệu ứng zoom nhẹ khi hiện thẻ */
        @keyframes quickFadeZoom {{
            0% {{ opacity: 0; transform: scale(0.96) translateY(5px); }}
            100% {{ opacity: 1; transform: scale(1) translateY(0); }}
        }}

        /* [MỚI] Hiệu ứng BIẾN HÌNH sang ĐÚNG (Trắng -> Xanh mượt mà) */
        @keyframes turnGreen {{
            0% {{ 
                background-color: {theme['btn_bg']}; 
                color: {theme['text']}; 
                border-color: {theme['border']};
                transform: scale(1);
            }}
            50% {{ transform: scale(1.03); }} /* Phình to ra một chút */
            100% {{ 
                background-color: #D4EDDA; 
                color: #155724; 
                border-color: #C3E6CB;
                transform: scale(1);
            }}
        }}

        /* [MỚI] Hiệu ứng BIẾN HÌNH sang SAI (Trắng -> Đỏ + Rung lắc) */
        @keyframes turnRed {{
            0% {{ 
                background-color: {theme['btn_bg']}; 
                color: {theme['text']};
                border-color: {theme['border']};
            }}
            25% {{ transform: translateX(-5px); }} /* Rung sang trái */
            50% {{ transform: translateX(5px); }}  /* Rung sang phải */
            75% {{ transform: translateX(-5px); }}
            100% {{ 
                background-color: #F8D7DA; 
                color: #721C24; 
                border-color: #F5C6CB;
                transform: translateX(0);
            }}
        }}

        /* --- 3. GIAO DIỆN CHÍNH --- */
        html, body, [class*="css"], button, input, textarea, p, h1, h2, h3 {{
            font-family: 'Nunito', sans-serif !important;
        }}

        .stApp {{ background-color: {theme['bg']}; transition: background-color 0.5s ease; }}
        div[data-testid="stVerticalBlock"] {{ gap: 0.5rem !important; }}
        
        /* Tiêu đề chính */
        .main-title {{ 
            font-size: 26px !important; font-weight: 800 !important; color: {theme['text']} !important; 
            text-align: center; margin-bottom: 0px; text-transform: uppercase; letter-spacing: 1px;
        }}
        
        /* Thẻ câu hỏi (Card) */
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

        /* Hộp kết quả (Cố định chiều cao để không bị nhảy) */
        .result-box {{
            min-height: 60px; display: flex; align-items: center; justify-content: center;
            padding: 5px 15px; border-radius: 12px; font-weight: 700; font-size: 1.1rem; text-align: center; margin-bottom: 10px;
            transition: all 0.3s ease;
        }}
        .result-success {{ background-color: #D1E7DD; color: #0f5132; border: 1px solid #badbcc; }}
        .result-error {{ background-color: #F8D7DA; color: #842029; border: 1px solid #f5c2c7; }}
        .result-hidden {{ background-color: transparent; color: transparent; border: 1px solid transparent; user-select: none; }}

        /* --- 4. NÚT BẤM (BUTTON GỐC CỦA STREAMLIT) --- */
        div.stButton > button {{ 
            min-height: 3.2em !important; 
            border-radius: 15px !important; 
            font-weight: 700 !important; 
            background-color: {theme['btn_bg']}; 
            border: 2px solid {theme['border']} !important; 
            color: {theme['btn_text']} !important; 
            width: 100%; transition: all 0.2s ease;
            box-shadow: 0 2px 0px rgba(0,0,0,0.05);
        }}
        div.stButton > button:hover {{ transform: translateY(-2px); box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        div.stButton > button p {{ font-size: 20px !important; margin: 0 !important; }}

        /* Fix nút Sidebar nhỏ lại */
        section[data-testid="stSidebar"] div.stButton > button {{
            min-height: auto !important; padding: 0.5em 1em !important; font-size: 16px !important; margin-top: 10px !important;
        }}

        /* --- 5. THANH TIẾN ĐỘ CẦU VỒNG (SUPER RAINBOW) --- */
        @keyframes rainbow-move {{ 0% {{ background-position: 0% 50%; }} 50% {{ background-position: 100% 50%; }} 100% {{ background-position: 0% 50%; }} }}
        div[data-testid="stProgress"] > div > div > div > div {{
            background: linear-gradient(90deg, #FF0000, #FF7F00, #FFFF00, #00FF00, #0000FF, #4B0082, #9400D3, #FF0000) !important;
            background-size: 400% 400% !important; border-radius: 10px !important;
            animation: rainbow-move 4s linear infinite !important;
            box-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
        }}
        div[data-testid="stProgress"] {{ background-color: rgba(0,0,0,0.05) !important; border-radius: 10px !important; padding: 2px !important; }}
        
        /* --- 6. [QUAN TRỌNG] CLASS NÚT GIẢ LẬP HIỆU ỨNG (BTN FAKE) --- */
        .btn-fake {{
            display: block; width: 100%; padding: 12px; margin: 5px 0;
            border-radius: 15px; font-weight: 700; text-align: center;
            font-size: 20px; /* Khớp size với nút thật */
            cursor: default; 
            border: 2px solid transparent;
            box-shadow: 0 2px 0px rgba(0,0,0,0.05);
            /* Bắt đầu với màu giống hệt nút thường */
            background-color: {theme['btn_bg']};
            color: {theme['text']};
            border-color: {theme['border']};
        }}
        
        /* KHI ĐÚNG: Chạy animation turnGreen trong 0.6 giây */
        .btn-correct-visual {{
            animation: turnGreen 0.6s ease forwards !important; 
        }}
        
        /* KHI SAI: Chạy animation turnRed trong 0.6 giây */
        .btn-wrong-visual {{
            animation: turnRed 0.6s ease forwards !important;
        }}
        
        /* CÁC NÚT KHÁC: Mờ dần đi */
        .btn-neutral-visual {{
            opacity: 0.5;
            transition: opacity 0.5s ease;
            filter: grayscale(100%); /* Làm xám màu đi */
        }}

        /* Text phụ */
        .combo-text {{ text-align: center; font-size: 1.1em; font-weight: 800; color: #FF4500; margin-bottom: 5px; }}
        .author-text {{ text-align: center; color: {theme['sub_text']}; font-size: 0.85em; margin-top: 15px; opacity: 0.6; font-style: italic; }}
        p, label {{ color: {theme['text']} !important; margin-bottom: 0px !important; }}
        .stCaption {{ color: {theme['sub_text']} !important; }}

        </style>
        """, unsafe_allow_html=True)
