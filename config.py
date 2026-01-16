# config.py

FILE_ID = '1xWdc8hmymvKn4bPzi8-YEy5hd_cVXdq22dVnwzB4Id0' 
COL_ENG = 'Từ vựng'
COL_VIE = 'Nghĩa'
AUTHOR = "Thanh Xuân"

def get_theme(mode):
    # 1. MINT (Xanh Bạc Hà - Tươi mới)
    if mode == "Mint (Xanh Bạc Hà)":
        return {
            "bg": "#E0F7FA", "card_bg": "#ffffff", "text": "#00695C", "sub_text": "#00897B",
            "border": "#4DB6AC", "btn_bg": "#ffffff", "btn_hover": "#B2DFDB", "btn_text": "#00695C", "progress": "#009688"
        }
    
    # 2. OCEAN (Xanh Dương - Năng động, Tập trung)
    elif mode == "Ocean (Xanh Dương)":
        return {
            "bg": "#E3F2FD", "card_bg": "#ffffff", "text": "#1565C0", "sub_text": "#1976D2",
            "border": "#64B5F6", "btn_bg": "#ffffff", "btn_hover": "#BBDEFB", "btn_text": "#0D47A1", "progress": "#2196F3"
        }

    # 3. SUNSET (Cam Ấm - Năng lượng, Sáng tạo)
    elif mode == "Sunset (Cam Ấm)":
        return {
            "bg": "#FFF3E0", "card_bg": "#ffffff", "text": "#E65100", "sub_text": "#EF6C00",
            "border": "#FFB74D", "btn_bg": "#ffffff", "btn_hover": "#FFE0B2", "btn_text": "#E65100", "progress": "#FF9800"
        }

    # 4. LAVENDER (Tím - Nhẹ nhàng, Thư giãn)
    elif mode == "Lavender (Tím Nhạt)":
        return {
            "bg": "#F3E5F5", "card_bg": "#ffffff", "text": "#6A1B9A", "sub_text": "#8E24AA",
            "border": "#BA68C8", "btn_bg": "#ffffff", "btn_hover": "#E1BEE7", "btn_text": "#4A148C", "progress": "#9C27B0"
        }

    # 5. MIDNIGHT (Tối - Bảo vệ mắt, Ngầu)
    elif mode == "Midnight (Chế độ Tối)":
        return {
            "bg": "#0E1117", "card_bg": "#262730", "text": "#E0E0E0", "sub_text": "#A0A0A0",
            "border": "#414141", "btn_bg": "#262730", "btn_hover": "#383838", "btn_text": "#FFFFFF", "progress": "#76FF03"
        }

    # 6. SAKURA (Hồng - Mặc định)
    else: 
        return {
            "bg": "#FFF0F5", "card_bg": "#ffffff", "text": "#C71585", "sub_text": "#C71585",
            "border": "#FFB6C1", "btn_bg": "#ffffff", "btn_hover": "#FFB6C1", "btn_text": "#C71585", "progress": "#FF69B4"
        }
