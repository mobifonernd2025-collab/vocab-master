# config.py

FILE_ID = '1xWdc8hmymvKn4bPzi8-YEy5hd_cVXdq22dVnwzB4Id0' 
COL_ENG = 'Từ vựng'
COL_VIE = 'Nghĩa'
AUTHOR = "Thanh Xuân"

def get_theme(mode):
    if mode == "Mint (Xanh Dịu)":
        return {
            "bg": "#E0F7FA", "card_bg": "#ffffff", "text": "#00695C", "sub_text": "#00897B",
            "border": "#4DB6AC", "btn_bg": "#ffffff", "btn_hover": "#B2DFDB", "btn_text": "#00695C", "progress": "#009688"
        }
    else: # Sakura
        return {
            "bg": "#FFF0F5", "card_bg": "#ffffff", "text": "#C71585", "sub_text": "#C71585",
            "border": "#FFB6C1", "btn_bg": "#ffffff", "btn_hover": "#FFB6C1", "btn_text": "#C71585", "progress": "#FF69B4"
        }
