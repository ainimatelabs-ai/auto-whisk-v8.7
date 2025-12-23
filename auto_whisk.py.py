"""
Auto Whisk Generator - Enhanced Version v8.5.0
Features:
- Smart Filtering (name/tags/caption based)
- Dynamic Subject/Scene Slots (unlimited)
- Turkish + English Language Support
- Modern UI with tooltips
- Reference image management with metadata

Author: Enhanced by Claude based on Duck Martians' original work
"""

import sys
import json
import requests
import base64
import os
import time
import re
import queue
import random
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QComboBox, QPlainTextEdit, QMessageBox, QFileDialog, 
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, 
    QProgressBar, QGroupBox, QSplitter, QCheckBox, QDialog, QScrollArea, 
    QSizePolicy, QStyle, QSpinBox, QFrame, QGridLayout, QToolButton, 
    QInputDialog, QTextEdit
)
from PySide6.QtGui import (
    QPixmap, QImage, QColor, QDesktopServices, QFont, QIcon, QPalette, 
    QPainter, QResizeEvent, QTextCursor
)
from PySide6.QtCore import Qt, Signal, QThread, QUrl, QSize, QObject, QTimer

# ==================== CONFIGURATION ====================
APP_VERSION = 'v8.6.0 FIXED FINAL'
USER_AGENT_STR = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
API_AUTH_SESSION = 'https://labs.google/fx/api/auth/session'
AUTHOR_API_URL = 'https://gist.githubusercontent.com/duckmartians/51788b5bc97bc83152b08a9886b834e1/raw/info.json'

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
        return os.path.join(base_path, relative_path)
    except Exception:
        return os.path.abspath(relative_path)

ICON_FILE = resource_path('icon.ico')

# App data directory
APP_NAME = 'AutoWhisk'
if sys.platform == 'win32':
    app_data_dir = os.getenv('APPDATA') or os.path.expanduser('~\\AppData\\Roaming')
elif sys.platform == 'darwin':
    app_data_dir = os.path.expanduser('~/Library/Application Support')
else:
    app_data_dir = os.path.expanduser('~/.local/share')

APP_DIR = os.path.join(app_data_dir, APP_NAME)
os.makedirs(APP_DIR, exist_ok=True)
AUTH_FILE = os.path.join(APP_DIR, 'auth_session_final.json')

RATIO_DATA = [
    ('ratio_landscape', 'IMAGE_ASPECT_RATIO_LANDSCAPE'),
    ('ratio_portrait', 'IMAGE_ASPECT_RATIO_PORTRAIT'),
    ('ratio_square', 'IMAGE_ASPECT_RATIO_SQUARE')
]

# ==================== TRANSLATIONS ====================
TRANSLATIONS = {
    'en': {
        'window_title': f'Auto Whisk Generator {APP_VERSION}',
        'grp_auth': 'Account Configuration',
        'instr_cookie': 'Cookie (JSON):',
        'placeholder_cookie': 'Paste your cookie JSON here...',
        'btn_check': 'Check & Save',
        'link_help': '📖 User Guide',
        'grp_info': 'Session Status',
        'info_placeholder': 'Please enter Cookie and click "Check & Save"...',
        'grp_config': 'Configuration & Prompts',
        'lbl_ratio': 'Aspect Ratio:',
        'lbl_num_images': 'Image Count:',
        'lbl_prompts': 'Prompts (one per line):',
        'placeholder_prompts': 'Enter your prompts here, one per line...',
        'btn_ref': 'Reference Images',
        'btn_import': 'Import TXT',
        'btn_start': 'START',
        'btn_stop': 'STOP',
        'btn_pause': 'PAUSE',
        'btn_resume': 'RESUME',
        'btn_retry_errors': 'Retry All Errors',
        'lbl_output': 'Output Folder:',
        'btn_browse': 'Browse',
        'btn_open_folder': 'Open Output Folder',
        'chk_auto_open': 'Auto-open folder when complete',
        'ratio_landscape': 'Landscape 16:9',
        'ratio_portrait': 'Portrait 9:16',
        'ratio_square': 'Square 1:1',
        'ref_dialog_title': 'Reference Images Manager - Smart Filtering',
        'cat_subject': 'Subjects (Characters)',
        'cat_scene': 'Scenes (Locations)',
        'cat_style': 'Style',
        'btn_add_subject': '+ Add Subject',
        'btn_add_scene': '+ Add Scene',
        'btn_upload_analyze': 'Upload & Analyze All',
        'btn_save_caption': 'Save All Metadata',
        'btn_ok': 'Done',
        'lbl_click_to_select': 'Click to select image',
        'lbl_name': 'Name:',
        'lbl_tags': 'Tags:',
        'lbl_caption': 'Caption:',
        'placeholder_name': 'e.g., John',
        'placeholder_tags': 'e.g., man, hero, brown-hair',
        'placeholder_caption': 'AI will generate caption...',
        'msg_uploading_3dot': 'Uploading...',
        'msg_upload_error_prefix': 'Error: ',
        'status_idle': 'Ready',
        'status_running': 'Running...',
        'status_done': '✓ Complete',
        'status_error': '✗ Error',
        'tooltip_delete': 'Delete this image',
        'tooltip_retry': 'Retry this row',
        'tooltip_folder': 'Open output folder',
        'alert_no_prompts': 'Please enter at least one prompt!',
        'alert_no_token': 'Please check and save your cookie first!',
        'alert_cookie_valid': 'Token retrieved successfully!\nExpires: ',
        'alert_cookie_invalid': 'Cookie verification failed!\nPlease check your cookie.',
        'smart_filter_info': 'Smart Filtering: References auto-selected based on prompt keywords',
        'filtering_status': 'Smart filtering: {count} references selected for this prompt',
        'help_url': 'https://github.com/duckmartians/Auto-Whisk-Portable'
    },
    'tr': {
        'window_title': f'Auto Whisk Generator {APP_VERSION}',
        'grp_auth': 'Hesap Yapılandırması',
        'instr_cookie': 'Cookie (JSON):',
        'placeholder_cookie': 'Cookie JSON buraya yapıştırın...',
        'btn_check': 'Kontrol Et ve Kaydet',
        'link_help': '📖 Kullanım Kılavuzu',
        'grp_info': 'Oturum Durumu',
        'info_placeholder': 'Lütfen Cookie girin ve "Kontrol Et ve Kaydet" butonuna basın...',
        'grp_config': 'Yapılandırma ve Promptlar',
        'lbl_ratio': 'Görsel Oranı:',
        'lbl_num_images': 'Görsel Sayısı:',
        'lbl_prompts': 'Promptlar (satır başına bir tane):',
        'placeholder_prompts': 'Promptlarınızı buraya girin, her satıra bir tane...',
        'btn_ref': 'Referans Görselleri',
        'btn_import': 'TXT İçe Aktar',
        'btn_start': 'BAŞLAT',
        'btn_stop': 'DURDUR',
        'btn_pause': 'DURAKLAT',
        'btn_resume': 'DEVAM ET',
        'btn_retry_errors': 'Tüm Hataları Tekrar Dene',
        'lbl_output': 'Çıktı Klasörü:',
        'btn_browse': 'Gözat',
        'btn_open_folder': 'Çıktı Klasörünü Aç',
        'chk_auto_open': 'Tamamlandığında klasörü otomatik aç',
        'ratio_landscape': 'Yatay 16:9',
        'ratio_portrait': 'Dikey 9:16',
        'ratio_square': 'Kare 1:1',
        'ref_dialog_title': 'Referans Görselleri Yöneticisi - Akıllı Filtreleme',
        'cat_subject': 'Karakterler',
        'cat_scene': 'Sahneler',
        'cat_style': 'Stil',
        'btn_add_subject': '+ Karakter Ekle',
        'btn_add_scene': '+ Sahne Ekle',
        'btn_upload_analyze': 'Tümünü Yükle ve Analiz Et',
        'btn_save_caption': 'Tüm Meta Verileri Kaydet',
        'btn_ok': 'Tamam',
        'lbl_click_to_select': 'Görsel seçmek için tıklayın',
        'lbl_name': 'İsim:',
        'lbl_tags': 'Etiketler:',
        'lbl_caption': 'Açıklama:',
        'placeholder_name': 'örn: Ahmet',
        'placeholder_tags': 'örn: adam, kahraman, kahverengi-saç',
        'placeholder_caption': 'AI açıklama oluşturacak...',
        'msg_uploading_3dot': 'Yükleniyor...',
        'msg_upload_error_prefix': 'Hata: ',
        'status_idle': 'Hazır',
        'status_running': 'Çalışıyor...',
        'status_done': '✓ Tamamlandı',
        'status_error': '✗ Hata',
        'tooltip_delete': 'Bu görseli sil',
        'tooltip_retry': 'Bu satırı tekrar dene',
        'tooltip_folder': 'Çıktı klasörünü aç',
        'alert_no_prompts': 'Lütfen en az bir prompt girin!',
        'alert_no_token': 'Önce cookie kontrol edin ve kaydedin!',
        'alert_cookie_valid': 'Token başarıyla alındı!\nSon kullanma tarihi: ',
        'alert_cookie_invalid': 'Cookie doğrulama başarısız!\nLütfen cookie kontrol edin.',
        'smart_filter_info': 'Akıllı Filtreleme: Referanslar prompt anahtar kelimelerine göre otomatik seçilir',
        'filtering_status': 'Akıllı filtreleme: Bu prompt için {count} referans seçildi',
        'help_url': 'https://github.com/duckmartians/Auto-Whisk-Portable'
    },
    'vi': {
        'window_title': f'Auto Whisk Generator {APP_VERSION}',
        'grp_auth': 'Cấu hình Tài khoản',
        'instr_cookie': 'Cookie (JSON):',
        'placeholder_cookie': 'Dán cookie JSON vào đây...',
        'btn_check': 'Kiểm tra & Lưu',
        'link_help': '📖 Hướng dẫn sử dụng',
        'grp_info': 'Trạng thái Phiên',
        'info_placeholder': 'Vui lòng nhập Cookie và nhấn "Kiểm tra & Lưu"...',
        'grp_config': 'Cấu hình & Prompts',
        'lbl_ratio': 'Tỉ lệ ảnh:',
        'lbl_num_images': 'Số lượng:',
        'lbl_prompts': 'Prompts (mỗi dòng một prompt):',
        'placeholder_prompts': 'Nhập prompts ở đây, mỗi dòng một cái...',
        'btn_ref': 'Ảnh Tham khảo',
        'btn_import': 'Nhập TXT',
        'btn_start': 'BẮT ĐẦU',
        'btn_stop': 'DỪNG',
        'btn_pause': 'TẠM DỪNG',
        'btn_resume': 'TIẾP TỤC',
        'btn_retry_errors': 'Thử lại Lỗi',
        'lbl_output': 'Thư mục đầu ra:',
        'btn_browse': 'Chọn',
        'btn_open_folder': 'Mở Thư mục',
        'chk_auto_open': 'Tự động mở thư mục khi hoàn thành',
        'ratio_landscape': 'Ngang 16:9',
        'ratio_portrait': 'Dọc 9:16',
        'ratio_square': 'Vuông 1:1',
        'ref_dialog_title': 'Quản lý Ảnh Tham khảo - Lọc Thông minh',
        'cat_subject': 'Chủ thể',
        'cat_scene': 'Cảnh',
        'cat_style': 'Phong cách',
        'btn_add_subject': '+ Thêm Chủ thể',
        'btn_add_scene': '+ Thêm Cảnh',
        'btn_upload_analyze': 'Tải lên & Phân tích',
        'btn_save_caption': 'Lưu Tất cả',
        'btn_ok': 'Xong',
        'lbl_click_to_select': 'Nhấp để chọn ảnh',
        'lbl_name': 'Tên:',
        'lbl_tags': 'Tags:',
        'lbl_caption': 'Mô tả:',
        'placeholder_name': 'vd: John',
        'placeholder_tags': 'vd: man, hero, brown-hair',
        'placeholder_caption': 'AI sẽ tạo mô tả...',
        'msg_uploading_3dot': 'Đang tải lên...',
        'msg_upload_error_prefix': 'Lỗi: ',
        'status_idle': 'Sẵn sàng',
        'status_running': 'Đang chạy...',
        'status_done': '✓ Hoàn thành',
        'status_error': '✗ Lỗi',
        'tooltip_delete': 'Xóa',
        'tooltip_retry': 'Thử lại',
        'tooltip_folder': 'Mở thư mục',
        'alert_no_prompts': 'Vui lòng nhập ít nhất một prompt!',
        'alert_no_token': 'Vui lòng kiểm tra và lưu cookie trước!',
        'alert_cookie_valid': 'Lấy token thành công!\nHết hạn: ',
        'alert_cookie_invalid': 'Xác minh cookie thất bại!\nVui lòng kiểm tra lại cookie.',
        'smart_filter_info': 'Lọc Thông minh: Tham khảo tự động chọn dựa trên từ khóa',
        'filtering_status': 'Lọc thông minh: {count} tham khảo được chọn cho prompt này',
        'help_url': 'https://github.com/duckmartians/Auto-Whisk-Portable'
    }
}

# ==================== STYLESHEET ====================
MODERN_STYLESHEET = '''
QWidget {
    background-color: #f4f7f6;
    font-family: "Segoe UI", sans-serif;
    font-size: 13px;
    color: #333;
}
QLabel { background-color: transparent; }
QCheckBox { background-color: transparent; spacing: 8px; }
QCheckBox::indicator { 
    width: 16px; height: 16px; 
    border: 2px solid #bdc3c7; 
    border-radius: 4px; 
    background-color: white; 
}
QCheckBox::indicator:unchecked:hover { border-color: #3498db; }
QCheckBox::indicator:checked { 
    background-color: #3498db; 
    border: 2px solid #3498db; 
}
QGroupBox { 
    background-color: #ffffff; 
    border-radius: 8px; 
    margin-top: 22px; 
    padding-top: 5px; 
    border: 1px solid #e0e0e0; 
}
QGroupBox::title { 
    subcontrol-origin: margin; 
    subcontrol-position: top left; 
    padding: 4px 10px; 
    background-color: #34495e; 
    color: white; 
    border-top-left-radius: 8px; 
    border-top-right-radius: 8px; 
    border-bottom-right-radius: 4px;
    font-weight: bold; 
    margin-left: 10px;
    font-size: 12px;
}
QLineEdit, QPlainTextEdit, QComboBox, QSpinBox, QTextEdit { 
    border: 1px solid #ccc; 
    border-radius: 4px; 
    padding: 5px; 
    background-color: #fff; 
}
QLineEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QSpinBox:focus, QTextEdit:focus { 
    border: 1px solid #3498db; 
}
QPushButton { 
    border-radius: 5px; 
    padding: 6px 12px; 
    font-weight: bold; 
    color: white; 
    border: none; 
}
QPushButton:hover { opacity: 0.9; }
QPushButton:pressed { background-color: rgba(0, 0, 0, 0.2); }
QPushButton:disabled { 
    background-color: #bdc3c7 !important; 
    color: #7f8c8d !important; 
}
QTableWidget { 
    background-color: white; 
    border: 1px solid #e0e0e0; 
    border-radius: 4px; 
    gridline-color: #f0f0f0; 
}
QHeaderView::section { 
    background-color: #ecf0f1; 
    padding: 6px; 
    border: none; 
    border-bottom: 2px solid #dcdcdc; 
    font-weight: bold; 
    color: #2c3e50; 
}
QTableWidget::item { padding: 5px; }
QTableWidget::item:selected { 
    background-color: #e8f6f3; 
    color: #333; 
}
QFrame.ref-slot { 
    border: 2px dashed #bdc3c7; 
    border-radius: 6px; 
    background-color: #fcfcfc; 
}
QFrame.ref-slot:hover { 
    border-color: #3498db; 
    background-color: #f0f8ff; 
}
QMessageBox QPushButton {
    background-color: #3498db;
    color: white;
    border-radius: 4px;
    padding: 6px 20px;
    font-weight: bold;
    min-width: 80px;
}
QMessageBox QPushButton:hover { background-color: #2980b9; }
QMessageBox QPushButton:pressed { background-color: #1f618d; }
'''


# ==================== SMART FILTERING FUNCTIONS ====================

def extract_important_words(text):
    """Extract important keywords from text for matching"""
    if not text:
        return []
    
    # Common stopwords (Turkish + English)
    stopwords_tr = {
        've', 'bir', 'bu', 'ile', 'için', 'de', 'da', 'mi', 'mı', 
        'mu', 'mü', 'gibi', 'daha', 'çok', 'en', 'olan', 'olarak',
        'var', 'yok', 'şey', 'şu', 'o', 'bu'
    }
    stopwords_en = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 
        'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was',
        'are', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'should', 'could',
        'may', 'might', 'can', 'this', 'that', 'these', 'those'
    }
    
    stopwords = stopwords_tr | stopwords_en
    
    # Remove punctuation and split
    text_clean = re.sub(r'[^\w\s-]', ' ', text.lower())
    words = text_clean.split()
    
    # Filter: length > 3 and not stopword
    important = [w for w in words if len(w) > 3 and w not in stopwords]
    
    return important[:10]  # Return first 10 important words


def calculate_match_score(prompt, ref):
    """
    Calculate how well a reference matches the prompt
    
    FIXED: Style uses caption only (no name/tags)
    
    Scoring:
    - Name exact match: +10
    - Tag exact match: +5 per tag
    - Caption important word match: +1 per word
    """
    score = 0
    prompt_lower = prompt.lower()
    
    # === STYLE: Caption only (NO name/tags) ===
    if ref.get('category') == 'MEDIA_CATEGORY_STYLE':
        if ref.get('caption'):
            important_words = extract_important_words(ref['caption'])
            for word in important_words:
                if word in prompt_lower:
                    score += 1
        return score  # Early return for style
    
    # Name match (highest priority)
    if ref.get('name'):
        name_lower = ref['name'].strip().lower()
        if name_lower and name_lower in prompt_lower:
            score += 10
    
    # Tags match
    if ref.get('tags'):
        tags = [t.strip().lower() for t in ref['tags'].split(',') if t.strip()]
        for tag in tags:
            if tag in prompt_lower:
                score += 5
    
    # Caption match (important words only)
    if ref.get('caption'):
        important_words = extract_important_words(ref['caption'])
        for word in important_words:
            if word in prompt_lower:
                score += 1
    
    return score


def smart_filter_references(prompt, all_refs):
    """
    Smart filtering: Select most relevant references based on prompt
    
    Rules:
    1. SUBJECTS with names mentioned in prompt → Include ALL matching names
    2. SUBJECTS without name matches → Top 2 by score (if score > 0)
    3. SCENES → Include if score > 0 (OR matching)
    4. STYLES → Include if score > 0 (OR matching)
    
    Args:
        prompt (str): User's generation prompt
        all_refs (list): List of reference dicts with 'name', 'tags', 'caption', 'category'
    
    Returns:
        list: Filtered list of references
    """
    if not all_refs:
        return []
    
    # Separate by category
    subjects = [r for r in all_refs if r.get('category') == 'MEDIA_CATEGORY_SUBJECT']
    scenes = [r for r in all_refs if r.get('category') == 'MEDIA_CATEGORY_SCENE']
    styles = [r for r in all_refs if r.get('category') == 'MEDIA_CATEGORY_STYLE']
    
    filtered = []
    
    # ===== SUBJECTS FILTERING =====
    if subjects:
        # Check for name matches first
        named_matches = []
        for ref in subjects:
            name = ref.get('name', '').strip()
            if name and name.lower() in prompt.lower():
                named_matches.append(ref)
        
        if named_matches:
            # Use ALL named matches (no limit when names are explicitly mentioned)
            filtered.extend(named_matches)
        else:
            # No name matches → score all subjects and take top 2
            scored = [(calculate_match_score(prompt, r), r) for r in subjects]
            scored.sort(reverse=True, key=lambda x: x[0])
            
            # Take top 2 subjects with score > 0
            for score, ref in scored[:2]:
                if score > 0:
                    filtered.append(ref)
    
    # ===== SCENES FILTERING (ONLY if match!) =====
    for ref in scenes:
        score = calculate_match_score(prompt, ref)
        if score > 0:  # Only include matching scenes
            filtered.append(ref)
            name = ref.get('name', 'Unnamed')
            print(f"[FILTER] ✓ Scene ({score}): {name}")
    
    # ===== STYLES FILTERING (OR matching) =====
    for ref in styles:
        if calculate_match_score(prompt, ref) > 0:
            filtered.append(ref)
    
    return filtered


# ==================== UTILITY FUNCTIONS ====================

def parse_cookie_input(raw_input):
    """Parse cookie from various input formats"""
    raw_input = raw_input.strip()
    if not raw_input:
        return ''
    
    # JSON format (array or single object)
    if raw_input.startswith('[') or raw_input.startswith('{'):
        try:
            data = json.loads(raw_input)
            if isinstance(data, dict):
                data = [data]
            
            cookies = []
            for c in data:
                if 'name' in c and 'value' in c:
                    cookies.append(f"{c['name']}={c['value']}")
            
            if cookies:
                return '; '.join(cookies)
        except:
            pass
    
    # Direct JWT token format
    if raw_input.startswith('ey'):
        return f'__Secure-next-auth.session-token={raw_input}'
    
    # Already formatted cookie string
    return raw_input


def upload_image_static(path, category, cookie_str, token):
    """
    Upload image to Google Labs and get caption + media ID
    
    Returns:
        tuple: (media_id, caption, error_msg)
    """
    if not os.path.exists(path):
        return (None, '', 'File not found')
    
    try:
        # Read and encode image
        with open(path, 'rb') as f:
            b64 = base64.b64encode(f.read()).decode('utf-8')
        
        ext = os.path.splitext(path)[1].lower()
        mime = 'image/png' if '.png' in ext else 'image/webp' if '.webp' in ext else 'image/jpeg'
        data_uri = f'data:{mime};base64,{b64}'
        
        sess_id = f';{int(datetime.now().timestamp() * 1000)}'
        common_headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'User-Agent': USER_AGENT_STR,
            'Origin': 'https://labs.google',
            'Referer': 'https://labs.google/fx/tools/whisk',
            'Authority': 'labs.google',
            'Cookie': parse_cookie_input(cookie_str)
        }
        
        # Step 1: Get caption
        caption_text = ''
        try:
            cap_payload = {
                'json': {
                    'clientContext': {
                        'workflowId': 'be042ce0-b110-463c-be13-5d23c5bf82b3',
                        'sessionId': sess_id
                    },
                    'captionInput': {
                        'candidatesCount': 1,
                        'mediaInput': {
                            'mediaCategory': category,
                            'rawBytes': data_uri
                        }
                    }
                }
            }
            
            r_cap = requests.post(
                'https://labs.google/fx/api/trpc/backbone.captionImage',
                headers=common_headers,
                json=cap_payload,
                timeout=40
            )
            
            if r_cap.status_code == 200:
                cap_data = r_cap.json()
                try:
                    candidates = cap_data.get('result', {}).get('data', {}).get('json', {}).get('result', {}).get('candidates', [])
                    if candidates:
                        caption_text = candidates[0].get('output', '')
                except:
                    pass
        except Exception:
            pass  # Caption is optional
        
        # Step 2: Upload media
        up_payload = {
            'json': {
                'clientContext': {
                    'workflowId': 'be042ce0-b110-463c-be13-5d23c5bf82b3',
                    'sessionId': sess_id
                },
                'uploadMediaInput': {
                    'mediaCategory': category,
                    'rawBytes': data_uri
                }
            }
        }
        
        r_up = requests.post(
            'https://labs.google/fx/api/trpc/backbone.uploadImage',
            headers=common_headers,
            json=up_payload,
            timeout=60
        )
        
        if r_up.status_code != 200:
            return (None, '', f'Upload HTTP {r_up.status_code}')
        
        up_data = r_up.json()
        try:
            mid = up_data.get('result', {}).get('data', {}).get('json', {}).get('result', {}).get('uploadMediaGenerationId')
            if mid:
                return (mid, caption_text if caption_text else 'No caption generated', None)
        except Exception as e:
            return (None, '', f'Parse error: {str(e)}')
        
        return (None, '', 'No Media ID returned')
        
    except Exception as e:
        return (None, '', str(e))


# ==================== QTHREAD WORKERS ====================

class AuthorInfoLoader(QThread):
    """Load author info from GitHub"""
    data_loaded = Signal(dict)
    
    def run(self):
        try:
            resp = requests.get(AUTHOR_API_URL, timeout=5)
            if resp.status_code == 200:
                self.data_loaded.emit(resp.json())
        except:
            pass


class CookieValidatorWorker(QThread):
    """Validate cookie and get access token"""
    result_signal = Signal(bool, str, int)
    
    def __init__(self, cookie_str):
        super().__init__()
        self.cookie_str = cookie_str
    
    def run(self):
        full_cookie = parse_cookie_input(self.cookie_str)
        
        try:
            # Get session token
            headers = {
                'Cookie': full_cookie,
                'Content-Type': 'text/plain;charset=UTF-8',
                'User-Agent': USER_AGENT_STR
            }
            
            resp = requests.get(API_AUTH_SESSION, headers=headers, timeout=20)
            if resp.status_code != 200:
                self.result_signal.emit(False, '', 0)
                return
            
            data = resp.json()
            token = data.get('access_token') or data.get('accessToken')
            
            if not token:
                self.result_signal.emit(False, '', 0)
                return
            
            # Validate token and get expiry
            try:
                r = requests.get(
                    f'https://www.googleapis.com/oauth2/v3/tokeninfo?access_token={token}',
                    timeout=10
                )
                if r.status_code == 200:
                    exp = int(r.json().get('exp', 0))
                    self.result_signal.emit(True, token, exp)
                else:
                    self.result_signal.emit(True, token, 0)
            except:
                # Token valid but can't get expiry
                self.result_signal.emit(True, token, 0)
                
        except Exception:
            self.result_signal.emit(False, '', 0)


class UploadWorker(QThread):
    """Upload single reference image"""
    finished = Signal(str, str, str)  # path, media_id, caption
    error = Signal(str, str)  # path, error_msg
    
    def __init__(self, path, category, cookie, token):
        super().__init__()
        self.path = path
        self.category = category
        self.cookie = cookie
        self.token = token
    
    def run(self):
        mid, cap, err = upload_image_static(
            self.path, self.category, self.cookie, self.token
        )
        
        if mid:
            self.finished.emit(self.path, mid, cap)
        else:
            self.error.emit(self.path, err or 'Unknown error')


class QueueWorker(QThread):
    """Main worker thread for image generation"""
    task_started = Signal(int, str)  # row_idx, status_text
    task_success = Signal(int, int, str)  # row_idx, col_idx, file_path
    task_failed = Signal(int, int, str)  # row_idx, col_idx, error_msg
    all_done = Signal()
    reference_uploaded = Signal(str, str, str)  # path, media_id, caption
    
    def __init__(self, task_queue, model_settings, output_dir, num_images, 
                 ref_data_list, cookie_str, token):
        super().__init__()
        self.task_queue = task_queue
        self.model_settings = model_settings
        self.output_dir = output_dir
        self.num_images = num_images
        self.ref_data_list = ref_data_list
        self.cookie_str = cookie_str
        self.access_token = token
        self.is_running = True
        self.is_paused = False
        self.prepared_refs = []
        self.prep_error = None
    
    def get_safe_filename(self, prompt):
        """Create safe filename from prompt"""
        slug = re.sub(r'[^\w\s-]', '', prompt).strip().replace(' ', '_')
        slug = re.sub(r'_+', '_', slug)[:40]
        return slug
    
    def prepare_references(self):
        """Upload any non-uploaded references"""
        final_list = []
        
        for item in self.ref_data_list:
            if not self.is_running:
                return False
            
            if item['type'] == 'uploaded':
                # Already uploaded
                final_list.append({
                    'caption': item['caption'],
                    'mediaInput': {
                        'mediaCategory': item['category'],
                        'mediaGenerationId': item['media_id']
                    }
                })
            else:
                # Need to upload
                mid, cap, err = upload_image_static(
                    item['path'], item['category'],
                    self.cookie_str, self.access_token
                )
                
                if mid:
                    self.reference_uploaded.emit(item['path'], mid, cap)
                    final_list.append({
                        'caption': cap,
                        'mediaInput': {
                            'mediaCategory': item['category'],
                            'mediaGenerationId': mid
                        }
                    })
                else:
                    self.prep_error = f"Upload Fail {os.path.basename(item['path'])}: {err}"
                    return False
        
        self.prepared_refs = final_list
        return True
    
    def run(self):
        """Main processing loop"""
        # Prepare references if any
        if self.ref_data_list:
            success = self.prepare_references()
            if not success:
                # Fail first task and exit
                try:
                    r, _ = self.task_queue.get_nowait()
                    self.task_failed.emit(r, 0, self.prep_error or 'Ref prep error')
                    self.task_queue.task_done()
                except:
                    pass
                self.all_done.emit()
                return
        
        # Process queue
        while self.is_running:
            # Wait if paused
            while self.is_paused and self.is_running:
                time.sleep(0.5)
            
            # Get task
            try:
                item = self.task_queue.get(timeout=1)
                
                # Support both formats
                if len(item) == 3:
                    row_idx, prompt, indices_to_process = item
                else:
                    row_idx, prompt = item
                    indices_to_process = range(self.num_images)
                    
            except queue.Empty:
                continue
            
            # Process each image in row
            for i in indices_to_process:
                if not self.is_running:
                    break
                
                while self.is_paused and self.is_running:
                    time.sleep(0.5)
                
                col_idx = i + 1
                self.task_started.emit(row_idx, f'{i+1}/{self.num_images}')
                
                try:
                    # Prepare request
                    sess_id = f';{int(datetime.now().timestamp() * 1000)}'
                    clean_cookie = parse_cookie_input(self.cookie_str)
                    
                    req_headers = {
                        'Authorization': f'Bearer {self.access_token}',
                        'Content-Type': 'application/json',
                        'User-Agent': USER_AGENT_STR,
                        'Origin': 'https://labs.google',
                        'Referer': 'https://labs.google/fx/tools/whisk',
                        'Authority': 'labs.google',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'X-Kl-Ajax-Request': 'Ajax_Request',
                        'Cookie': clean_cookie
                    }
                    
                    random_seed = random.randint(1, 2147483647)
                    
                    # Choose endpoint and payload based on references
                    if self.prepared_refs:
                        target_url = 'https://aisandbox-pa.googleapis.com/v1/whisk:runImageRecipe'
                        settings = self.model_settings.copy()
                        
                        # Model selection based on ref count
                        if len(self.prepared_refs) == 1:
                            settings['imageModel'] = 'GEM_PIX'
                        else:
                            settings['imageModel'] = 'R2I'
                        
                        payload = {
                            'clientContext': {
                                'workflowId': '',
                                'tool': 'BACKBONE',
                                'sessionId': sess_id
                            },
                            'imageModelSettings': settings,
                            'userInstruction': prompt,
                            'recipeMediaInputs': self.prepared_refs,
                            'seed': random_seed
                        }
                    else:
                        target_url = 'https://aisandbox-pa.googleapis.com/v1/whisk:generateImage'
                        payload = {
                            'clientContext': {
                                'workflowId': '',
                                'tool': 'BACKBONE',
                                'sessionId': sess_id
                            },
                            'imageModelSettings': self.model_settings,
                            'prompt': prompt,
                            'mediaCategory': 'MEDIA_CATEGORY_BOARD',
                            'seed': random_seed
                        }
                    
                    # Make request
                    resp = requests.post(
                        target_url,
                        headers=req_headers,
                        json=payload,
                        timeout=60
                    )
                    
                    if not self.is_running:
                        self.task_queue.task_done()
                        break
                    
                    # Handle response
                    if resp.status_code == 200:
                        data = resp.json()
                        panels = data.get('imagePanels', [])
                        
                        if panels:
                            gen_imgs = panels[0].get('generatedImages', [])
                            if gen_imgs:
                                b64_img = gen_imgs[0].get('encodedImage', '')
                                
                                # Save image
                                safe_name = self.get_safe_filename(prompt)
                                ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                                fn = f'{row_idx+1}_{safe_name}_{ts}_{i+1}.jpg'
                                fpath = os.path.join(self.output_dir, fn)
                                
                                with open(fpath, 'wb') as f:
                                    f.write(base64.b64decode(b64_img))
                                
                                self.task_success.emit(row_idx, col_idx, fpath)
                            else:
                                self.task_failed.emit(row_idx, col_idx, 'No image data')
                        else:
                            self.task_failed.emit(row_idx, col_idx, 'No panels')
                    else:
                        self.task_failed.emit(row_idx, col_idx, f'HTTP {resp.status_code}')
                    
                except Exception as e:
                    self.task_failed.emit(row_idx, col_idx, str(e)[:30])
                
                # Delay between images
                time.sleep(2)
            
            self.task_queue.task_done()
            time.sleep(1)
        
        self.all_done.emit()
    
    def stop(self):
        self.is_running = False
    
    def pause(self):
        self.is_paused = True
    
    def resume(self):
        self.is_paused = False


# ==================== CUSTOM WIDGETS ====================

class ClickableLabel(QLabel):
    """Label that emits signal when clicked"""
    clicked = Signal()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class ReferenceImageSlot(QFrame):
    """Enhanced reference image slot with name, tags, and caption"""
    image_changed = Signal()
    remove_requested = Signal(object)  # Emits self
    
    def __init__(self, category_key, category_api_val, parent=None, removable=False):
        super().__init__(parent)
        self.parent_dialog = parent
        self.category_key = category_key
        self.category_api_val = category_api_val
        self.image_path = None
        self.media_id = None
        self.removable = removable
        
        self.setProperty('class', 'ref-slot')
        self.setFixedWidth(280)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        # Image container
        self.img_container = QWidget()
        self.img_container.setFixedSize(264, 150)
        img_layout = QVBoxLayout(self.img_container)
        img_layout.setContentsMargins(0, 0, 0, 0)
        
        lang = self.parent_dialog.lang if self.parent_dialog else 'en'
        
        self.lbl_icon = QLabel(TRANSLATIONS[lang]['lbl_click_to_select'])
        self.lbl_icon.setAlignment(Qt.AlignCenter)
        self.lbl_icon.setStyleSheet('color: #bdc3c7; font-weight: bold; font-size: 11px;')
        
        self.lbl_thumb = QLabel()
        self.lbl_thumb.setAlignment(Qt.AlignCenter)
        self.lbl_thumb.setVisible(False)
        
        img_layout.addWidget(self.lbl_icon)
        img_layout.addWidget(self.lbl_thumb)
        
        layout.addWidget(self.img_container)
        
        # === CRITICAL FIX: Name & Tags ONLY for non-style ===
        if category_api_val != 'MEDIA_CATEGORY_STYLE':
            # Name input
            lbl_name = QLabel(TRANSLATIONS[lang]['lbl_name'])
            lbl_name.setStyleSheet('font-size: 11px; font-weight: bold; color: #555;')
            self.txt_name = QLineEdit()
            self.txt_name.setPlaceholderText(TRANSLATIONS[lang]['placeholder_name'])
            self.txt_name.setStyleSheet('font-size: 11px; padding: 4px;')
            layout.addWidget(lbl_name)
            layout.addWidget(self.txt_name)
        
            # Tags input
            lbl_tags = QLabel(TRANSLATIONS[lang]['lbl_tags'])
            lbl_tags.setStyleSheet('font-size: 11px; font-weight: bold; color: #555;')
            self.txt_tags = QLineEdit()
            self.txt_tags.setPlaceholderText(TRANSLATIONS[lang]['placeholder_tags'])
            self.txt_tags.setStyleSheet('font-size: 11px; padding: 4px;')
            layout.addWidget(lbl_tags)
            layout.addWidget(self.txt_tags)
        else:
            # Style: NO name/tags fields
            self.txt_name = None
            self.txt_tags = None
        
        # Caption input
        lbl_caption = QLabel(TRANSLATIONS[lang]['lbl_caption'])
        lbl_caption.setStyleSheet('font-size: 11px; font-weight: bold; color: #555;')
        self.txt_caption = QPlainTextEdit()
        self.txt_caption.setPlaceholderText(TRANSLATIONS[lang]['placeholder_caption'])
        self.txt_caption.setStyleSheet('font-size: 11px; border: 1px solid #ddd; background: #f9f9f9;')
        self.txt_caption.setFixedHeight(80)
        self.txt_caption.setReadOnly(True)
        layout.addWidget(lbl_caption)
        layout.addWidget(self.txt_caption)
        
        # Clear button
        self.btn_clear = QPushButton()
        self.btn_clear.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        self.btn_clear.setFixedSize(26, 26)
        self.btn_clear.setStyleSheet(
            'background-color: rgba(231, 76, 60, 0.9); '
            'border-radius: 4px; border: none; padding: 2px;'
        )
        self.btn_clear.setToolTip(TRANSLATIONS[lang]['tooltip_delete'])
        self.btn_clear.clicked.connect(self.clear_image)
        self.btn_clear.setVisible(False)
        self.btn_clear.setParent(self)
        self.btn_clear.move(245, 8)
        
        # Remove slot button (for dynamic slots)
        if self.removable:
            self.btn_remove = QPushButton('×')
            self.btn_remove.setFixedSize(24, 24)
            self.btn_remove.setStyleSheet(
                'QPushButton { '
                'background-color: #e74c3c; color: white; '
                'font-size: 16px; font-weight: bold; '
                'border-radius: 12px; border: 1px solid white; '
                '} '
                'QPushButton:hover { background-color: #c0392b; }'
            )
            self.btn_remove.setToolTip('Remove this slot')
            self.btn_remove.clicked.connect(lambda: self.remove_requested.emit(self))
            self.btn_remove.setParent(self)
            self.btn_remove.move(8, 8)
    
    def mousePressEvent(self, event):
        """Handle click to select image"""
        if not self.image_path and event.button() == Qt.LeftButton:
            # Only if clicking in image area
            if event.position().y() < 160:
                path, _ = QFileDialog.getOpenFileName(
                    self, 'Select Image', '',
                    'Images (*.png *.jpg *.jpeg *.webp)'
                )
                if path:
                    self.set_image(path)
    
    def update_lang(self, lang):
        """Update language of labels"""
        if not self.image_path:
            self.lbl_icon.setText(TRANSLATIONS[lang]['lbl_click_to_select'])
        
        # Update placeholders
        self.txt_name.setPlaceholderText(TRANSLATIONS[lang]['placeholder_name'])
        self.txt_tags.setPlaceholderText(TRANSLATIONS[lang]['placeholder_tags'])
        self.txt_caption.setPlaceholderText(TRANSLATIONS[lang]['placeholder_caption'])
    
    def set_image(self, path):
        """Set image from file path"""
        self.image_path = path
        self.media_id = None
        
        pixmap = QPixmap(path)
        self.lbl_thumb.setPixmap(
            pixmap.scaled(264, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
        
        self.lbl_icon.setVisible(False)
        self.lbl_thumb.setVisible(True)
        self.btn_clear.setVisible(True)
        
        # Reset caption
        self.txt_caption.setPlainText('')
        self.txt_caption.setReadOnly(True)
        self.txt_caption.setStyleSheet(
            'font-size: 11px; border: 1px solid #ddd; background: #f9f9f9;'
        )
        
        self.image_changed.emit()
    
    def set_upload_start(self):
        """Show uploading status"""
        lang = self.parent_dialog.lang if self.parent_dialog else 'en'
        self.txt_caption.setPlaceholderText(TRANSLATIONS[lang]['msg_uploading_3dot'])
    
    def set_upload_success(self, path, mid, caption):
        """Handle successful upload"""
        if path != self.image_path:
            return
        
        self.media_id = mid
        self.txt_caption.setPlainText(caption)
        self.txt_caption.setReadOnly(False)
        self.txt_caption.setStyleSheet(
            'font-size: 11px; border: 1px solid #27ae60; background: #fff;'
        )
        
        self.image_changed.emit()
    
    def set_upload_error(self, err):
        """Handle upload error"""
        lang = self.parent_dialog.lang if self.parent_dialog else 'en'
        self.txt_caption.setPlainText(
            f"{TRANSLATIONS[lang]['msg_upload_error_prefix']}{err}"
        )
        self.media_id = None
        self.image_changed.emit()
    
    def clear_image(self):
        """Clear selected image"""
        self.image_path = None
        self.media_id = None
        self.lbl_thumb.clear()
        self.lbl_thumb.setVisible(False)
        self.btn_clear.setVisible(False)
        self.txt_caption.clear()
        self.txt_name.clear()
        self.txt_tags.clear()
        self.lbl_icon.setVisible(True)
        self.image_changed.emit()
    
    def get_data(self):
        """Get slot data for processing"""
        if not self.image_path:
            return None
        
        return {
            'path': self.image_path,
            'category': self.category_api_val,
            'media_id': self.media_id,
            'name': self.txt_name.text().strip() if self.txt_name else '',
            'tags': self.txt_tags.text().strip() if self.txt_tags else '',
            'caption': self.txt_caption.toPlainText().strip(),
            'type': 'uploaded' if self.media_id else 'pending'
        }


class ReferenceDialog(QDialog):
    """Enhanced reference dialog with dynamic slots and smart filtering"""
    images_updated = Signal(int)  # total_count
    
    def __init__(self, lang='en', parent=None, cookie='', token=''):
        super().__init__(parent)
        self.lang = lang
        self.cookie = cookie
        self.token = token
        
        self.setWindowTitle(TRANSLATIONS[lang]['ref_dialog_title'])
        self.setModal(True)
        self.resize(950, 700)
        self.setStyleSheet('background-color: white;')
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        
        # Info banner
        info_banner = QLabel(f"ℹ️ {TRANSLATIONS[lang]['smart_filter_info']}")
        info_banner.setStyleSheet(
            'background-color: #e8f4f8; color: #2c3e50; '
            'padding: 8px; border-radius: 4px; font-size: 11px;'
        )
        info_banner.setWordWrap(True)
        main_layout.addWidget(info_banner)
        
        # Scroll area for slots
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet('QScrollArea { border: none; }')
        
        scroll_content = QWidget()
        self.main_grid = QVBoxLayout(scroll_content)
        self.main_grid.setSpacing(15)
        
        # ===== SUBJECTS SECTION =====
        self.subjects_widget = QWidget()
        subjects_layout = QVBoxLayout(self.subjects_widget)
        subjects_layout.setSpacing(8)
        
        # Header with add button
        subj_header = QHBoxLayout()
        lbl_subj = QLabel(TRANSLATIONS[lang]['cat_subject'])
        lbl_subj.setStyleSheet(
            'font-weight: bold; color: #34495e; font-size: 14px;'
        )
        
        self.btn_add_subject = QPushButton(TRANSLATIONS[lang]['btn_add_subject'])
        self.btn_add_subject.setStyleSheet(
            'background-color: #3498db; color: white; '
            'padding: 5px 10px; border-radius: 4px; font-size: 11px;'
        )
        self.btn_add_subject.clicked.connect(self.add_subject_slot)
        
        subj_header.addWidget(lbl_subj)
        subj_header.addStretch()
        subj_header.addWidget(self.btn_add_subject)
        
        subjects_layout.addLayout(subj_header)
        
        # Subjects container
        self.subjects_container = QWidget()
        self.subjects_layout = QHBoxLayout(self.subjects_container)
        self.subjects_layout.setSpacing(10)
        self.subjects_layout.addStretch()
        
        subjects_layout.addWidget(self.subjects_container)
        self.main_grid.addWidget(self.subjects_widget)
        
        # ===== SCENES SECTION =====
        self.scenes_widget = QWidget()
        scenes_layout = QVBoxLayout(self.scenes_widget)
        scenes_layout.setSpacing(8)
        
        # Header with add button
        scene_header = QHBoxLayout()
        lbl_scene = QLabel(TRANSLATIONS[lang]['cat_scene'])
        lbl_scene.setStyleSheet(
            'font-weight: bold; color: #34495e; font-size: 14px;'
        )
        
        self.btn_add_scene = QPushButton(TRANSLATIONS[lang]['btn_add_scene'])
        self.btn_add_scene.setStyleSheet(
            'background-color: #3498db; color: white; '
            'padding: 5px 10px; border-radius: 4px; font-size: 11px;'
        )
        self.btn_add_scene.clicked.connect(self.add_scene_slot)
        
        scene_header.addWidget(lbl_scene)
        scene_header.addStretch()
        scene_header.addWidget(self.btn_add_scene)
        
        scenes_layout.addLayout(scene_header)
        
        # Scenes container
        self.scenes_container = QWidget()
        self.scenes_layout = QHBoxLayout(self.scenes_container)
        self.scenes_layout.setSpacing(10)
        self.scenes_layout.addStretch()
        
        scenes_layout.addWidget(self.scenes_container)
        self.main_grid.addWidget(self.scenes_widget)
        
        # ===== STYLE SECTION =====
        style_widget = QWidget()
        style_layout = QVBoxLayout(style_widget)
        style_layout.setSpacing(8)
        
        lbl_style = QLabel(TRANSLATIONS[lang]['cat_style'])
        lbl_style.setStyleSheet(
            'font-weight: bold; color: #34495e; font-size: 14px;'
        )
        style_layout.addWidget(lbl_style)
        
        # Style slot (single, not removable)
        self.style_slot = ReferenceImageSlot(
            'cat_style', 'MEDIA_CATEGORY_STYLE', self, removable=False
        )
        
        style_h = QHBoxLayout()
        style_h.addStretch()
        style_h.addWidget(self.style_slot)
        style_h.addStretch()
        
        style_layout.addLayout(style_h)
        self.main_grid.addWidget(style_widget)
        
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_upload = QPushButton(TRANSLATIONS[lang]['btn_upload_analyze'])
        self.btn_upload.setStyleSheet(
            'background-color: #3498db; color: white; '
            'padding: 10px 20px; font-weight: bold; border-radius: 5px;'
        )
        self.btn_upload.clicked.connect(self.do_upload_all)
        
        self.btn_save_cap = QPushButton(TRANSLATIONS[lang]['btn_save_caption'])
        self.btn_save_cap.setStyleSheet(
            'background-color: #e67e22; color: white; '
            'padding: 10px 20px; font-weight: bold; border-radius: 5px;'
        )
        self.btn_save_cap.clicked.connect(self.save_captions)
        
        self.btn_ok = QPushButton(TRANSLATIONS[lang]['btn_ok'])
        self.btn_ok.setStyleSheet(
            'background-color: #27ae60; color: white; '
            'padding: 10px 30px; font-weight: bold; border-radius: 5px;'
        )
        self.btn_ok.clicked.connect(self.accept)
        
        btn_layout.addWidget(self.btn_upload)
        btn_layout.addSpacing(10)
        btn_layout.addWidget(self.btn_save_cap)
        btn_layout.addSpacing(10)
        btn_layout.addWidget(self.btn_ok)
        btn_layout.addStretch()
        
        main_layout.addLayout(btn_layout)
        
        # Track slots
        self.subject_slots = []
        self.scene_slots = []
        
        # Add initial slot for each
        self.add_subject_slot()
        self.add_scene_slot()
    
    def add_subject_slot(self):
        """Add a new subject slot"""
        slot = ReferenceImageSlot(
            'cat_subject', 'MEDIA_CATEGORY_SUBJECT', 
            self, removable=True
        )
        slot.image_changed.connect(self.notify_update)
        slot.remove_requested.connect(self.remove_subject_slot)
        
        # Insert before stretch
        self.subjects_layout.insertWidget(
            self.subjects_layout.count() - 1, slot
        )
        self.subject_slots.append(slot)
        self.notify_update()
    
    def remove_subject_slot(self, slot):
        """Remove a subject slot"""
        if slot in self.subject_slots:
            self.subject_slots.remove(slot)
            slot.deleteLater()
            self.notify_update()
    
    def add_scene_slot(self):
        """Add a new scene slot"""
        slot = ReferenceImageSlot(
            'cat_scene', 'MEDIA_CATEGORY_SCENE',
            self, removable=True
        )
        slot.image_changed.connect(self.notify_update)
        slot.remove_requested.connect(self.remove_scene_slot)
        
        # Insert before stretch
        self.scenes_layout.insertWidget(
            self.scenes_layout.count() - 1, slot
        )
        self.scene_slots.append(slot)
        self.notify_update()
    
    def remove_scene_slot(self, slot):
        """Remove a scene slot"""
        if slot in self.scene_slots:
            self.scene_slots.remove(slot)
            slot.deleteLater()
            self.notify_update()
    
    def get_all_slots(self):
        """Get all slots"""
        return self.subject_slots + self.scene_slots + [self.style_slot]
    
    def notify_update(self):
        """Notify parent of changes"""
        count = sum(1 for s in self.get_all_slots() if s.image_path)
        self.images_updated.emit(count)
    
    def do_upload_all(self):
        """Upload all pending images"""
        slots_to_upload = [
            s for s in self.get_all_slots() 
            if s.image_path and not s.media_id
        ]
        
        if not slots_to_upload:
            QMessageBox.information(
                self, 'Info', 
                'All images already uploaded or no images selected.'
            )
            return
        
        # Disable button
        self.btn_upload.setEnabled(False)
        self.btn_upload.setText('Uploading...')
        
        self.upload_workers = []
        
        for slot in slots_to_upload:
            slot.set_upload_start()
            
            worker = UploadWorker(
                slot.image_path, slot.category_api_val,
                self.cookie, self.token
            )
            worker.finished.connect(
                lambda p, m, c, s=slot: s.set_upload_success(p, m, c)
            )
            worker.error.connect(
                lambda p, e, s=slot: s.set_upload_error(e)
            )
            worker.finished.connect(self.check_upload_complete)
            worker.error.connect(self.check_upload_complete)
            
            self.upload_workers.append(worker)
            worker.start()
    
    def check_upload_complete(self):
        """Check if all uploads done"""
        if all(not w.isRunning() for w in self.upload_workers):
            self.btn_upload.setEnabled(True)
            self.btn_upload.setText(TRANSLATIONS[self.lang]['btn_upload_analyze'])
            self.upload_workers.clear()
    
    def save_captions(self):
        """Save all metadata (no re-upload)"""
        count = 0
        for slot in self.get_all_slots():
            if slot.image_path:
                # Metadata already in slot widgets
                count += 1
        
        QMessageBox.information(
            self, 'Saved',
            f'Metadata saved for {count} image(s).'
        )
    
    def get_reference_data(self):
        """Get all reference data for generation"""
        data = []
        for slot in self.get_all_slots():
            slot_data = slot.get_data()
            if slot_data:
                data.append(slot_data)
        return data
    
    def update_language(self, lang):
        """Update language of all elements"""
        self.lang = lang
        self.setWindowTitle(TRANSLATIONS[lang]['ref_dialog_title'])
        
        # Update all slots
        for slot in self.get_all_slots():
            slot.update_lang(lang)
        
        # Update buttons
        self.btn_add_subject.setText(TRANSLATIONS[lang]['btn_add_subject'])
        self.btn_add_scene.setText(TRANSLATIONS[lang]['btn_add_scene'])
        self.btn_upload.setText(TRANSLATIONS[lang]['btn_upload_analyze'])
        self.btn_save_cap.setText(TRANSLATIONS[lang]['btn_save_caption'])
        self.btn_ok.setText(TRANSLATIONS[lang]['btn_ok'])


# ==================== TABLE CELL WIDGETS ====================

class ImageCellWidget(QWidget):
    """Widget for displaying generated images in table"""
    view_requested = Signal(str)
    delete_requested = Signal(str, str)
    
    def __init__(self, image_path, lang_code='en', parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.lang_code = lang_code
        self.original_pixmap = QPixmap(image_path)
        
        # Clickable label
        self.label = ClickableLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setCursor(Qt.PointingHandCursor)
        self.label.clicked.connect(
            lambda: self.view_requested.emit(self.image_path)
        )
        
        # Delete button
        self.delete_button = QPushButton(self)
        self.delete_button.setIcon(
            self.style().standardIcon(QStyle.SP_TrashIcon)
        )
        self.delete_button.setFixedSize(24, 24)
        self.delete_button.setStyleSheet(
            'background-color: rgba(231, 76, 60, 0.9); '
            'border-radius: 12px; border: 1px solid white;'
        )
        self.delete_button.clicked.connect(
            lambda: self.delete_requested.emit(self.image_path, self.lang_code)
        )
        
        l = QVBoxLayout(self)
        l.setContentsMargins(2, 2, 2, 2)
        l.addWidget(self.label)
        
        self.update_pixmap()
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_pixmap()
        self.delete_button.move(self.width() - 29, self.height() - 29)
    
    def update_pixmap(self):
        if not self.original_pixmap.isNull():
            w = self.width() - 4
            h = self.height() - 4
            if w > 0 and h > 0:
                scaled = self.original_pixmap.scaled(
                    w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self.label.setPixmap(scaled)
    
    def update_tooltip(self, lang):
        self.lang_code = lang
        self.delete_button.setToolTip(TRANSLATIONS[lang]['tooltip_delete'])


class PromptCellWidget(QWidget):
    """Editable prompt cell"""
    text_changed = Signal(str)
    
    def __init__(self, text='', parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.txt_edit = QPlainTextEdit(text)
        self.txt_edit.textChanged.connect(self.on_text_changed)
        layout.addWidget(self.txt_edit)
        
        # Edit button
        self.edit_button = QPushButton(self)
        icon_data = b'PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik0xNyAzYTIuODI4IDIuODI4IDAgMSAxIDQgNEw3LjUgMjAuNSAyIDIybDEuNS01LjVMMTcgM3oiPjwvcGF0aD48L3N2Zz4='
        img = QImage.fromData(base64.b64decode(icon_data))
        pix = QPixmap.fromImage(img)
        self.edit_button.setIcon(QIcon(pix))
        self.edit_button.setFixedSize(24, 24)
        self.edit_button.setStyleSheet(
            'background-color: rgba(52, 152, 219, 0.9); '
            'border-radius: 12px; border: 1px solid white;'
        )
        self.edit_button.clicked.connect(self.trigger_edit)
        self.edit_button.setToolTip('Edit Prompt')
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.edit_button.move(self.width() - 29, self.height() - 29)
    
    def trigger_edit(self):
        self.txt_edit.setFocus()
        self.txt_edit.moveCursor(QTextCursor.End)
    
    def on_text_changed(self):
        self.text_changed.emit(self.txt_edit.toPlainText())


class StatusCellWidget(QWidget):
    """Status cell with retry and folder buttons"""
    retry_requested = Signal()
    open_folder_requested = Signal()
    
    def __init__(self, lang_code='en', parent=None):
        super().__init__(parent)
        
        l = QVBoxLayout(self)
        l.setContentsMargins(5, 5, 5, 5)
        l.setAlignment(Qt.AlignCenter)
        
        self.lbl_status = QLabel()
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setWordWrap(True)
        l.addWidget(self.lbl_status)
        
        bl = QHBoxLayout()
        bl.setSpacing(4)
        
        self.btn_retry = QPushButton()
        self.btn_retry.setIcon(
            self.style().standardIcon(QStyle.SP_BrowserReload)
        )
        self.btn_retry.setFixedSize(28, 28)
        self.btn_retry.setStyleSheet(
            'background-color: #e67e22; border-radius: 4px;'
        )
        self.btn_retry.clicked.connect(self.retry_requested.emit)
        self.btn_retry.setVisible(False)
        
        self.btn_folder = QPushButton()
        self.btn_folder.setIcon(
            self.style().standardIcon(QStyle.SP_DirOpenIcon)
        )
        self.btn_folder.setFixedSize(28, 28)
        self.btn_folder.setStyleSheet(
            'background-color: #3498db; border-radius: 4px;'
        )
        self.btn_folder.clicked.connect(self.open_folder_requested.emit)
        self.btn_folder.setVisible(False)
        
        bl.addStretch()
        bl.addWidget(self.btn_retry)
        bl.addWidget(self.btn_folder)
        bl.addStretch()
        
        l.addLayout(bl)
        
        self.update_tooltips(lang_code)
    
    def update_tooltips(self, lang):
        self.btn_retry.setToolTip(TRANSLATIONS[lang]['tooltip_retry'])
        self.btn_folder.setToolTip(TRANSLATIONS[lang]['tooltip_folder'])
    
    def set_status(self, text, color='#333', show_retry=False, show_folder=False):
        self.lbl_status.setText(text)
        self.lbl_status.setStyleSheet(f'color: {color}; font-weight: bold;')
        self.btn_retry.setVisible(show_retry)
        self.btn_folder.setVisible(show_folder)


# ==================== MAIN WINDOW ====================

class BatchImageGenerator(QWidget):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        self.lang = 'en'  # Default language
        self.setWindowTitle(TRANSLATIONS[self.lang]['window_title'])
        self.resize(1350, 920)
        self.setStyleSheet(MODERN_STYLESHEET)
        
        if os.path.exists(ICON_FILE):
            self.setWindowIcon(QIcon(ICON_FILE))
        
        # Output directory
        self.output_directory = os.path.join(os.getcwd(), 'output')
        os.makedirs(self.output_directory, exist_ok=True)
        
        # State
        self.task_queue = queue.Queue()
        self.worker = None
        self.validator = None
        self.donate_url = ''
        self.current_num_images = 1
        self.current_token = None
        self.token_exp_timestamp = 0
        
        # Reference dialog
        self.ref_dialog = ReferenceDialog(self.lang, self)
        self.ref_dialog.images_updated.connect(self.update_ref_btn_text)
        
        # Timer for token display
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_token_display)
        
        # Build UI
        self.init_ui()
        
        # Load saved session
        self.load_last_session()
        
        # Update language buttons
        self.update_language_button_styles()
        
        # Load author info
        self.author_loader = AuthorInfoLoader()
        self.author_loader.data_loaded.connect(self.update_author_info)
        self.author_loader.start()
    
    def init_ui(self):
        """Initialize the user interface"""
        main_layout = QHBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # ===== LEFT PANEL =====
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        left.setMaximumWidth(450)
        
        # Header frame
        header_frame = QFrame()
        header_frame.setStyleSheet(
            '.QFrame { background-color: white; border-radius: 8px; '
            'border: 1px solid #e0e0e0; }'
        )
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(12, 12, 12, 12)
        
        header_info_layout = QHBoxLayout()
        
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        
        self.lbl_app = QLabel('Auto Whisk')
        self.lbl_app.setStyleSheet(
            'font-weight: bold; font-size: 18px; color: #2c3e50;'
        )
        
        self.lbl_auth = QLabel('Loading...')
        self.lbl_auth.setOpenExternalLinks(True)
        self.lbl_auth.setStyleSheet('color: #7f8c8d; font-size: 12px;')
        
        title_layout.addWidget(self.lbl_app)
        title_layout.addWidget(self.lbl_auth)
        
        self.btn_donate = QPushButton('☕ Buy Me a Coffee')
        self.btn_donate.setCursor(Qt.PointingHandCursor)
        self.btn_donate.setStyleSheet(
            'QPushButton { background-color: rgba(253, 214, 99, 0.2); '
            'color: #d4ac0d; border-radius: 15px; padding: 6px 12px; '
            'border: none; } '
            'QPushButton:hover { background-color: #fdd663; color: #000; }'
        )
        self.btn_donate.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(self.donate_url)) 
            if self.donate_url else None
        )
        self.btn_donate.setVisible(False)
        
        header_info_layout.addLayout(title_layout)
        header_info_layout.addStretch()
        header_info_layout.addWidget(self.btn_donate)
        
        header_layout.addLayout(header_info_layout)
        left_layout.addWidget(header_frame)
        
        # Language selector
        lang_layout = QHBoxLayout()
        
        self.btn_en = QPushButton('🇺🇸 English')
        self.btn_en.clicked.connect(lambda: self.change_language('en'))
        
        self.btn_tr = QPushButton('🇹🇷 Türkçe')
        self.btn_tr.clicked.connect(lambda: self.change_language('tr'))
        
        self.btn_vi = QPushButton('🇻🇳 Tiếng Việt')
        self.btn_vi.clicked.connect(lambda: self.change_language('vi'))
        
        lang_layout.addWidget(self.btn_en)
        lang_layout.addWidget(self.btn_tr)
        lang_layout.addWidget(self.btn_vi)
        
        left_layout.addLayout(lang_layout)
        
        # Auth group
        self.grp_auth = QGroupBox(TRANSLATIONS[self.lang]['grp_auth'])
        auth_layout = QVBoxLayout()
        auth_layout.setSpacing(8)
        auth_layout.setContentsMargins(10, 10, 10, 15)
        
        self.lbl_instr = QLabel(TRANSLATIONS[self.lang]['instr_cookie'])
        self.lbl_instr.setStyleSheet('color: #666; font-style: italic;')
        
        self.txt_cookie = QPlainTextEdit()
        self.txt_cookie.setMaximumHeight(60)
        self.txt_cookie.setPlaceholderText(
            TRANSLATIONS[self.lang]['placeholder_cookie']
        )
        
        auth_btn_layout = QHBoxLayout()
        
        self.btn_help = QPushButton(TRANSLATIONS[self.lang]['link_help'])
        self.btn_help.setIcon(
            self.style().standardIcon(QStyle.SP_MessageBoxQuestion)
        )
        self.btn_help.setStyleSheet(
            'background-color: #2980b9; color: white; '
            'padding: 8px; text-align: left;'
        )
        self.btn_help.clicked.connect(self.open_help)
        
        self.btn_check = QPushButton(TRANSLATIONS[self.lang]['btn_check'])
        self.btn_check.setStyleSheet(
            'background-color: #9b59b6; padding: 8px; '
            'color: white; font-weight: bold;'
        )
        self.btn_check.clicked.connect(self.check_cookie)
        
        auth_btn_layout.addWidget(self.btn_help, 1)
        auth_btn_layout.addSpacing(10)
        auth_btn_layout.addWidget(self.btn_check, 2)
        
        auth_layout.addWidget(self.lbl_instr)
        auth_layout.addWidget(self.txt_cookie)
        auth_layout.addLayout(auth_btn_layout)
        
        self.grp_auth.setLayout(auth_layout)
        left_layout.addWidget(self.grp_auth)
        
        # Info group
        self.grp_info = QGroupBox(TRANSLATIONS[self.lang]['grp_info'])
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(10, 10, 10, 15)
        
        self.txt_info = QPlainTextEdit()
        self.txt_info.setReadOnly(True)
        self.txt_info.setStyleSheet(
            'font-family: Consolas; font-size: 12px; '
            'background: #f8f9fa; border: none;'
        )
        self.txt_info.setMaximumHeight(80)
        self.txt_info.setPlaceholderText(
            TRANSLATIONS[self.lang]['info_placeholder']
        )
        
        info_layout.addWidget(self.txt_info)
        self.grp_info.setLayout(info_layout)
        left_layout.addWidget(self.grp_info)
        
        # Config group
        self.grp_conf = QGroupBox(TRANSLATIONS[self.lang]['grp_config'])
        conf_layout = QVBoxLayout()
        conf_layout.setSpacing(8)
        conf_layout.setContentsMargins(10, 10, 10, 15)
        
        # Aspect ratio and count
        self.lbl_rat = QLabel(TRANSLATIONS[self.lang]['lbl_ratio'])
        self.cbo_rat = QComboBox()
        for k, v in RATIO_DATA:
            self.cbo_rat.addItem(TRANSLATIONS[self.lang][k], v)
        
        self.lbl_num = QLabel(TRANSLATIONS[self.lang]['lbl_num_images'])
        self.cbo_num = QComboBox()
        self.cbo_num.addItems([str(i) for i in range(1, 5)])
        
        row_opt = QHBoxLayout()
        vr = QVBoxLayout()
        vr.setSpacing(2)
        vr.addWidget(self.lbl_rat)
        vr.addWidget(self.cbo_rat)
        
        vn = QVBoxLayout()
        vn.setSpacing(2)
        vn.addWidget(self.lbl_num)
        vn.addWidget(self.cbo_num)
        
        row_opt.addLayout(vr, 1)
        row_opt.addSpacing(10)
        row_opt.addLayout(vn, 1)
        
        conf_layout.addLayout(row_opt)
        
        # Reference images button
        self.btn_ref = QPushButton(TRANSLATIONS[self.lang]['btn_ref'])
        self.btn_ref.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        self.btn_ref.setStyleSheet(
            'background-color: #8e44ad; color: white; padding: 8px;'
        )
        self.btn_ref.clicked.connect(self.open_reference_dialog)
        conf_layout.addWidget(self.btn_ref)
        
        # Prompts
        self.lbl_prompts = QLabel(TRANSLATIONS[self.lang]['lbl_prompts'])
        conf_layout.addWidget(self.lbl_prompts)
        
        self.txt_prompts = QPlainTextEdit()
        self.txt_prompts.setPlaceholderText(
            TRANSLATIONS[self.lang]['placeholder_prompts']
        )
        self.txt_prompts.setMinimumHeight(150)
        conf_layout.addWidget(self.txt_prompts)
        
        # Import button
        self.btn_import = QPushButton(TRANSLATIONS[self.lang]['btn_import'])
        self.btn_import.setIcon(self.style().standardIcon(QStyle.SP_FileDialogStart))
        self.btn_import.setStyleSheet(
            'background-color: #16a085; color: white; padding: 6px;'
        )
        self.btn_import.clicked.connect(self.import_prompts)
        conf_layout.addWidget(self.btn_import)
        
        # Output folder
        out_layout = QHBoxLayout()
        self.lbl_out = QLabel(TRANSLATIONS[self.lang]['lbl_output'])
        self.txt_out = QLineEdit(self.output_directory)
        self.btn_browse = QPushButton(TRANSLATIONS[self.lang]['btn_browse'])
        self.btn_browse.setStyleSheet(
            'background-color: #34495e; color: white; padding: 6px;'
        )
        self.btn_browse.clicked.connect(self.browse_output)
        
        out_layout.addWidget(self.lbl_out)
        out_layout.addWidget(self.txt_out, 1)
        out_layout.addWidget(self.btn_browse)
        
        conf_layout.addLayout(out_layout)
        
        # Auto-open checkbox
        self.chk_auto_open = QCheckBox(
            TRANSLATIONS[self.lang]['chk_auto_open']
        )
        self.chk_auto_open.setChecked(True)
        conf_layout.addWidget(self.chk_auto_open)
        
        self.grp_conf.setLayout(conf_layout)
        left_layout.addWidget(self.grp_conf)
        
        # Control buttons
        self.btn_start = QPushButton(TRANSLATIONS[self.lang]['btn_start'])
        self.btn_start.setStyleSheet(
            'background-color: #27ae60; color: white; font-size: 14px; '
            'padding: 12px; font-weight: bold;'
        )
        self.btn_start.clicked.connect(self.start_generation)
        
        self.btn_stop = QPushButton(TRANSLATIONS[self.lang]['btn_stop'])
        self.btn_stop.setStyleSheet(
            'background-color: #e74c3c; color: white; font-size: 14px; '
            'padding: 12px; font-weight: bold;'
        )
        self.btn_stop.clicked.connect(self.stop_generation)
        self.btn_stop.setVisible(False)
        
        self.btn_pause = QPushButton(TRANSLATIONS[self.lang]['btn_pause'])
        self.btn_pause.setStyleSheet(
            'background-color: #f39c12; color: white; font-size: 14px; '
            'padding: 12px; font-weight: bold;'
        )
        self.btn_pause.clicked.connect(self.toggle_pause)
        self.btn_pause.setVisible(False)
        
        left_layout.addWidget(self.btn_start)
        left_layout.addWidget(self.btn_stop)
        left_layout.addWidget(self.btn_pause)
        left_layout.addStretch()
        
        # ===== RIGHT PANEL (Table) =====
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setValue(0)
        right_layout.addWidget(self.progress)
        
        # Results table
        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(False)
        
        right_layout.addWidget(self.table)
        
        # Bottom buttons
        bottom_layout = QHBoxLayout()
        
        self.btn_retry_errors = QPushButton(
            TRANSLATIONS[self.lang]['btn_retry_errors']
        )
        self.btn_retry_errors.setStyleSheet(
            'background-color: #e67e22; color: white; padding: 8px;'
        )
        self.btn_retry_errors.clicked.connect(self.retry_all_errors)
        self.btn_retry_errors.setVisible(False)
        
        self.btn_open_folder = QPushButton(
            TRANSLATIONS[self.lang]['btn_open_folder']
        )
        self.btn_open_folder.setStyleSheet(
            'background-color: #3498db; color: white; padding: 8px;'
        )
        self.btn_open_folder.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl.fromLocalFile(self.output_directory)
            )
        )
        
        bottom_layout.addWidget(self.btn_retry_errors)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.btn_open_folder)
        
        right_layout.addLayout(bottom_layout)
        
        # Add panels to splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

    
    # ==================== MAIN WINDOW METHODS ====================
    
    def update_author_info(self, data):
        """Update author info from loaded data"""
        try:
            author_name = data.get('author', {}).get('name', 'Duck Martians')
            author_github = data.get('author', {}).get('github', 'https://github.com/duckmartians')
            self.donate_url = data.get('donate_url', '')
            
            self.lbl_auth.setText(
                f'by <a href="{author_github}" style="color: #3498db; text-decoration: none;">{author_name}</a>'
            )
            
            if self.donate_url:
                self.btn_donate.setVisible(True)
        except:
            pass
    
    def change_language(self, lang):
        """Change application language"""
        self.lang = lang
        
        # Update all UI text
        self.setWindowTitle(TRANSLATIONS[lang]['window_title'])
        self.grp_auth.setTitle(TRANSLATIONS[lang]['grp_auth'])
        self.grp_info.setTitle(TRANSLATIONS[lang]['grp_info'])
        self.grp_conf.setTitle(TRANSLATIONS[lang]['grp_config'])
        
        self.lbl_instr.setText(TRANSLATIONS[lang]['instr_cookie'])
        self.txt_cookie.setPlaceholderText(TRANSLATIONS[lang]['placeholder_cookie'])
        self.btn_check.setText(TRANSLATIONS[lang]['btn_check'])
        self.btn_help.setText(TRANSLATIONS[lang]['link_help'])
        
        self.txt_info.setPlaceholderText(TRANSLATIONS[lang]['info_placeholder'])
        
        self.lbl_rat.setText(TRANSLATIONS[lang]['lbl_ratio'])
        self.lbl_num.setText(TRANSLATIONS[lang]['lbl_num_images'])
        
        # Update combo items
        for i, (k, v) in enumerate(RATIO_DATA):
            self.cbo_rat.setItemText(i, TRANSLATIONS[lang][k])
        
        self.btn_ref.setText(TRANSLATIONS[lang]['btn_ref'])
        self.lbl_prompts.setText(TRANSLATIONS[lang]['lbl_prompts'])
        self.txt_prompts.setPlaceholderText(TRANSLATIONS[lang]['placeholder_prompts'])
        self.btn_import.setText(TRANSLATIONS[lang]['btn_import'])
        
        self.lbl_out.setText(TRANSLATIONS[lang]['lbl_output'])
        self.btn_browse.setText(TRANSLATIONS[lang]['btn_browse'])
        self.chk_auto_open.setText(TRANSLATIONS[lang]['chk_auto_open'])
        
        self.btn_start.setText(TRANSLATIONS[lang]['btn_start'])
        self.btn_stop.setText(TRANSLATIONS[lang]['btn_stop'])
        self.btn_pause.setText(TRANSLATIONS[lang]['btn_pause'])
        self.btn_retry_errors.setText(TRANSLATIONS[lang]['btn_retry_errors'])
        self.btn_open_folder.setText(TRANSLATIONS[lang]['btn_open_folder'])
        
        # Update reference dialog
        self.ref_dialog.update_language(lang)
        
        # Update button styles
        self.update_language_button_styles()
        
        # Save preference
        try:
            with open(AUTH_FILE, 'r') as f:
                data = json.load(f)
            data['lang'] = lang
            with open(AUTH_FILE, 'w') as f:
                json.dump(data, f)
        except:
            pass
    
    def update_language_button_styles(self):
        """Update language button styles based on selection"""
        active_style = 'background-color: #3498db; color: white; padding: 6px; font-weight: bold;'
        inactive_style = 'background-color: #ecf0f1; color: #7f8c8d; padding: 6px;'
        
        self.btn_en.setStyleSheet(active_style if self.lang == 'en' else inactive_style)
        self.btn_tr.setStyleSheet(active_style if self.lang == 'tr' else inactive_style)
        self.btn_vi.setStyleSheet(active_style if self.lang == 'vi' else inactive_style)
    
    def check_cookie(self):
        """Validate cookie and get token"""
        cookie_input = self.txt_cookie.toPlainText().strip()
        
        if not cookie_input:
            QMessageBox.warning(self, 'Error', 'Please enter cookie!')
            return
        
        self.btn_check.setEnabled(False)
        self.btn_check.setText('Checking...')
        
        self.validator = CookieValidatorWorker(cookie_input)
        self.validator.result_signal.connect(self.handle_validation_result)
        self.validator.start()
    
    def handle_validation_result(self, success, token, exp_timestamp):
        """Handle cookie validation result"""
        self.btn_check.setEnabled(True)
        self.btn_check.setText(TRANSLATIONS[self.lang]['btn_check'])
        
        if success:
            self.current_token = token
            self.token_exp_timestamp = exp_timestamp
            
            # Update reference dialog
            self.ref_dialog.cookie = self.txt_cookie.toPlainText().strip()
            self.ref_dialog.token = token
            
            # Save to file
            try:
                with open(AUTH_FILE, 'w') as f:
                    json.dump({
                        'cookie': self.txt_cookie.toPlainText().strip(),
                        'token': token,
                        'exp': exp_timestamp,
                        'lang': self.lang
                    }, f)
            except:
                pass
            
            # Update display
            self.update_token_display()
            self.timer.start(60000)  # Update every minute
            
            exp_str = datetime.fromtimestamp(exp_timestamp).strftime('%Y-%m-%d %H:%M:%S') if exp_timestamp else 'Unknown'
            
            QMessageBox.information(
                self, 'Success',
                TRANSLATIONS[self.lang]['alert_cookie_valid'] + exp_str
            )
        else:
            self.txt_info.setPlainText('')
            QMessageBox.critical(
                self, 'Error',
                TRANSLATIONS[self.lang]['alert_cookie_invalid']
            )
    
    def update_token_display(self):
        """Update token expiry display"""
        if not self.token_exp_timestamp:
            return
        
        now = int(time.time())
        remaining = self.token_exp_timestamp - now
        
        if remaining < 0:
            self.txt_info.setPlainText('⚠️ Token expired! Please check cookie again.')
            self.txt_info.setStyleSheet('background: #fee; color: #c00;')
            self.timer.stop()
        else:
            hours = remaining // 3600
            minutes = (remaining % 3600) // 60
            self.txt_info.setPlainText(
                f'✅ Token valid\n'
                f'Expires in: {hours}h {minutes}m'
            )
            self.txt_info.setStyleSheet('background: #efe; color: #060;')
    
    def open_help(self):
        """Open help URL"""
        QDesktopServices.openUrl(QUrl(TRANSLATIONS[self.lang]['help_url']))
    
    def update_ref_btn_text(self, count):
        """Update reference button text with count"""
        base_text = TRANSLATIONS[self.lang]['btn_ref']
        if count > 0:
            self.btn_ref.setText(f'{base_text} ({count})')
        else:
            self.btn_ref.setText(base_text)
    
    def open_reference_dialog(self):
        """Open reference images dialog"""
        # Update cookie/token
        self.ref_dialog.cookie = self.txt_cookie.toPlainText().strip()
        self.ref_dialog.token = self.current_token
        
        self.ref_dialog.exec()
    
    def import_prompts(self):
        """Import prompts from text file"""
        path, _ = QFileDialog.getOpenFileName(
            self, 'Import Prompts', '', 'Text Files (*.txt)'
        )
        
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.txt_prompts.setPlainText(f.read())
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to read file:\n{str(e)}')
    
    def browse_output(self):
        """Browse for output directory"""
        path = QFileDialog.getExistingDirectory(
            self, 'Select Output Directory', self.output_directory
        )
        
        if path:
            self.output_directory = path
            self.txt_out.setText(path)
    
    def start_generation(self):
        """Start image generation"""
        # Validate
        prompts_text = self.txt_prompts.toPlainText().strip()
        if not prompts_text:
            QMessageBox.warning(
                self, 'Warning',
                TRANSLATIONS[self.lang]['alert_no_prompts']
            )
            return
        
        if not self.current_token:
            QMessageBox.warning(
                self, 'Warning',
                TRANSLATIONS[self.lang]['alert_no_token']
            )
            return
        
        # Parse prompts
        prompts = [p.strip() for p in prompts_text.split('\n') if p.strip()]
        
        # Get settings
        aspect_ratio = self.cbo_rat.currentData()
        num_images = int(self.cbo_num.currentText())
        self.current_num_images = num_images
        
        # Get reference data
        ref_data = self.ref_dialog.get_reference_data()
        
        # Apply smart filtering for display
        if ref_data:
            print(f"\n{'='*60}")
            print(f"SMART FILTERING PREVIEW")
            print(f"{'='*60}")
            print(f"Total references loaded: {len(ref_data)}\n")
            
            for i, prompt in enumerate(prompts[:3], 1):  # Show first 3
                filtered = smart_filter_references(prompt, ref_data)
                print(f"{i}. Prompt: \"{prompt[:50]}...\"" if len(prompt) > 50 else f"{i}. Prompt: \"{prompt}\"")
                print(f"   → {len(filtered)}/{len(ref_data)} references selected")
                for ref in filtered:
                    name = ref.get('name', 'Unnamed')
                    cat = ref.get('category', '').replace('MEDIA_CATEGORY_', '')
                    print(f"      • {cat}: {name}")
                print()
        
        # Setup table
        self.setup_table(prompts, num_images)
        
        # Clear queue
        while not self.task_queue.empty():
            try:
                self.task_queue.get_nowait()
            except:
                break
        
        # Add tasks
        for idx, prompt in enumerate(prompts):
            # Apply smart filtering per prompt
            if ref_data:
                filtered_refs = smart_filter_references(prompt, ref_data)
                print(f"Row {idx+1}: {len(filtered_refs)} refs selected for \"{prompt[:40]}...\"")
            else:
                filtered_refs = []
            
            # Store filtered refs for this prompt
            self.task_queue.put((idx, prompt))
        
        # Create worker with ALL reference data (filtering happens per-prompt in worker)
        model_settings = {
            'imageModel': 'imagen-3.0-generate-001',
            'aspectRatio': aspect_ratio
        }
        
        self.worker = QueueWorker(
            self.task_queue,
            model_settings,
            self.output_directory,
            num_images,
            ref_data,  # Pass all refs, worker will filter per-prompt
            self.txt_cookie.toPlainText().strip(),
            self.current_token
        )
        
        # Connect signals
        self.worker.task_started.connect(self.on_task_started)
        self.worker.task_success.connect(self.on_task_success)
        self.worker.task_failed.connect(self.on_task_failed)
        self.worker.all_done.connect(self.on_all_done)
        
        # Start
        self.worker.start()
        
        # Update UI
        self.btn_start.setVisible(False)
        self.btn_stop.setVisible(True)
        self.btn_pause.setVisible(True)
        self.txt_prompts.setEnabled(False)
        self.cbo_rat.setEnabled(False)
        self.cbo_num.setEnabled(False)
        self.btn_ref.setEnabled(False)
        self.btn_import.setEnabled(False)
    
    def stop_generation(self):
        """Stop generation"""
        if self.worker:
            self.worker.stop()
    
    def toggle_pause(self):
        """Toggle pause state"""
        if not self.worker:
            return
        
        if self.worker.is_paused:
            self.worker.resume()
            self.btn_pause.setText(TRANSLATIONS[self.lang]['btn_pause'])
        else:
            self.worker.pause()
            self.btn_pause.setText(TRANSLATIONS[self.lang]['btn_resume'])
    
    def retry_all_errors(self):
        """Retry all failed rows"""
        error_rows = []
        for row in range(self.table.rowCount()):
            status_widget = self.table.cellWidget(row, self.current_num_images + 1)
            if status_widget and status_widget.btn_retry.isVisible():
                error_rows.append(row)
        
        if not error_rows:
            return
        
        # Re-queue failed tasks
        prompts_text = self.txt_prompts.toPlainText().strip()
        prompts = [p.strip() for p in prompts_text.split('\n') if p.strip()]
        
        for row_idx in error_rows:
            if row_idx < len(prompts):
                self.task_queue.put((row_idx, prompts[row_idx]))
        
        # Hide retry button
        self.btn_retry_errors.setVisible(False)
    
    def setup_table(self, prompts, num_images):
        """Setup results table"""
        self.table.clear()
        self.table.setRowCount(len(prompts))
        self.table.setColumnCount(num_images + 2)  # Prompt + Images + Status
        
        headers = ['Prompt'] + [f'Image {i+1}' for i in range(num_images)] + ['Status']
        self.table.setHorizontalHeaderLabels(headers)
        
        # Set column widths
        self.table.setColumnWidth(0, 300)
        for i in range(1, num_images + 1):
            self.table.setColumnWidth(i, 120)
        self.table.setColumnWidth(num_images + 1, 150)
        
        # Fill prompts
        for row, prompt in enumerate(prompts):
            prompt_widget = PromptCellWidget(prompt)
            self.table.setCellWidget(row, 0, prompt_widget)
            self.table.setRowHeight(row, 100)
            
            # Empty image cells
            for col in range(1, num_images + 1):
                self.table.setItem(row, col, QTableWidgetItem(''))
            
            # Status cell
            status_widget = StatusCellWidget(self.lang)
            status_widget.set_status(TRANSLATIONS[self.lang]['status_idle'], '#999')
            self.table.setCellWidget(row, num_images + 1, status_widget)
        
        self.progress.setValue(0)
        self.progress.setMaximum(len(prompts) * num_images)
    
    def on_task_started(self, row_idx, status_text):
        """Handle task started"""
        status_widget = self.table.cellWidget(row_idx, self.current_num_images + 1)
        if status_widget:
            status_widget.set_status(
                f"{TRANSLATIONS[self.lang]['status_running']} {status_text}",
                '#3498db'
            )
    
    def on_task_success(self, row_idx, col_idx, file_path):
        """Handle task success"""
        # Add image
        img_widget = ImageCellWidget(file_path, self.lang)
        self.table.setCellWidget(row_idx, col_idx, img_widget)
        
        # Update progress
        current = self.progress.value() + 1
        self.progress.setValue(current)
        
        # Check if row complete
        all_done = True
        for c in range(1, self.current_num_images + 1):
            if not self.table.cellWidget(row_idx, c):
                all_done = False
                break
        
        if all_done:
            status_widget = self.table.cellWidget(row_idx, self.current_num_images + 1)
            if status_widget:
                status_widget.set_status(
                    TRANSLATIONS[self.lang]['status_done'],
                    '#27ae60', False, True
                )
    
    def on_task_failed(self, row_idx, col_idx, error_msg):
        """Handle task failure"""
        # Update progress
        current = self.progress.value() + 1
        self.progress.setValue(current)
        
        # Update status
        status_widget = self.table.cellWidget(row_idx, self.current_num_images + 1)
        if status_widget:
            status_widget.set_status(
                f"{TRANSLATIONS[self.lang]['status_error']}: {error_msg}",
                '#e74c3c', True, False
            )
            self.btn_retry_errors.setVisible(True)
    
    def on_all_done(self):
        """Handle all tasks complete"""
        self.btn_start.setVisible(True)
        self.btn_stop.setVisible(False)
        self.btn_pause.setVisible(False)
        self.txt_prompts.setEnabled(True)
        self.cbo_rat.setEnabled(True)
        self.cbo_num.setEnabled(True)
        self.btn_ref.setEnabled(True)
        self.btn_import.setEnabled(True)
        
        if self.chk_auto_open.isChecked():
            QDesktopServices.openUrl(
                QUrl.fromLocalFile(self.output_directory)
            )
    
    def load_last_session(self):
        """Load last saved session"""
        try:
            if os.path.exists(AUTH_FILE):
                with open(AUTH_FILE, 'r') as f:
                    data = json.load(f)
                
                self.txt_cookie.setPlainText(data.get('cookie', ''))
                self.current_token = data.get('token')
                self.token_exp_timestamp = data.get('exp', 0)
                
                saved_lang = data.get('lang', 'en')
                if saved_lang in TRANSLATIONS:
                    self.change_language(saved_lang)
                
                if self.current_token:
                    self.ref_dialog.cookie = data.get('cookie', '')
                    self.ref_dialog.token = self.current_token
                    self.update_token_display()
                    self.timer.start(60000)
        except:
            pass


# ==================== MAIN ====================

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BatchImageGenerator()
    window.show()
    sys.exit(app.exec())

