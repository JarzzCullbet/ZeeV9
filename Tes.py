#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║                ELITE FB CREATOR - ENHANCED SYSTEM            ║
║             Pancingan + Tinyhost + Desktop OTP               ║
║              Developer: ZeeTheFounder - Ultra                ║
╚══════════════════════════════════════════════════════════════╝
"""

import sys
import time
import re
import random
import string
import sqlite3
import os
import json
import uuid
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from contextlib import contextmanager
from faker import Faker
from fake_useragent import UserAgent
import threading
from queue import Queue, Empty

# =============================================================================
# CONFIGURATION
# =============================================================================
W = 60  # Terminal width
OUTPUT_FILE = "/sdcard/akunw.txt"
LOG_FILE = "/sdcard/fb_creator_logs.txt"
DB_FILE = "domains.db"
CONFIG_FILE = "config.json"
SHORTCUTS_FILE = "shortcuts.json"
API_BASE = "https://tinyhost.shop/api"
DOMAINS_PER_PAGE = 150  # Ditingkatkan dari 20 ke 150

# Enhanced Color Palette - Ultra Hardstyle
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"
    
    # Primary Colors
    PURPLE1 = "\033[38;5;93m"
    PURPLE2 = "\033[38;5;99m"
    PURPLE3 = "\033[38;5;135m"
    PURPLE4 = "\033[38;5;141m"
    PURPLE5 = "\033[38;5;177m"
    PINK = "\033[38;5;213m"
    MAGENTA = "\033[38;5;201m"
    CYAN = "\033[38;5;51m"
    WHITE = "\033[38;5;231m"
    GRAY = "\033[38;5;240m"
    GREEN = "\033[38;5;46m"
    RED = "\033[38;5;196m"
    YELLOW = "\033[38;5;226m"
    BLUE = "\033[38;5;39m"
    ORANGE = "\033[38;5;214m"
    
    # Backgrounds
    BG_PURPLE = "\033[48;5;93m"
    BG_PINK = "\033[48;5;213m"
    BG_RED = "\033[48;5;196m"
    BG_GREEN = "\033[48;5;46m"
    BG_BLUE = "\033[48;5;39m"
    BG_YELLOW = "\033[48;5;226m"

# Short aliases for colors
R = Colors.RESET
B = Colors.BOLD
D = Colors.DIM
U = Colors.UNDERLINE
P1 = Colors.PURPLE1
P2 = Colors.PURPLE2
P3 = Colors.PURPLE3
P4 = Colors.PURPLE4
P5 = Colors.PURPLE5
PK = Colors.PINK
MG = Colors.MAGENTA
CY = Colors.CYAN
WH = Colors.WHITE
GR = Colors.GRAY
GN = Colors.GREEN
RD = Colors.RED
YL = Colors.YELLOW
BL = Colors.BLUE
OR = Colors.ORANGE
BG1 = Colors.BG_PURPLE
BG2 = Colors.BG_PINK
BG3 = Colors.BG_RED
BG4 = Colors.BG_GREEN
BG5 = Colors.BG_BLUE
BG6 = Colors.BG_YELLOW

# Default Config
DEFAULT_CONFIG = {
    "endpoint": "desktop",
    "gender": "random",
    "password_type": "auto",
    "custom_password": "",
    "min_age": 18,
    "max_age": 35,
    "account_limit": 10,
    "otp_timeout": 15,
    "otp_check_interval": 1,
    "name_type": "filipino"
}

config = DEFAULT_CONFIG.copy()
fake_id = Faker('id_ID')
lock = threading.Lock()
log_lock = threading.Lock()

# Worker Queues
creation_queue = Queue()
monitor_queue = Queue()
verify_queue = Queue()

# Enhanced Statistics with Live Data
stats = {
    "total_created": 0,
    "total_verified": 0,
    "total_with_cookies": 0,
    "total_failed": 0,
    "worker1_status": "Idle",
    "worker2_status": "Idle",
    "worker3_status": "Idle",
    "ok_count": 0,
    "cp_count": 0,
    "rejected_count": 0,
    "current_account": None,
    "last_success": None,
    "success_rate": 0.0,
    "current_process": "Waiting...",
    "current_email": "None",
    "current_pancingan": "None",
    "start_time": None
}

# =============================================================================
# ENHANCED UI SYSTEM - ULTRA DESIGN
# =============================================================================

def clear():
    """Clear terminal screen"""
    os.system('clear' if os.name != 'nt' else 'cls')

def loading_animation(text, duration=2, color=PK):
    """Enhanced loading animation with gradient"""
    frames = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']
    gradient = [P1, P2, P3, P4, P5, PK, MG, CY]
    end_time = time.time() + duration
    i = 0
    
    while time.time() < end_time:
        frame_color = gradient[i % len(gradient)]
        frame = frames[i % len(frames)]
        sys.stdout.write(f"\r{frame_color}{frame}{R} {color}{text}{R}")
        sys.stdout.flush()
        time.sleep(0.12)
        i += 1
    
    sys.stdout.write(f"\r{GN}✓{R} {B}{text}... {GN}Done{R}\n")
    sys.stdout.flush()

def print_box_title(title, width=W, color=P3):
    """Print box title with borders"""
    border = "═" * (width - 4)
    print(f"{color}╔{border}╗{R}")
    
    # Calculate padding for title
    title_len = len(re.sub(r'\033\[[0-9;]+m', '', title))
    left_pad = (width - 4 - title_len) // 2
    right_pad = width - 4 - title_len - left_pad
    
    print(f"{color}║{R}{' ' * left_pad}{title}{' ' * right_pad}{color}║{R}")

def print_box_content(lines, width=W, color=P3):
    """Print box content with borders"""
    for line in lines:
        clean_len = len(re.sub(r'\033\[[0-9;]+m', '', line))
        padding = width - 4 - clean_len
        print(f"{color}║{R} {line}{' ' * padding} {color}║{R}")

def print_box_bottom(width=W, color=P3):
    """Print box bottom border"""
    border = "═" * (width - 4)
    print(f"{color}╚{border}╝{R}")

def box(title, lines=None, width=W, color=P3, show_top=True, show_bottom=True):
    """Enhanced box with custom borders"""
    border = "═" * (width - 4)
    
    if show_top:
        print(f"{color}╔{border}╗{R}")
    
    # Title
    title_len = len(re.sub(r'\033\[[0-9;]+m', '', title))
    left_pad = (width - 4 - title_len) // 2
    right_pad = width - 4 - title_len - left_pad
    print(f"{color}║{R}{' ' * left_pad}{B}{WH}{title}{R}{' ' * right_pad}{color}║{R}")
    
    if lines:
        # Separator
        print(f"{color}╠{border}╣{R}")
        
        for line in lines:
            clean_len = len(re.sub(r'\033\[[0-9;]+m', '', line))
            padding = width - 4 - clean_len
            print(f"{color}║{R} {line}{' ' * padding} {color}║{R}")
    
    if show_bottom:
        print(f"{color}╚{border}╝{R}")

def divider(char="─", length=W, color=GR):
    """Enhanced divider with gradient"""
    print(f"{color}{char * length}{R}")

def print_header(text, width=W, color1=P1, color2=PK):
    """Enhanced header with gradient effect"""
    gradient = [color1, color2]
    border_top = "╔" + "═" * (width - 2) + "╗"
    border_bottom = "╚" + "═" * (width - 2) + "╝"
    
    print(f"{color1}{border_top}{R}")
    
    # Center text
    text_len = len(re.sub(r'\033\[[0-9;]+m', '', text))
    left_pad = (width - 2 - text_len) // 2
    right_pad = width - 2 - text_len - left_pad
    
    line = f"{' ' * left_pad}{B}{text}{R}{' ' * right_pad}"
    colored_line = ""
    for i, char in enumerate(line):
        color_idx = i % len(gradient)
        colored_line += f"{gradient[color_idx]}{char}"
    
    print(f"{color1}║{R}{colored_line}{color1}║{R}")
    print(f"{color1}{border_bottom}{R}")

def print_status(message, status_type="info"):
    """Print status message with icon and color"""
    icons = {
        "info": f"{BL}ℹ",
        "success": f"{GN}✓",
        "warning": f"{YL}⚠",
        "error": f"{RD}✗",
        "process": f"{CY}↻"
    }
    
    colors = {
        "info": BL,
        "success": GN,
        "warning": YL,
        "error": RD,
        "process": CY
    }
    
    icon = icons.get(status_type, f"{BL}ℹ")
    color = colors.get(status_type, BL)
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{GR}[{timestamp}]{R} {icon}{R} {color}{message}{R}")

def print_progress_bar(iteration, total, prefix='', suffix='', length=40, fill='█'):
    """Display progress bar"""
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = f"{P3}{fill * filled_length}{P1}{'░' * (length - filled_length)}{R}"
    
    # Use carriage return to update the same line
    sys.stdout.write(f'\r{prefix} {bar} {percent}% {suffix}')
    sys.stdout.flush()
    
    # Print new line on completion
    if iteration == total: 
        print()

def enhanced_banner():
    """Ultra Hardstyle Banner with ASCII Art"""
    clear()
    
    banner_art = [
        f"{P1}╔═══════════════════════════════════════════════════════════╗",
        f"{P1}║{P2}▗▄▄▖ ▗▄▄▖▗▄▖  ▗▄▄▖▗▄▄▄▖ ▗▄▖  ▗▄▄▖ ▗▄▄▖  ▗▄▄▖ ▗▄▄▄▖ ▗▄▄▄▖{P1}║",
        f"{P1}║{P3}▐▌ ▐▌▐▌  ▐▌ ▐▌▐▌   █   ▐▌ ▐▌ ▐▌  ▐▌  ▐▌▐▌  ▐▌  █     █  {P1}║",
        f"{P1}║{P4}▐▌▝▜▌▐▌   ▀▀ ▐▌    █   ▐▌▝▜▌ ▐▌  ▐▌▝▜▌ ▐▌▝▜▌  █     █  {P1}║",
        f"{P1}║{P5}▐▌ ▐▌▐▌   ▗▄▖▐▌    █   ▐▌ ▐▌ ▐▌  ▐▌ ▐▌ ▐▌ ▐▌  █     █  {P1}║",
        f"{P1}║{PK}▝▘ ▝▘▝▚▘▘▝▘ ▝▘▝▚▘▘  ▘   ▝▘ ▝▘ ▝▚▘▘▝▘ ▝▘ ▝▘ ▝▘  ▘     ▘  {P1}║",
        f"{P1}║{P2}═══════════════════════════════════════════════════════{P1}║",
        f"{P1}║{MG}         ELITE FACEBOOK CREATOR - ULTRA EDITION        {P1}║",
        f"{P1}║{CY}       Pancingan → Tinyhost → OTP → Cookies           {P1}║",
        f"{P1}╚═══════════════════════════════════════════════════════════╝{R}",
        "",
        f"{P3}╔═══════════════════════════════════════════════════════════╗{R}",
        f"{P3}║{R}      {B}{PK}Developer: ZeeTheFounder • Version: Ultra{R}       {P3}║{R}",
        f"{P3}╚═══════════════════════════════════════════════════════════╝{R}",
        ""
    ]
    
    for line in banner_art:
        print(line)
        time.sleep(0.05)

def banner():
    """Main banner display"""
    enhanced_banner()

def get_input(prompt):
    """Get user input with stylish prompt"""
    sys.stdout.write(f"{P4}┌─[{BL}INPUT{R}]\n{P4}└──╼ {B}{WH}{prompt}: {R}")
    sys.stdout.flush()
    return input().strip()

# =============================================================================
# LOGGING SYSTEM - ENHANCED
# =============================================================================

def write_log(message, level="INFO"):
    """Write logs to file only"""
    try:
        with log_lock:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] [{level}] {message}\n"
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(log_entry)
    except:
        pass

def clear_logs():
    """Clear log file at start"""
    try:
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)
        write_log("=" * 80, "SYSTEM")
        write_log("Elite FB Creator - Enhanced OTP & Display", "SYSTEM")
        write_log("=" * 80, "SYSTEM")
    except:
        pass

# =============================================================================
# NAME DATABASES (Filipino & RPW Names)
# =============================================================================
FILIPINO_FIRST_NAMES_MALE = [
    'Juan', 'Jose', 'Miguel', 'Gabriel', 'Rafael', 'Antonio', 'Carlos', 'Luis',
    'Marco', 'Paolo', 'Angelo', 'Joshua', 'Christian', 'Mark', 'John', 'James',
    'Daniel', 'David', 'Michael', 'Jayson', 'Kenneth', 'Ryan', 'Kevin', 'Neil',
    'Jerome', 'Renzo', 'Carlo', 'Andres', 'Felipe', 'Diego', 'Mateo', 'Lucas'
]

FILIPINO_FIRST_NAMES_FEMALE = [
    'Maria', 'Ana', 'Sofia', 'Isabella', 'Gabriela', 'Valentina', 'Camila',
    'Angelica', 'Nicole', 'Michelle', 'Christine', 'Sarah', 'Jessica',
    'Andrea', 'Patricia', 'Jennifer', 'Karen', 'Ashley', 'Jasmine', 'Princess',
    'Angel', 'Joyce', 'Kristine', 'Diane', 'Joanna', 'Carmela', 'Isabel'
]

FILIPINO_LAST_NAMES = [
    'Reyes', 'Santos', 'Cruz', 'Bautista', 'Garcia', 'Flores', 'Gonzales',
    'Martinez', 'Ramos', 'Mendoza', 'Rivera', 'Torres', 'Fernandez', 'Lopez',
    'Castillo', 'Aquino', 'Villanueva', 'Santiago', 'Dela Cruz', 'Perez'
]

RPW_NAMES_MALE = [
    'Zephyr', 'Shadow', 'Phantom', 'Blaze', 'Storm', 'Frost', 'Raven', 'Ace',
    'Knight', 'Wolf', 'Dragon', 'Phoenix', 'Thunder', 'Void', 'Eclipse',
    'Nexus', 'Atlas', 'Orion', 'Dante', 'Xavier', 'Axel', 'Kai', 'Ryker'
]

RPW_NAMES_FEMALE = [
    'Luna', 'Aurora', 'Mystic', 'Crystal', 'Sapphire', 'Scarlet', 'Violet',
    'Rose', 'Athena', 'Venus', 'Nova', 'Stella', 'Serena', 'Raven', 'Jade',
    'Ruby', 'Pearl', 'Ivy', 'Willow', 'Hazel', 'Skye', 'Aria', 'Melody'
]

RPW_LAST_NAMES = [
    'Shadow', 'Dark', 'Light', 'Star', 'Moon', 'Sun', 'Sky', 'Night', 'Dawn',
    'Storm', 'Frost', 'Fire', 'Stanley', 'Nero', 'Clifford', 'Volsckev'
]

# =============================================================================
# PANCINGAN EMAIL DOMAINS
# =============================================================================
PANCINGAN_DOMAINS = [
    'hotmail.com', 'outlook.com', 'live.com', 'gmail.com',
    'mail.com', 'yahoo.com', 'protonmail.com', 'icloud.com'
]

# =============================================================================
# ENHANCED USER AGENT GENERATORS
# =============================================================================

def W_ueragent():
    """Enhanced User Agent for Desktop - HARDENED"""
    chrome_versions = [
        (120, 6099, 224), (121, 6167, 184), (122, 6261, 128),
        (123, 6312, 105), (124, 6367, 201), (125, 6422, 141)
    ]
    webkit_version = (537, 36)
    safari_version = random.choice([600, 620, 640])
    windows_versions = [(10, 0), (11, 0)]
    
    chrome = random.choice(chrome_versions)
    windows = random.choice(windows_versions)
    is_win64 = random.choice([True, False])
    win64_str = 'Win64; x64' if is_win64 else 'WOW64'
    
    user_agent = (
        f'Mozilla/5.0 (Windows NT {windows[0]}.{windows[1]}; {win64_str}) '
        f'AppleWebKit/{webkit_version[0]}.{webkit_version[1]} (KHTML, like Gecko) '
        f'Chrome/{chrome[0]}.{chrome[1]}.{chrome[2]} Safari/{safari_version}'
    )
    return user_agent

def get_random_device():
    """Enhanced device info for mobile - HARDENED"""
    devices = [
        {
            'model': 'Samsung-SM-S918B',
            'android': '14',
            'build': 'UP1A.231005.007',
            'brand': 'samsung',
            'device': 's918b',
            'fingerprint': 'samsung/s918bxx/s918b:14/UP1A.231005.007/S918BXXU2BWK4:user/release-keys'
        },
        {
            'model': 'Xiaomi-2210132G',
            'android': '13',
            'build': 'TKQ1.221114.001',
            'brand': 'xiaomi',
            'device': 'marble',
            'fingerprint': 'Xiaomi/marble_global/marble:13/TKQ1.221114.001/V14.0.8.0.TMRMIXM:user/release-keys'
        },
        {
            'model': 'OnePlus-CPH2451',
            'android': '14',
            'build': 'UKQ1.230924.001',
            'brand': 'oneplus',
            'device': 'OP594DL1',
            'fingerprint': 'OnePlus/CPH2451IND/OP594DL1:14/UKQ1.230924.001/U.R4T3.16e6e87-4ae-6b6:user/release-keys'
        },
        {
            'model': 'Google-Pixel-7-Pro',
            'android': '14',
            'build': 'UP1A.231105.001',
            'brand': 'google',
            'device': 'cheetah',
            'fingerprint': 'google/cheetah/cheetah:14/UP1A.231105.001/10817346:user/release-keys'
        },
        {
            'model': 'Samsung-SM-A546E',
            'android': '14',
            'build': 'UP1A.231005.007',
            'brand': 'samsung',
            'device': 'a54x',
            'fingerprint': 'samsung/a54xdx/a54x:14/UP1A.231005.007/A546EDXU3CXC1:user/release-keys'
        }
    ]
    
    device = random.choice(devices)
    device['width'] = random.choice([1080, 1440, 2400])
    device['height'] = random.choice([2340, 3088, 3200])
    device['dpi'] = random.choice([420, 480, 560, 640])
    
    return device

def generate_user_agent(device, fb_app_version="484.0.0.14.106"):
    """Enhanced User Agent for Mobile - HARDENED"""
    chrome_version = f"{random.randint(128, 135)}.0.{random.randint(6700, 6800)}.{random.randint(100, 200)}"
    webkit_version = "537.36"
    
    ua = f"Mozilla/5.0 (Linux; Android {device['android']}; {device['model']} Build/{device['build']}; wv) "
    ua += f"AppleWebKit/{webkit_version} (KHTML, like Gecko) Version/4.0 "
    ua += f"Chrome/{chrome_version} Mobile Safari/{webkit_version} "
    ua += f"[FBAN/EMA;FBLC/id_ID;FBAV/{fb_app_version};]"
    
    return ua

def generate_advanced_headers(device, locale='id_ID'):
    """Enhanced Headers for Mobile - HARDENED ANTI-CHECKPOINT"""
    ua = generate_user_agent(device)
    
    # Generate unique identifiers
    device_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    
    # Extract chrome version from UA for sec-ch-ua headers
    chrome_match = re.search(r'Chrome/(\d+)\.(\d+)\.(\d+)', ua)
    if chrome_match:
        chrome_major = chrome_match.group(1)
        chrome_version = f"{chrome_match.group(1)}.{chrome_match.group(2)}.{chrome_match.group(3)}"
    else:
        chrome_major = "131"
        chrome_version = "131.0.6778.135"
    
    headers = {
        'Host': 'm.facebook.com',
        'User-Agent': ua,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'DNT': '1',
        'X-Requested-With': 'com.facebook.lite',
        'X-FB-Connection-Type': random.choice(['WIFI', 'mobile.LTE', '4G', 'mobile.5G']),
        'X-FB-Connection-Quality': 'EXCELLENT',
        'X-FB-Device': device['model'],
        'X-FB-Device-Group': str(random.randint(5000, 9999)),
        'X-FB-Net-HNI': str(random.randint(40000, 52000)),
        'X-FB-SIM-HNI': str(random.randint(40000, 52000)),
        'X-FB-HTTP-Engine': 'Liger',
        'X-FB-Client-IP': 'True',
        'X-FB-Server-Cluster': 'True',
        'X-FB-Device-ID': device_id,
        'X-FB-Session-ID': session_id,
        'sec-ch-ua': f'"Chromium";v="{chrome_major}", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-ch-ua-platform-version': f'"{device["android"]}.0.0"',
        'sec-ch-ua-model': f'"{device["model"]}"',
        'sec-ch-ua-full-version-list': f'"Chromium";v="{chrome_version}", "Not_A Brand";v="24.0.0.0"',
    }
    
    return headers

def extractor(data):
    """Extract form data from HTML"""
    try:
        soup = BeautifulSoup(data, "html.parser")
        result = {}
        for inputs in soup.find_all("input"):
            name = inputs.get("name")
            value = inputs.get("value")
            if name:
                result[name] = value
        return result
    except Exception as e:
        return {"error": str(e)}

# =============================================================================
# DATABASE - ENHANCED
# =============================================================================

@contextmanager
def db_conn():
    conn = sqlite3.connect(DB_FILE, timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        write_log(f"DB error: {e}", "ERROR")
        raise
    finally:
        conn.close()

def init_db():
    with db_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS domains (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT UNIQUE NOT NULL,
                tld TEXT NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

def get_domains_by_tld(tld, page=1):
    try:
        with db_conn() as conn:
            cursor = conn.execute("SELECT COUNT(*) as total FROM domains WHERE tld = ?", (tld,))
            total = cursor.fetchone()['total']
            offset = (page - 1) * DOMAINS_PER_PAGE
            cursor = conn.execute("SELECT domain FROM domains WHERE tld = ? ORDER BY domain LIMIT ? OFFSET ?", 
                                (tld, DOMAINS_PER_PAGE, offset))
            domains = [row['domain'] for row in cursor.fetchall()]
            total_pages = (total + DOMAINS_PER_PAGE - 1) // DOMAINS_PER_PAGE
            return domains, total_pages, total
    except:
        return [], 0, 0

def get_tld_stats():
    try:
        with db_conn() as conn:
            cursor = conn.execute("SELECT tld, COUNT(*) as count FROM domains GROUP BY tld ORDER BY count DESC")
            return {row['tld']: row['count'] for row in cursor.fetchall()}
    except:
        return {}

# =============================================================================
# CONFIG & SHORTCUTS
# =============================================================================

def load_config():
    global config
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config.update(json.load(f))
    except:
        pass

def save_config():
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except:
        pass

def load_shortcuts():
    try:
        if os.path.exists(SHORTCUTS_FILE):
            with open(SHORTCUTS_FILE, 'r') as f:
                return json.load(f)
    except:
        return {}
    return {}

def save_shortcuts(shortcuts):
    try:
        with open(SHORTCUTS_FILE, 'w') as f:
            json.dump(shortcuts, f, indent=2)
    except:
        pass

# =============================================================================
# NAME GENERATORS
# =============================================================================

def get_filipino_name(gender):
    if gender == '1':
        first_name = random.choice(FILIPINO_FIRST_NAMES_MALE)
    else:
        first_name = random.choice(FILIPINO_FIRST_NAMES_FEMALE)
    last_name = random.choice(FILIPINO_LAST_NAMES)
    return first_name, last_name

def get_rpw_name(gender):
    if gender == '1':
        first_name = random.choice(RPW_NAMES_MALE)
    else:
        first_name = random.choice(RPW_NAMES_FEMALE)
    last_name = random.choice(RPW_LAST_NAMES)
    return first_name, last_name

def gen_password(first, last):
    name = f"{first}{last}".replace(' ', '')
    return f"{name}{random.randint(1000,9999)}"

def generate_pancingan_email():
    """Generate email pancingan (hotmail/gmail/etc)"""
    username_length = random.randint(10, 15)
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=username_length))
    domain = random.choice(PANCINGAN_DOMAINS)
    return f"{username}@{domain}"

# =============================================================================
# API CLIENT
# =============================================================================

class EmailAPI:
    def __init__(self):
        self.session = requests.Session()
    
    def get_all_domains(self, show_progress=True):
        all_domains = []
        page = 1
        
        if show_progress:
            print(f"\n{P4}⚡{R} {B}Fetching domains from server...{R}\n")
        
        while True:
            try:
                url = f"{API_BASE}/all-domains/"
                params = {"page": page, "limit": 100}
                
                r = self.session.get(url, params=params, timeout=15)
                r.raise_for_status()
                data = r.json()
                
                if isinstance(data, dict):
                    domains = data.get('domains', [])
                    total = data.get('total', 0)
                    has_next = data.get('has_next', False)
                else:
                    domains = data if isinstance(data, list) else []
                    total = len(domains)
                    has_next = False
                
                if not domains:
                    break
                
                all_domains.extend(domains)
                
                if show_progress:
                    progress = int((len(all_domains) / max(total, len(all_domains))) * 40)
                    bar = f"{P3}{'█' * progress}{P1}{'░' * (40 - progress)}{R}"
                    print(f"\r{CY}Page {page}{R} {bar} {B}{len(all_domains)}/{total}{R}", end='', flush=True)
                
                if not has_next and total > 0 and len(all_domains) >= total:
                    break
                
                if len(domains) < 100:
                    break
                
                page += 1
                time.sleep(0.3)
                
            except Exception as e:
                write_log(f"Domain fetch error on page {page}: {str(e)}", "ERROR")
                break
        
        if show_progress:
            print(f"\n\n{GN}✓{R} {B}Downloaded {len(all_domains)} domains{R}")
        
        write_log(f"Downloaded {len(all_domains)} domains from server", "SUCCESS")
        return all_domains
    
    def get_emails(self, domain, username, limit=20):
        try:
            r = self.session.get(f"{API_BASE}/email/{domain}/{username}/", params={"limit": limit}, timeout=10)
            r.raise_for_status()
            data = r.json()
            return data.get('emails', []) if isinstance(data, dict) else data
        except:
            return None
    
    def get_email_detail(self, domain, username, email_id):
        try:
            r = self.session.get(f"{API_BASE}/email/{domain}/{username}/{email_id}", timeout=10)
            r.raise_for_status()
            return r.json()
        except:
            return None

email_api = EmailAPI()

# =============================================================================
# OTP DETECTION
# =============================================================================

class OTPEngine:
    PATTERNS = [
        r'^(\d{4,8})$',
        r'(?:kode|otp|code)\s*(?:verifikasi)?\s*(?:adalah|is|:)?\s*(\d{4,8})',
        r'gunakan\s*(?:kode)?\s*(\d{4,8})',
        r'\b(\d{4,8})\b'
    ]
    
    @classmethod
    def extract(cls, subject, content):
        combined = f"{subject} {content}".strip()
        for pattern in cls.PATTERNS:
            match = re.search(pattern, combined, re.IGNORECASE)
            if match:
                code = match.group(1)
                if 4 <= len(code) <= 8 and code.isdigit():
                    return code
        return None

otp_engine = OTPEngine()

# =============================================================================
# DESKTOP ENGINE - ENHANCED ANTI-CHECKPOINT
# =============================================================================

class EnhancedDesktopEngine:
    """Desktop endpoint with enhanced headers - HARDENED"""
    
    def register(self, first, last, contact, password, gender):
        try:
            write_log(f"Desktop registration started for {first} {last}", "INFO")
            
            ses = requests.Session()
            
            # Enhanced headers for desktop - ANTI-CHECKPOINT
            enhanced_desktop_headers = {
                'Host': 'm.facebook.com',
                'User-Agent': W_ueragent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
                'DNT': '1',
                'sec-ch-ua': '"Chromium";v="120", "Not_A Brand";v="24", "Google Chrome";v="120"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Android"',
                'sec-ch-ua-platform-version': '"15.0.0"',
                'Pragma': 'no-cache',
            }
            
            ses.headers.update(enhanced_desktop_headers)
            
            response = ses.get(
                url='https://x.facebook.com/reg',
                params={
                    "_rdc": "1",
                    "_rdr": "",
                    "wtsid": "rdr_0t3qOXoIHbMS6isLw",
                    "refsrc": "deprecated"
                },
                timeout=30,
                allow_redirects=False
            )
            
            mts = ses.get("https://x.facebook.com", timeout=30).text
            m_ts_match = re.search(r'name="m_ts" value="(.*?)"', str(mts))
            m_ts = m_ts_match.group(1) if m_ts_match else ""
            
            formula = extractor(response.text)
            
            min_age = config.get('min_age', 18)
            max_age = config.get('max_age', 35)
            current_year = datetime.now().year
            birth_year = random.randint(current_year - max_age, current_year - min_age)
            
            fb_gender = "2" if gender == "male" else "1"
            
            birthday_day = str(random.randint(1, 28))
            birthday_month = str(random.randint(1, 12))
            
            payload = {
                'ccp': "2",
                'reg_instance': str(formula.get("reg_instance", "")),
                'submission_request': "true",
                'helper': "",
                'reg_impression_id': str(formula.get("reg_impression_id", "")),
                'ns': "1",
                'zero_header_af_client': "",
                'app_id': "103",
                'logger_id': str(formula.get("logger_id", "")),
                'field_names[0]': "firstname",
                'firstname': first,
                'lastname': last,
                'field_names[1]': "birthday_wrapper",
                'birthday_day': birthday_day,
                'birthday_month': birthday_month,
                'birthday_year': str(birth_year),
                'age_step_input': "",
                'did_use_age': "false",
                'field_names[2]': "reg_email__",
                'reg_email__': contact,
                'field_names[3]': "sex",
                'sex': fb_gender,
                'preferred_pronoun': "",
                'custom_gender': "",
                'field_names[4]': "reg_passwd__",
                'name_suggest_elig': "false",
                'was_shown_name_suggestions': "false",
                'did_use_suggested_name': "false",
                'use_custom_gender': "false",
                'guid': "",
                'pre_form_step': "",
                'encpass': f'#PWD_BROWSER:0:{int(time.time())}:{password}',
                'submit': "Daftar",
                'm_ts': m_ts,
                'fb_dtsg': str(formula.get("fb_dtsg", "")),
                'jazoest': str(formula.get("jazoest", "")),
                'lsd': str(formula.get("lsd", "")),
                '__dyn': str(formula.get("__dyn", "")),
                '__csr': str(formula.get("__csr", "")),
                '__req': str(formula.get("__req", "p")),
                '__fmt': str(formula.get("__fmt", "1")),
                '__a': str(formula.get("__a", "")),
                '__user': "0"
            }
            
            header1 = {
                "Authority": "m.facebook.com",
                "Host": "m.facebook.com",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": W_ueragent(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "dnt": "1",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-User": "?1",
                "Sec-Fetch-Dest": "document",
                "dpr": "1",
                "viewport-width": "1920",
                "sec-ch-ua": '"Chromium";v="120", "Not_A Brand";v="24", "Google Chrome";v="120"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "https://m.facebook.com",
                "Referer": "https://m.facebook.com/reg"
            }
            
            reg_url = "https://www.facebook.com/reg/submit/?privacy_mutation_token=eyJ0eXBlIjowLCJjcmVhdGlvbl90aW1lIjoxNzM0NDE0OTk2LCJjYWxsc2l0ZV9pZCI6OTA3OTI0NDAyOTQ4MDU4fQ%3D%3D&multi_step_form=1&skip_suma=0&shouldForceMTouch=0"
            
            submit = ses.post(reg_url, data=payload, headers=header1, timeout=30)
            
            if "c_user" in submit.cookies:
                cookies = ses.cookies.get_dict()
                uid = str(cookies["c_user"])
                write_log(f"Desktop registration successful - UID: {uid}", "SUCCESS")
                
                # Return additional info needed for verification
                return {
                    'success': True, 
                    'uid': uid, 
                    'session': ses,
                    'birthday_day': birthday_day,
                    'birthday_month': birthday_month,
                    'birthday_year': str(birth_year)
                }
            
            write_log("Desktop registration failed - No c_user cookie", "ERROR")
            return {'success': False, 'error': 'No c_user'}
        except Exception as e:
            write_log(f"Desktop registration exception: {str(e)}", "ERROR")
            return {'success': False, 'error': str(e)}

# =============================================================================
# MOBILE ENGINE - ENHANCED ANTI-CHECKPOINT WITH FIXED FBREDIRECT
# =============================================================================

class EnhancedMobileEngined:
    """Mobile endpoint with enhanced headers - HARDENED with fbredirect fix"""
    
    def __init__(self):
        pass
    
    def fix_fbredirect_url(self, action, base_url):
        """Fix fbredirect URLs by replacing them with base URL"""
        if not action:
            return base_url
        
        if action.startswith('fbredirect:'):
            # Extract path from fbredirect if possible
            match = re.search(r'fbredirect:(.+)', action)
            if match:
                path = match.group(1)
                if path.startswith('/'):
                    return f"https://m.facebook.com{path}"
                else:
                    return f"https://m.facebook.com/{path}"
            else:
                return base_url
        
        # Handle relative URLs
        if action.startswith('/'):
            return f"https://m.facebook.com{action}"
        
        # Handle full URLs
        if action.startswith('http'):
            return action
        
        # Default case
        return base_url
    
    def get_registration_form(self, session, url):
        """Fetch registration form with enhanced headers - FIXED for fbredirect"""
        device = get_random_device()
        fb_locale = 'id_ID'
        urls_to_try = [
            "https://m.facebook.com/reg",
            "https://mbasic.facebook.com/reg",
        ]
        
        for attempt in range(3):
            for form_url in urls_to_try:
                try:
                    write_log(f"Mobile form fetch attempt {attempt + 1}: {form_url}", "INFO")
                    
                    # Add headers to prevent fbredirect behavior
                    headers = generate_advanced_headers(device, fb_locale)
                    headers.update({
                        'X-FB-No-Redirect': '1',
                        'X-FB-Log-Web-Net': 'false',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'DNT': '1',
                        'Upgrade-Insecure-Requests': '1',
                    })
                    
                    response = session.get(form_url, headers=headers, timeout=30, allow_redirects=False)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, "html.parser")
                        
                        # Try to find form by multiple methods
                        form = None
                        
                        # Method 1: Direct form tag
                        forms = soup.find_all("form")
                        if forms:
                            form = forms[0]
                            write_log(f"Found form with action: {form.get('action', 'N/A')}", "INFO")
                        
                        # Method 2: Look for registration form by ID
                        if not form:
                            form = soup.find("form", {"id": lambda x: x and ('reg' in x.lower() or 'form' in x.lower())})
                        
                        # Method 3: Look for any form with registration inputs
                        if not form:
                            all_forms = soup.find_all("form")
                            for f in all_forms:
                                inputs = f.find_all("input")
                                if any(inp.get("name", "") in ["firstname", "lastname", "reg_email__"] for inp in inputs):
                                    form = f
                                    break
                        
                        if form:
                            # Fix fbredirect in form action
                            action = form.get("action", "")
                            if action and 'fbredirect:' in action:
                                write_log(f"Detected fbredirect in action: {action[:50]}...", "WARNING")
                                # Create a new form tag with fixed action
                                form['action'] = self.fix_fbredirect_url(action, form_url)
                                write_log(f"Fixed action to: {form['action']}", "INFO")
                            
                            write_log("Mobile form fetched successfully", "SUCCESS")
                            return True, form, response.cookies.get_dict(), response.text
                        else:
                            write_log("No form found in page", "WARNING")
                
                except requests.exceptions.RequestException as e:
                    error_msg = str(e)
                    if 'fbredirect' in error_msg:
                        write_log(f"Mobile form fetch failed (fbredirect): {error_msg[:50]}", "WARNING")
                        # Try alternative approach
                        try:
                            # Force no redirects
                            response = session.get(form_url, headers=headers, timeout=30, allow_redirects=False)
                            if response.status_code == 200:
                                # Parse manually without BeautifulSoup
                                if 'fbredirect:' in response.text:
                                    # Extract form manually
                                    form_match = re.search(r'<form[^>]*action="([^"]*)"[^>]*>(.*?)</form>', response.text, re.DOTALL | re.IGNORECASE)
                                    if form_match:
                                        action = form_match.group(1)
                                        form_html = form_match.group(0)
                                        # Create a minimal form
                                        soup = BeautifulSoup(form_html, "html.parser")
                                        form = soup.find("form")
                                        if form:
                                            form['action'] = self.fix_fbredirect_url(action, form_url)
                                            write_log("Form extracted manually from fbredirect page", "INFO")
                                            return True, form, response.cookies.get_dict(), response.text
                        except:
                            pass
                    else:
                        write_log(f"Mobile form fetch failed: {error_msg[:50]}", "WARNING")
                    continue
                except Exception as e:
                    write_log(f"Mobile form fetch error: {str(e)[:50]}", "WARNING")
                    continue
            
            if attempt < 2:
                time.sleep(random.uniform(1, 2))
        
        write_log("Failed to fetch registration form after all attempts", "ERROR")
        return False, None, {}, ""
    
    def extract_form_data(self, form_html, first_name, last_name, contact, password, gender):
        """Extract and prepare form data from HTML"""
        try:
            soup = BeautifulSoup(form_html, "html.parser") if isinstance(form_html, str) else form_html
            
            min_age = config.get('min_age', 18)
            max_age = config.get('max_age', 35)
            current_year = datetime.now().year
            birth_year = random.randint(current_year - max_age, current_year - min_age)
            
            birthday_day = str(random.randint(1, 28))
            birthday_month = str(random.randint(1, 12))
            
            user_details = {
                'firstname': first_name,
                'lastname': last_name,
                'date': birthday_day,
                'month': birthday_month,
                'year': str(birth_year),
                'contact': contact,
                'password': password,
                'gender': '2' if gender == 'male' else '1'
            }
            
            data = {
                "firstname": user_details['firstname'],
                "lastname": user_details['lastname'],
                "birthday_day": user_details['date'],
                "birthday_month": user_details['month'],
                "birthday_year": user_details['year'],
                "reg_email__": user_details['contact'],
                "sex": user_details['gender'],
                "encpass": f'#PWD_BROWSER:0:{int(time.time())}:{user_details["password"]}',
                "submit": "Sign Up"
            }
            
            # Extract all hidden fields
            if soup:
                for inp in soup.find_all("input"):
                    name = inp.get("name")
                    if name and name not in data:
                        value = inp.get("value", "")
                        data[name] = value
            
            return data, user_details
            
        except Exception as e:
            write_log(f"Form data extraction error: {str(e)}", "ERROR")
            return {}, {}
    
    def register(self, first, last, contact, password, fb_gender):
        """Main registration function with enhanced headers and fbredirect fix"""
        try:
            write_log(f"Mobile registration started for {first} {last}", "INFO")
            
            gender = 'male' if fb_gender == 2 else 'female'
            device = get_random_device()
            fb_locale = 'id_ID'
            session = requests.Session()
            
            endpoints = [
                "https://m.facebook.com/reg",
                "https://mbasic.facebook.com/reg",
            ]
            
            # Enhanced headers to prevent fbredirect
            base_headers = generate_advanced_headers(device, fb_locale)
            base_headers.update({
                'X-FB-No-Redirect': '1',
                'X-FB-Log-Web-Net': 'false',
                'X-FB-Sensible-Logging': 'false',
                'X-FB-Connection-Quality': 'EXCELLENT',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Cache-Control': 'max-age=0',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
            })
            
            session.headers.update(base_headers)
            
            for endpoint_attempt in range(2):
                for endpoint in endpoints:
                    try:
                        write_log(f"Mobile registration attempt {endpoint_attempt + 1} at {endpoint}", "INFO")
                        
                        success, form, initial_cookies, page_html = self.get_registration_form(session, endpoint)
                        
                        if not success:
                            write_log(f"Failed to get form from {endpoint}", "WARNING")
                            continue
                        
                        # Extract form data
                        data, user_details = self.extract_form_data(form, first, last, contact, password, gender)
                        
                        if not data:
                            write_log("Failed to extract form data", "ERROR")
                            continue
                        
                        # Get action URL
                        action_url = endpoint
                        if form and form.get("action"):
                            action = form.get("action", "")
                            action_url = self.fix_fbredirect_url(action, endpoint)
                        
                        write_log(f"Submitting mobile registration to {action_url}", "INFO")
                        
                        # Prepare POST headers
                        post_headers = base_headers.copy()
                        post_headers.update({
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'Origin': 'https://m.facebook.com',
                            'Referer': endpoint,
                            'Content-Length': str(len('&'.join([f'{k}={v}' for k, v in data.items()]))),
                        })
                        
                        # Submit registration
                        response = session.post(
                            action_url,
                            data=data,
                            headers=post_headers,
                            timeout=60,
                            allow_redirects=True
                        )
                        
                        cookies = session.cookies.get_dict()
                        
                        # Check for successful registration
                        if "c_user" in cookies:
                            uid = str(cookies["c_user"])
                            write_log(f"Mobile registration successful - UID: {uid}", "SUCCESS")
                            
                            return {
                                'success': True, 
                                'uid': uid, 
                                'session': session,
                                'cookies': cookies,
                                'details': user_details
                            }
                        
                        # Check if checkpoint/verification is required
                        response_text_lower = response.text.lower()
                        response_url_lower = response.url.lower()
                        
                        if any(k in response_url_lower or k in response_text_lower 
                               for k in ['checkpoint', 'confirm', 'verification', 'kode', 'code']):
                            write_log("Mobile registration requires verification", "INFO")
                            
                            # Try to extract UID from response
                            uid_match = re.search(r'"userID":"(\d+)"', response.text)
                            if uid_match:
                                uid = uid_match.group(1)
                            else:
                                # Check cookies again
                                temp_cookies = session.cookies.get_dict()
                                if 'c_user' in temp_cookies:
                                    uid = str(temp_cookies['c_user'])
                                else:
                                    uid = "UNKNOWN"
                            
                            write_log(f"Mobile registration pending verification - UID: {uid}", "SUCCESS")
                            return {
                                'success': True, 
                                'uid': uid, 
                                'session': session,
                                'cookies': session.cookies.get_dict(),
                                'details': user_details,
                                'requires_verification': True
                            }
                        
                        # Try to extract error message
                        error_match = re.search(r'class="[^"]*error[^"]*"[^>]*>([^<]+)', response.text, re.IGNORECASE)
                        if error_match:
                            error_msg = error_match.group(1).strip()[:100]
                            write_log(f"Registration error: {error_msg}", "ERROR")
                        else:
                            write_log("Registration failed without clear error", "ERROR")
                        
                    except requests.exceptions.Timeout:
                        write_log(f"Mobile registration timeout at {endpoint}", "WARNING")
                        continue
                    except Exception as e:
                        write_log(f"Mobile registration exception at {endpoint}: {str(e)[:50]}", "WARNING")
                        continue
                
                if endpoint_attempt < 1:
                    time.sleep(random.uniform(3, 5))
            
            write_log("Mobile registration failed after all attempts", "ERROR")
            return {'success': False, 'error': 'Registration failed after all attempts'}
            
        except Exception as e:
            write_log(f"Mobile registration fatal error: {str(e)}", "ERROR")
            return {'success': False, 'error': str(e)}

# =============================================================================
# EMAIL CHANGER - USES SAME SESSION (MOBILE STYLE)
# =============================================================================

class EmailChanger:
    """Change email using same session - EXACT method from nando.py"""
    
    @staticmethod
    def change_email_to_tinyhost(session, new_email, fb_locale='id_ID'):
        """Change email PERSIS seperti nando.py - direct endpoint approach"""
        try:
            write_log(f"Starting email change to: {new_email}", "INFO")
            
            # Get device for headers (mobile style like nando.py)
            device = get_random_device()
            headers = generate_advanced_headers(device, fb_locale)
            
            # Update session headers
            session.headers.update(headers)
            
            # Delay sebelum change email
            time.sleep(random.uniform(1.5, 2.5))
            
            # Method 1: Try direct approach like nando.py - visit home first
            try:
                session.get("https://m.facebook.com/", timeout=30)
                time.sleep(1)
            except:
                pass
            
            # Access change email page - try multiple URLs
            urls_to_try = [
                f"https://m.facebook.com/changeemail/?locale={fb_locale}",
                "https://m.facebook.com/changeemail/",
                f"https://m.facebook.com/settings/email/?locale={fb_locale}",
                "https://m.facebook.com/settings/email/"
            ]
            
            response = None
            working_url = None
            
            for url in urls_to_try:
                try:
                    response = session.get(url, headers=headers, timeout=30)
                    if response.status_code == 200 and len(response.text) > 500:
                        working_url = url
                        write_log(f"Accessed change email page: {url}", "INFO")
                        break
                except:
                    continue
            
            if not response or not working_url:
                write_log("Failed to access any change email page", "ERROR")
                return False
            
            # Parse HTML untuk extract tokens
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract tokens yang diperlukan (seperti nando.py)
            fb_dtsg = ""
            jazoest = ""
            lsd = ""
            
            # Method 1: From input fields
            for inp in soup.find_all("input"):
                name = inp.get("name", "")
                value = inp.get("value", "")
                if name == "fb_dtsg":
                    fb_dtsg = value
                elif name == "jazoest":
                    jazoest = value
                elif name == "lsd":
                    lsd = value
            
            # Method 2: From script/JSON if not found in inputs
            if not fb_dtsg:
                dtsg_match = re.search(r'"DTSGInitialData".*?"token":"([^"]+)"', response.text)
                if dtsg_match:
                    fb_dtsg = dtsg_match.group(1)
            
            if not jazoest and fb_dtsg:
                # Generate jazoest from fb_dtsg
                jazoest_val = sum(ord(c) for c in fb_dtsg)
                jazoest = f"2{jazoest_val}"
            
            # Find form action URL
            action_url = working_url
            form = soup.find("form")
            if form:
                action = form.get("action", "")
                if action:
                    if action.startswith('/'):
                        action_url = f"https://m.facebook.com{action}"
                    elif action.startswith('http'):
                        action_url = action
                    else:
                        action_url = f"https://m.facebook.com/{action}"
            
            # Build payload seperti nando.py
            data = {
                "new": new_email,
                "submit": "Add"
            }
            
            # Add tokens if available
            if fb_dtsg:
                data["fb_dtsg"] = fb_dtsg
            if jazoest:
                data["jazoest"] = jazoest
            if lsd:
                data["lsd"] = lsd
            
            # Add all hidden fields from form
            if form:
                for inp in form.find_all("input"):
                    name = inp.get("name")
                    if name and name not in data:
                        value = inp.get("value", "")
                        data[name] = value
            
            # Headers for POST
            post_headers = headers.copy()
            post_headers.update({
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://m.facebook.com',
                'Referer': working_url
            })
            
            # Submit email change
            write_log(f"Submitting to: {action_url}", "INFO")
            response = session.post(action_url, data=data, headers=post_headers, timeout=30, allow_redirects=True)
            
            # Verification
            if response.status_code == 200:
                time.sleep(1)
                
                # Check response text
                response_lower = response.text.lower()
                
                # Success indicators
                if any(indicator in response_lower for indicator in [
                    new_email.lower(),
                    'success', 'berhasil', 'added', 'ditambahkan',
                    'email added', 'email ditambahkan'
                ]):
                    write_log(f"Email changed successfully to: {new_email}", "SUCCESS")
                    return True
                
                # Double check by visiting settings again
                try:
                    check_url = working_url
                    check_response = session.get(check_url, headers=headers, timeout=30)
                    if new_email.lower() in check_response.text.lower():
                        write_log(f"Email changed successfully to: {new_email}", "SUCCESS")
                        return True
                except:
                    pass
            
            write_log("Email change verification failed", "WARNING")
            return False
            
        except Exception as e:
            write_log(f"Email change exception: {str(e)}", "ERROR")
            return False

# =============================================================================
# OTP VERIFICATION ENGINE (From tes.py - FIXED)
# =============================================================================

class ViaBrowserSimulator:
    def get_via_user_agent(self):
        ua_list = [
            "Mozilla/5.0 (Linux; Android 13; SM-A546E Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/131.0.6778.135 Mobile Safari/537.36 [FBAN/EMA;FBLC/id_ID;FBAV/484.0.0.14.106;]",
            "Mozilla/5.0 (Linux; Android 12; SM-G991B Build/SP1A.210812.016; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/130.0.6723.86 Mobile Safari/537.36 [FBAN/EMA;FBLC/id_ID;FBAV/483.0.0.15.109;]",
            "Mozilla/5.0 (Linux; Android 13; SM-A525F Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/131.0.6778.104 Mobile Safari/537.36 [FBAN/EMA;FBLC/id_ID;FBAV/484.0.0.14.106;]"
        ]
        return random.choice(ua_list)

    def create_via_session(self):
        session = requests.Session()
        session.headers.update({
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, br',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://m.facebook.com',
            'referer': 'https://m.facebook.com/',
            'sec-ch-ua': '"Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': self.get_via_user_agent(),
            'x-requested-with': 'mark.via.gp',
        })
        return session

    def build_thick_cookies(self, session, uid):
        cookies_dict = {}
        seen_keys = set()
        
        for cookie in session.cookies:
            if cookie.name not in seen_keys:
                cookies_dict[cookie.name] = cookie.value
                seen_keys.add(cookie.name)
        
        if 'c_user' not in cookies_dict:
            write_log(f"No c_user for UID {uid}", "WARNING")
            return None
            
        cookies_dict.update({
            'm_pixel_ratio': cookies_dict.get('m_pixel_ratio', '2'),
            'wd': cookies_dict.get('wd', '360x806'),
            'ps_l': cookies_dict.get('ps_l', '1'),
            'ps_n': cookies_dict.get('ps_n', '1'),
            'locale': cookies_dict.get('locale', 'id_ID'),
            'pas': cookies_dict.get('pas', f'{uid}%3AdrxQXO9bo9'),
            'wl_cbv': cookies_dict.get('wl_cbv', f'v2%3Bclient_version%3A3000%3Btimestamp%3A{int(time.time())}'),
            'vpd': cookies_dict.get('vpd', 'v1%3B662x360x2')
        })
        return cookies_dict

    def format_cookie_string(self, cookies_dict):
        priority = ['datr', 'sb', 'm_pixel_ratio', 'wd', 'ps_l', 'ps_n', 'c_user', 'xs', 'fr', 'locale', 'pas', 'presence', 'spin']
        ending = ['wl_cbv', 'vpd']
        parts = []
        
        for key in priority:
            if key in cookies_dict:
                parts.append(f"{key}={cookies_dict[key]}")
        for key, value in cookies_dict.items():
            if key not in priority and key not in ending:
                parts.append(f"{key}={value}")
        for key in ending:
            if key in cookies_dict:
                parts.append(f"{key}={cookies_dict[key]}")
        return "; ".join(parts)

    def login_and_extract(self, identifier, password, prefix=""):
        """Login method that returns session for OTP verification - 3 PARAMETERS ONLY"""
        try:
            write_log(f"{prefix} - Initializing session", "INFO")
            session = self.create_via_session()
            
            write_log(f"{prefix} - Requesting login page", "INFO")
            resp = session.get('https://m.facebook.com/login/', timeout=30)
            
            lsd = re.search(r'name="lsd" value="(.*?)"', resp.text)
            jazoest = re.search(r'name="jazoest" value="(.*?)"', resp.text)
            privacy = re.search(r'privacy_mutation_token=([^&"]+)', resp.text)
            
            data = {
                'lsd': lsd.group(1) if lsd else "",
                'jazoest': jazoest.group(1) if jazoest else "",
                'email': identifier,
                'pass': password,
                'login_source': 'comet_headerless_login',
                'encpass': f'#PWD_BROWSER:0:{int(time.time())}:{password}'
            }
            
            url = f'https://m.facebook.com/login/device-based/regular/login/?privacy_mutation_token={privacy.group(1)}&refsrc=deprecated' if privacy else 'https://m.facebook.com/login/device-based/regular/login/?refsrc=deprecated'
            
            write_log(f"{prefix} - Authenticating credentials", "INFO")
            session.post(url, data=data, timeout=30, allow_redirects=True)
            
            cookies = {}
            for c in session.cookies:
                if c.name not in cookies:
                    cookies[c.name] = c.value
            
            if 'c_user' not in cookies:
                write_log(f"{prefix} - Authentication failed", "ERROR")
                return {'status': 'failed', 'message': 'No c_user', 'session': session, 'cookies': None}
            
            uid = cookies['c_user']
            write_log(f"{prefix} - Authenticated → UID: {uid}", "SUCCESS")
            
            return {
                'status': 'success',
                'uid': uid,
                'session': session,
                'cookies': cookies
            }
        except Exception as e:
            write_log(f"{prefix} - Login exception: {str(e)[:30]}", "ERROR")
            return {'status': 'failed', 'message': str(e), 'session': None, 'cookies': None}


class HardcoreEndpointOTPSubmitter:
    def __init__(self, session, prefix=""):
        self.session = session
        self.prefix = prefix
        self.session.headers.update({
            'User-Agent': W_ueragent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
        })

    def detect_otp_page(self):
        write_log(f"{self.prefix} - Scanning for OTP page", "INFO")
        urls = [
            "https://www.facebook.com/checkpoint/",
            "https://www.facebook.com/confirmemail.php",
            "https://www.facebook.com/"
        ]
        
        for url in urls:
            try:
                r = self.session.get(url, timeout=10, allow_redirects=True)
                if r.status_code == 200:
                    if any(k in r.url.lower() or k in r.text.lower() for k in ['confirmemail', 'checkpoint', 'verification', 'kode', 'code']):
                        write_log(f"{self.prefix} - OTP page detected", "SUCCESS")
                        form = self.extract_form(r.text)
                        if form and 'error' not in form:
                            form['__action_url'] = self.get_action(r.text, r.url)
                            form['__code_input_name'] = self.get_code_field(r.text)
                            return True, form, r.url
            except Exception as e:
                write_log(f"{self.prefix} - Error checking URL {url}: {str(e)}", "WARNING")
                continue
        
        write_log(f"{self.prefix} - No OTP page found", "WARNING")
        return False, {}, ""

    def extract_form(self, html):
        try:
            soup = BeautifulSoup(html, "html.parser")
            form_data = {}
            for inp in soup.find_all("input"):
                name = inp.get("name")
                value = inp.get("value", "")
                if name:
                    form_data[name] = value
            return form_data
        except:
            return {"error": "parse_failed"}

    def get_action(self, html, url):
        try:
            soup = BeautifulSoup(html, 'html.parser')
            form = soup.find('form')
            if form:
                action = form.get('action', '')
                if action and not action.startswith('http'):
                    return f"https://www.facebook.com{action}" if action.startswith('/') else f"{url.rsplit('/', 1)[0]}/{action}"
                return action or url
        except:
            pass
        return url

    def get_code_field(self, html):
        try:
            soup = BeautifulSoup(html, 'html.parser')
            code_inp = soup.find('input', {'name': lambda x: x and 'code' in x.lower()})
            return code_inp.get('name', 'code') if code_inp else 'code'
        except:
            return 'code'

    def submit_otp_via_endpoint(self, otp_code):
        write_log(f"{self.prefix} - Submitting OTP: {otp_code}", "INFO")
        
        has_page, form, otp_url = self.detect_otp_page()
        if not has_page or not form:
            write_log(f"{self.prefix} - OTP page unavailable", "ERROR")
            return False, "NO_OTP_PAGE"
        
        payload = {k: v for k, v in form.items() if not k.startswith('__') and v is not None}
        code_field = form.get('__code_input_name', 'code')
        payload[code_field] = otp_code
        submit_url = form.get('__action_url', otp_url)
        
        self.session.headers.update({
            'Referer': otp_url,
            'Origin': 'https://www.facebook.com',
            'Content-Type': 'application/x-www-form-urlencoded'
        })
        
        try:
            r = self.session.post(submit_url, data=payload, timeout=15, allow_redirects=True)
            
            if r.status_code != 200:
                write_log(f"{self.prefix} - HTTP {r.status_code} response", "WARNING")
            
            success_ind = ['home.php', 'welcome', 'feed', 'confirmed', 'success', 'verified', 'beranda', 'selamat']
            error_ind = ['error', 'invalid', 'wrong', 'incorrect', 'salah', 'gagal']
            
            # Check cookies first
            cookies_after = self.session.cookies.get_dict()
            if 'c_user' in cookies_after:
                write_log(f"{self.prefix} - OTP SUCCESS! UID: {cookies_after['c_user']}", "SUCCESS")
                return True, "SUCCESS"
            
            # Check response indicators
            response_lower = r.text.lower()
            
            for indicator in success_ind:
                if indicator in response_lower:
                    write_log(f"{self.prefix} - Success indicator: {indicator}", "SUCCESS")
                    return True, "SUCCESS"
            
            for indicator in error_ind:
                if indicator in response_lower:
                    write_log(f"{self.prefix} - Error indicator: {indicator}", "ERROR")
                    return False, "OTP_INVALID"
            
            # If redirected away from checkpoint, assume success
            if "checkpoint" not in r.url.lower() and "confirm" not in r.url.lower():
                write_log(f"{self.prefix} - Redirected away from checkpoint (success)", "SUCCESS")
                return True, "SUCCESS"
            
            write_log(f"{self.prefix} - OTP status unclear", "WARNING")
            return True, "UNKNOWN"
            
        except Exception as e:
            write_log(f"{self.prefix} - Submit error: {str(e)[:20]}", "ERROR")
            return False, str(e)


class OTPVerifier:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.prefix = email[:20] if email else "Unknown"
        self.via_browser = ViaBrowserSimulator()
        self.session = None
    
    def login_and_extract(self):
        """Login via browser simulation"""
        try:
            write_log(f"Browser login started for {self.email}", "INFO")
            
            result = self.via_browser.login_and_extract(self.email, self.password, self.prefix)
            
            if result['status'] == 'success':
                self.session = result['session']
                write_log(f"Browser login successful - UID: {result['uid']}", "SUCCESS")
                return {'success': True, 'uid': result['uid'], 'session': self.session}
            else:
                write_log(f"Browser login failed: {result.get('message', 'Unknown')}", "ERROR")
                return {'success': False, 'error': result.get('message', 'Login failed')}
                
        except Exception as e:
            write_log(f"Browser login exception: {str(e)}", "ERROR")
            return {'success': False, 'error': str(e)}
    
    def verify_with_otp(self, otp_code, max_retries=3):
        """Complete OTP verification flow using same session"""
        write_log(f"Starting OTP verification for {self.email} with code {otp_code}", "INFO")
        
        for attempt in range(max_retries):
            try:
                write_log(f"Verification attempt {attempt + 1}/{max_retries}", "INFO")
                
                login_result = self.login_and_extract()
                
                if not login_result['success']:
                    if attempt < max_retries - 1:
                        write_log("Browser login failed, retrying...", "WARNING")
                        time.sleep(3)
                        continue
                    else:
                        write_log("Browser login failed after all retries", "ERROR")
                        return False, "LOGIN_FAILED"
                
                otp_submitter = HardcoreEndpointOTPSubmitter(self.session, self.prefix)
                success, msg = otp_submitter.submit_otp_via_endpoint(otp_code)
                
                if success:
                    write_log("OTP verification completed successfully", "SUCCESS")
                    return True, "SUCCESS"
                else:
                    if attempt < max_retries - 1:
                        write_log(f"Verification failed: {msg}, retrying...", "WARNING")
                        time.sleep(3)
                        continue
                    else:
                        write_log(f"OTP verification failed after all retries: {msg}", "ERROR")
                        return False, msg
                        
            except Exception as e:
                write_log(f"Verification attempt {attempt + 1} error: {str(e)}", "ERROR")
                if attempt < max_retries - 1:
                    time.sleep(3)
                    continue
                else:
                    return False, str(e)
        
        return False, "MAX_RETRIES_EXCEEDED"
    
    def get_session(self):
        return self.session


class CookieExtractor:
    def __init__(self, session):
        self.session = session
        self.via_browser = ViaBrowserSimulator()
    
    def extract(self, uid):
        try:
            write_log(f"Cookie extraction started for UID: {uid}", "INFO")
            
            self.session.get(f'https://m.facebook.com/{uid}', timeout=30)
            
            thick = self.via_browser.build_thick_cookies(self.session, uid)
            if not thick:
                write_log("Cookie extraction failed - Unable to build thick cookies", "ERROR")
                return None
            
            cookie_str = self.via_browser.format_cookie_string(thick)
            write_log(f"Cookie extraction successful - Length: {len(cookie_str)}", "SUCCESS")
            return cookie_str
        except Exception as e:
            write_log(f"Cookie extraction exception: {str(e)}", "ERROR")
            return None

# =============================================================================
# ENHANCED PROCESS DISPLAY FUNCTIONS
# =============================================================================

def display_process_header(account_number, total_accounts):
    """Display process header with account number"""
    print(f"{P3}╔{'═' * (W-2)}╗{R}")
    print(f"{P3}║{R} {B}{CY}PROSES AKUN KE-{account_number:03d} DARI {total_accounts:03d}{R}{' ' * (W-35)} {P3}║{R}")
    print(f"{P3}╚{'═' * (W-2)}╝{R}")

def display_account_creation(first, last, pancingan_email, tinyhost_email, password, gender):
    """Display account creation process"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    print(f"\n{GR}[{timestamp}] {BL}↻{R} {B}Membuat Akun Baru{R}")
    print(f"   {P4}├─{R} {CY}Nama:{R} {WH}{first} {last}{R}")
    print(f"   {P4}├─{R} {CY}Gender:{R} {WH}{gender}{R}")
    print(f"   {P4}├─{R} {CY}Email Pancingan:{R} {WH}{pancingan_email}{R}")
    print(f"   {P4}├─{R} {CY}Email Tinyhost:{R} {WH}{tinyhost_email}{R}")
    print(f"   {P4}└─{R} {CY}Password:{R} {WH}{password}{R}")

def display_email_change_status(old_email, new_email, success=True):
    """Display email change status"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    icon = f"{GN}✓" if success else f"{RD}✗"
    status = f"{GN}Berhasil" if success else f"{RD}Gagal"
    
    print(f"{GR}[{timestamp}] {icon}{R} {B}Mengubah Email{R}")
    print(f"   {P4}├─{R} {CY}Dari:{R} {WH}{old_email}{R}")
    print(f"   {P4}├─{R} {CY}Ke:{R} {WH}{new_email}{R}")
    print(f"   {P4}└─{R} {CY}Status:{R} {status}{R}")

def display_otp_monitoring(username, domain, attempt, max_attempts, found=False, otp=None):
    """Display OTP monitoring status"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    if found:
        print(f"{GR}[{timestamp}] {GN}✓{R} {B}OTP Ditemukan!{R}")
        print(f"   {P4}├─{R} {CY}Email:{R} {WH}{username}@{domain}{R}")
        print(f"   {P4}├─{R} {CY}Kode OTP:{R} {B}{GN}{otp}{R}")
        print(f"   {P4}└─{R} {CY}Percobaan:{R} {WH}{attempt}/{max_attempts}{R}")
    else:
        print(f"{GR}[{timestamp}] {YL}↻{R} {B}Mencari OTP{R}")
        print(f"   {P4}├─{R} {CY}Email:{R} {WH}{username}@{domain}{R}")
        print(f"   {P4}├─{R} {CY}Percobaan:{R} {WH}{attempt}/{max_attempts}{R}")
        print(f"   {P4}└─{R} {CY}Status:{R} {YL}Memeriksa...{R}")

def display_otp_submission(otp, success=True, message=""):
    """Display OTP submission status"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    icon = f"{GN}✓" if success else f"{RD}✗"
    status = f"{GN}Berhasil" if success else f"{RD}Gagal"
    
    print(f"{GR}[{timestamp}] {icon}{R} {B}Submit OTP{R}")
    print(f"   {P4}├─{R} {CY}Kode:{R} {B}{WH}{otp}{R}")
    print(f"   {P4}├─{R} {CY}Status:{R} {status}{R}")
    if message:
        print(f"   {P4}└─{R} {CY}Pesan:{R} {WH}{message}{R}")

def display_cookie_extraction(uid, success=True, cookie_length=0):
    """Display cookie extraction status"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    icon = f"{GN}✓" if success else f"{RD}✗"
    status = f"{GN}Berhasil" if success else f"{RD}Gagal"
    
    print(f"{GR}[{timestamp}] {icon}{R} {B}Ekstraksi Cookies{R}")
    print(f"   {P4}├─{R} {CY}UID:{R} {WH}{uid}{R}")
    print(f"   {P4}├─{R} {CY}Status:{R} {status}{R}")
    if success:
        print(f"   {P4}└─{R} {CY}Panjang Cookies:{R} {WH}{cookie_length} karakter{R}")

def display_account_save(uid, email, filename):
    """Display account save status"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    print(f"{GR}[{timestamp}] {GN}✓{R} {B}Akun Disimpan{R}")
    print(f"   {P4}├─{R} {CY}UID:{R} {WH}{uid}{R}")
    print(f"   {P4}├─{R} {CY}Email:{R} {WH}{email}{R}")
    print(f"   {P4}└─{R} {CY}File:{R} {WH}{filename}{R}")

def display_failure_reason(reason, details=""):
    """Display failure reason"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    print(f"{GR}[{timestamp}] {RD}✗{R} {B}Akun Gagal{R}")
    print(f"   {P4}├─{R} {CY}Alasan:{R} {RD}{reason}{R}")
    if details:
        print(f"   {P4}└─{R} {CY}Detail:{R} {WH}{details[:50]}{R}")

# =============================================================================
# ULTRA LIVE MONITOR DISPLAY
# =============================================================================

def display_live_monitor_ultra(start_time, account_limit):
    """Ultra enhanced live monitor display"""
    try:
        # Get elapsed time
        current_time = time.time()
        elapsed = int(current_time - start_time)
        mins = elapsed // 60
        secs = elapsed % 60
        
        # Get stats with lock
        with lock:
            total_created = stats['total_created']
            ok_count = stats['ok_count']
            cp_count = stats['cp_count']
            rejected_count = stats['rejected_count']
            worker1_status = stats['worker1_status']
            worker2_status = stats['worker2_status']
            worker3_status = stats['worker3_status']
            current_account = stats['current_account']
            last_success = stats['last_success']
            total_with_cookies = stats['total_with_cookies']
            current_process = stats['current_process']
            current_email = stats['current_email']
            current_pancingan = stats['current_pancingan']
        
        # Clear screen
        clear()
        
        # Display header
        print_header("ELITE FB CREATOR - LIVE MONITOR", width=W)
        print()
        
        # Progress section
        box("PROGRESS", [
            f"{PK}Target:{R} {B}{WH}{account_limit}{R} akun",
            f"{PK}Proses:{R} {B}{WH}{total_created}{R}/{account_limit}",
            f"{PK}Waktu:{R} {B}{WH}{mins:02d}:{secs:02d}{R}"
        ], width=W, color=P3)
        
        # Statistics section
        print()
        print(f"{P3}╔{'═' * (W-2)}╗{R}")
        print(f"{P3}║{R} {B}{CY}STATISTIK AKUN{R}{' ' * (W-18)} {P3}║{R}")
        print(f"{P3}╠{'═' * (W-2)}╣{R}")
        
        # Create progress bar
        if account_limit > 0:
            progress = int((total_created / account_limit) * 30)
            bar = f"{P3}{'█' * progress}{P1}{'░' * (30 - progress)}{R}"
            print(f"{P3}║{R} {bar} {B}{total_created}/{account_limit}{R}{' ' * (W-44)} {P3}║{R}")
        
        # Account status
        print(f"{P3}║{R} {BG4}{B}{WH} HIDUP {R} {B}{GN}{ok_count:3d}{R}    ", end='')
        print(f"{BG3}{B}{WH} MATI  {R} {B}{RD}{cp_count:3d}{R}    ", end='')
        print(f"{BG6}{B}{WH} REJECT {R} {B}{YL}{rejected_count:2d}{R}{' ' * (W-50)} {P3}║{R}")
        
        # Additional stats
        print(f"{P3}║{R} {CY}With Cookies:{R} {B}{WH}{total_with_cookies}{R}{' ' * (W-30)} {P3}║{R}")
        
        # Success rate
        if total_created > 0:
            success_rate = (ok_count / total_created) * 100
            print(f"{P3}║{R} {CY}Success Rate:{R} {B}{WH}{success_rate:.1f}%{R}{' ' * (W-30)} {P3}║{R}")
        
        print(f"{P3}╚{'═' * (W-2)}╝{R}")
        
        # Worker status section
        print()
        print(f"{P3}╔{'═' * (W-2)}╗{R}")
        print(f"{P3}║{R} {B}{CY}STATUS WORKER{R}{' ' * (W-19)} {P3}║{R}")
        print(f"{P3}╠{'═' * (W-2)}╣{R}")
        
        # Worker 1 (Creation)
        w1_color = GN if "success" in worker1_status.lower() else RD if "error" in worker1_status.lower() else CY
        print(f"{P3}║{R} {P4}W1{R} {B}(Creation):{R} {w1_color}{worker1_status[:40]:<40}{R} {P3}║{R}")
        
        # Worker 2 (Monitor)
        w2_color = GN if "otp found" in worker2_status.lower() else CY if "checking" in worker2_status.lower() else RD if "error" in worker2_status.lower() else CY
        print(f"{P3}║{R} {P4}W2{R} {B}(Monitor):{R}  {w2_color}{worker2_status[:40]:<40}{R} {P3}║{R}")
        
        # Worker 3 (Verify)
        w3_color = GN if "success" in worker3_status.lower() else RD if "failed" in worker3_status.lower() else CY
        print(f"{P3}║{R} {P4}W3{R} {B}(Verify):{R}   {w3_color}{worker3_status[:40]:<40}{R} {P3}║{R}")
        
        print(f"{P3}╚{'═' * (W-2)}╝{R}")
        
        # Current process section
        if current_process and current_process != "Waiting...":
            print()
            print(f"{P3}╔{'═' * (W-2)}╗{R}")
            print(f"{P3}║{R} {B}{CY}PROSES SAAT INI{R}{' ' * (W-21)} {P3}║{R}")
            print(f"{P3}╠{'═' * (W-2)}╣{R}")
            
            print(f"{P3}║{R} {CY}Aktivitas:{R} {B}{WH}{current_process[:45]}{R}{' ' * (W-60)} {P3}║{R}")
            
            if current_account and current_account != "None":
                print(f"{P3}║{R} {CY}Akun:{R} {B}{WH}{current_account[:45]}{R}{' ' * (W-60)} {P3}║{R}")
            
            if current_pancingan and current_pancingan != "None":
                print(f"{P3}║{R} {CY}Pancingan:{R} {B}{WH}{current_pancingan[:45]}{R}{' ' * (W-60)} {P3}║{R}")
            
            if current_email and current_email != "None":
                print(f"{P3}║{R} {CY}Tinyhost:{R} {B}{WH}{current_email[:45]}{R}{' ' * (W-60)} {P3}║{R}")
            
            print(f"{P3}╚{'═' * (W-2)}╝{R}")
        
        # Last success
        if last_success and last_success != "None":
            print()
            print(f"{P3}╔{'═' * (W-2)}╗{R}")
            print(f"{P3}║{R} {B}{GN}TERAKHIR BERHASIL{R}{' ' * (W-25)} {P3}║{R}")
            print(f"{P3}╠{'═' * (W-2)}╣{R}")
            print(f"{P3}║{R} {WH}{last_success[:52]}{R}{' ' * (W-56)} {P3}║{R}")
            print(f"{P3}╚{'═' * (W-2)}╝{R}")
        
        # Footer
        print()
        print(f"{GR}{'─' * W}{R}")
        print(f"{GR}Output: {OUTPUT_FILE}{R}")
        print(f"{GR}Logs: {LOG_FILE}{R}")
        print(f"{GR}Press Ctrl+C to stop{R}")
        print(f"{GR}{'─' * W}{R}")
        
        sys.stdout.flush()
        
    except Exception as e:
        # Fallback minimal display
        print(f"\n{RD}Error in monitor:{R} {str(e)[:50]}")
        print(f"Created: {stats.get('total_created', 0)}")
        print(f"Time: {int(time.time() - start_time)}s")

# =============================================================================
# ACCOUNT SAVER & DISPLAY
# =============================================================================

def save_account(account_info):
    """Save account dengan format lengkap"""
    try:
        line = f"{account_info['uid']}|{account_info['password']}|{account_info['email']}|{account_info['cookies']}\n"
        with open(OUTPUT_FILE, 'a') as f:
            f.write(line)
        write_log(f"Account saved: {account_info['uid']} | {account_info['email']}", "SUCCESS")
        
        # Display save status
        display_account_save(account_info['uid'], account_info['email'], OUTPUT_FILE)
        
    except Exception as e:
        write_log(f"Save error: {str(e)}", "ERROR")
        print_status(f"Gagal menyimpan akun: {str(e)}", "error")

def display_account_success(account_info):
    """Display success account with ultra design"""
    print(f"\n{GN}{'═' * W}{R}")
    print(f"{BG4}{B}{WH}  ✓ ACCOUNT SUCCESS - COOKIES AWET  {R}".center(W + 35))
    print(f"{GN}{'═' * W}{R}\n")
    
    # Account info in box
    box("INFORMASI AKUN", [
        f"{PK}UID:{R} {B}{WH}{account_info['uid']}{R}",
        f"{PK}Nama:{R} {B}{WH}{account_info.get('full_name', 'N/A')}{R}",
        f"{PK}Email:{R} {B}{WH}{account_info['email']}{R}",
        f"{PK}Password:{R} {B}{WH}{account_info['password']}{R}",
        f"{PK}Gender:{R} {B}{WH}{account_info.get('gender', 'N/A')}{R}",
        f"{PK}Dibuat:{R} {B}{WH}{account_info.get('creation_time', 'N/A')}{R}"
    ], width=W, color=P3)
    
    # Cookies info
    print()
    cookies = account_info['cookies']
    cookie_count = len(cookies.split(';'))
    
    print(f"{P3}╔{'═' * (W-2)}╗{R}")
    print(f"{P3}║{R} {B}{CY}COOKIES ({cookie_count} items){R}{' ' * (W-25)} {P3}║{R}")
    print(f"{P3}╠{'═' * (W-2)}╣{R}")
    
    # Display first few cookies
    cookie_parts = cookies.split(';')[:5]
    for i, part in enumerate(cookie_parts):
        part = part.strip()
        if len(part) > W-6:
            part = part[:W-9] + "..."
        print(f"{P3}║{R} {D}{part}{R}{' ' * (W-len(part)-4)} {P3}║{R}")
    
    if len(cookie_parts) < len(cookies.split(';')):
        print(f"{P3}║{R} {GR}... and {len(cookies.split(';')) - len(cookie_parts)} more{R}{' ' * (W-30)} {P3}║{R}")
    
    print(f"{P3}╚{'═' * (W-2)}╝{R}")
    print(f"{GN}{'═' * W}{R}\n")

# =============================================================================
# TRIPLE WORKER SYSTEM - ENHANCED WITH UI
# =============================================================================

class CreationWorker(threading.Thread):
    def __init__(self, worker_id):
        super().__init__(daemon=True)
        self.worker_id = worker_id
        self.running = True
        self.account_counter = 0
    
    def run(self):
        write_log(f"Creation Worker {self.worker_id} started", "SYSTEM")
        
        while self.running:
            try:
                task = creation_queue.get(timeout=1)
                
                if task == "STOP":
                    write_log(f"Creation Worker {self.worker_id} received STOP signal", "SYSTEM")
                    break
                
                domain = task
                
                # Update stats
                with lock:
                    stats['worker1_status'] = "Getting task..."
                    stats['current_process'] = "Mempersiapkan akun baru"
                
                # Check limit
                with lock:
                    current_total = stats['total_created']
                    account_limit = config.get('account_limit', 10)
                
                if current_total >= account_limit:
                    write_log(f"Account limit reached ({account_limit})", "INFO")
                    creation_queue.task_done()
                    break
                
                # Generate account data
                gender_cfg = config.get('gender', 'random')
                gender = random.choice(['male', 'female']) if gender_cfg == 'random' else gender_cfg
                
                name_type = config.get('name_type', 'filipino')
                if name_type == 'filipino':
                    first, last = get_filipino_name('1' if gender == 'male' else '2')
                else:
                    first, last = get_rpw_name('1' if gender == 'male' else '2')
                
                full_name = f"{first} {last}"
                
                if config.get('password_type') == 'auto' or not config.get('custom_password'):
                    password = gen_password(first, last)
                else:
                    password = config.get('custom_password')
                
                # Generate PANCINGAN email
                pancingan_email = generate_pancingan_email()
                
                # Update stats
                with lock:
                    stats['worker1_status'] = f"Creating: {first} {last[:1]}."
                    stats['current_account'] = f"{first} {last}"
                    stats['current_pancingan'] = pancingan_email
                    stats['current_process'] = "Membuat akun dengan email pancingan"
                
                # Display account creation
                display_account_creation(first, last, pancingan_email, f"waiting@{domain}", password, gender)
                
                write_log(f"Worker1: Creating {full_name} | Pancingan: {pancingan_email}", "INFO")
                
                # Register with PANCINGAN email
                if config.get('endpoint') == 'desktop':
                    result = EnhancedDesktopEngine().register(first, last, pancingan_email, password, gender)
                else:
                    fb_gender = 2 if gender == 'male' else 1
                    # Use enhanced mobile engine
                    enhanced_mobile_engine = EnhancedMobileEngined()  # Use the fixed version
                    result = enhanced_mobile_engine.register(first, last, pancingan_email, password, fb_gender)
                
                if result.get('success'):
                    uid = result.get('uid', 'UNKNOWN')
                    
                    # Update stats
                    with lock:
                        stats['worker1_status'] = f"Created: {uid}"
                        stats['current_account'] = f"{first} {last} ({uid})"
                    
                    write_log(f"Worker1: Registration success - UID: {uid}", "SUCCESS")
                    
                    # CHANGE EMAIL TO TINYHOST
                    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
                    tinyhost_email = f"{username}@{domain}"
                    
                    # Update stats
                    with lock:
                        stats['worker1_status'] = f"Changing email..."
                        stats['current_email'] = tinyhost_email
                        stats['current_process'] = "Mengubah email ke Tinyhost"
                    
                    # Display email change
                    display_email_change_status(pancingan_email, tinyhost_email, False)  # Show as in progress
                    
                    write_log(f"Worker1: Changing email to: {tinyhost_email}", "INFO")
                    
                    # Get session from result
                    session = result.get('session')
                    if session:
                        email_changed = EmailChanger.change_email_to_tinyhost(session, tinyhost_email)
                        
                        # Display result
                        display_email_change_status(pancingan_email, tinyhost_email, email_changed)
                        
                        if email_changed:
                            write_log(f"Worker1: Email changed successfully", "SUCCESS")
                            
                            # Get birthday info
                            birthday_info = result.get('details', {}) if 'details' in result else {}
                            
                            account_data = {
                                'uid': uid,
                                'first': first,
                                'last': last,
                                'full_name': full_name,
                                'email': tinyhost_email,
                                'pancingan_email': pancingan_email,
                                'password': password,
                                'gender': gender,
                                'domain': domain,
                                'username': username,
                                'session': session,
                                'cookies': session.cookies.get_dict() if hasattr(session, 'cookies') else {},
                                'birthday_day': birthday_info.get('date', result.get('birthday_day', str(random.randint(1, 28)))),
                                'birthday_month': birthday_info.get('month', result.get('birthday_month', str(random.randint(1, 12)))),
                                'birthday_year': birthday_info.get('year', result.get('birthday_year', str(random.randint(1985, 2000)))),
                                'user_agent': W_ueragent() if config.get('endpoint') == 'desktop' else generate_user_agent(get_random_device()),
                                'requires_verification': result.get('requires_verification', False)
                            }
                            
                            # Send to monitor queue
                            monitor_queue.put(account_data)
                            
                            # Update stats
                            with lock:
                                stats['worker1_status'] = f"Queued: {username}"
                                stats['current_process'] = "Menunggu OTP"
                            
                        else:
                            write_log(f"Worker1: Failed to change email for UID {uid}", "ERROR")
                            with lock:
                                stats['total_failed'] += 1
                                stats['rejected_count'] += 1
                                stats['current_process'] = "Gagal mengubah email"
                            
                            display_failure_reason("Gagal mengubah email", "Email change failed")
                    else:
                        write_log(f"Worker1: No session available for UID {uid}", "ERROR")
                        with lock:
                            stats['total_failed'] += 1
                            stats['rejected_count'] += 1
                            stats['current_process'] = "Tidak ada session"
                        
                        display_failure_reason("Tidak ada session", "No session available")
                else:
                    error_msg = result.get('error', 'Unknown error')
                    write_log(f"Worker1: Registration failed - {error_msg}", "ERROR")
                    with lock:
                        stats['total_failed'] += 1
                        stats['rejected_count'] += 1
                        stats['current_process'] = "Registrasi gagal"
                    
                    display_failure_reason("Registrasi gagal", error_msg[:50])
                
                # Delay between accounts
                time.sleep(random.uniform(2, 4))
                
                # Update stats
                with lock:
                    stats['worker1_status'] = "Idle"
                    stats['current_process'] = "Menunggu tugas berikutnya"
                
                creation_queue.task_done()
                
                self.account_counter += 1
                
            except Empty:
                with lock:
                    stats['worker1_status'] = "Waiting for task..."
                    stats['current_process'] = "Menunggu tugas"
                time.sleep(2)
                continue
            except Exception as e:
                write_log(f"Creation Worker {self.worker_id} error: {str(e)}", "ERROR")
                with lock:
                    stats['worker1_status'] = f"Error: {str(e)[:20]}"
                    stats['rejected_count'] += 1
                    stats['current_process'] = "Error dalam proses"
                time.sleep(3)
                continue
        
        write_log(f"Creation Worker {self.worker_id} stopped. Created: {self.account_counter} accounts", "SYSTEM")

class MonitorWorker(threading.Thread):
    def __init__(self, worker_id):
        super().__init__(daemon=True)
        self.worker_id = worker_id
        self.running = True
        self.monitored_count = 0
    
    def run(self):
        write_log(f"Monitor Worker {self.worker_id} started", "SYSTEM")
        
        while self.running:
            try:
                account = monitor_queue.get(timeout=1)
                
                if account == "STOP":
                    write_log(f"Monitor Worker {self.worker_id} received STOP signal", "SYSTEM")
                    break
                
                domain = account['domain']
                username = account['username']
                uid = account['uid']
                full_name = account['full_name']
                tinyhost_email = account['email']
                
                # Update stats
                with lock:
                    stats['worker2_status'] = f"Monitoring: {username}@{domain}"
                    stats['current_account'] = f"{full_name}"
                    stats['current_email'] = tinyhost_email
                    stats['current_process'] = "Memantau email untuk OTP"
                
                # Display monitoring start
                display_otp_monitoring(username, domain, 1, 10, False)
                
                write_log(f"Worker2: Monitoring OTP for {username}@{domain} (UID: {uid})", "INFO")
                
                timeout = config.get('otp_timeout', 15)
                interval = config.get('otp_check_interval', 1)
                checks = int(timeout / interval)
                otp = None
                
                for i in range(checks):
                    # Update stats
                    with lock:
                        stats['worker2_status'] = f"Checking {i+1}/{checks}"
                        stats['current_process'] = f"Memeriksa email ({i+1}/{checks})"
                    
                    # Display checking status
                    display_otp_monitoring(username, domain, i+1, checks, False)
                    
                    time.sleep(interval)
                    
                    try:
                        # Update stats
                        with lock:
                            stats['worker2_status'] = f"Fetching emails..."
                        
                        emails = email_api.get_emails(domain, username, limit=5)
                        
                        if emails:
                            # Update stats
                            with lock:
                                stats['worker2_status'] = f"Processing {len(emails)} emails"
                            
                            for email_msg in emails[:3]:
                                email_id = email_msg.get('id')
                                if not email_id:
                                    continue
                                
                                detail = email_api.get_email_detail(domain, username, email_id)
                                if not detail:
                                    continue
                                
                                subject = detail.get('subject', '')
                                content = detail.get('body', '') or detail.get('text', '')
                                
                                otp = otp_engine.extract(subject, content)
                                if otp:
                                    # Update stats
                                    with lock:
                                        stats['worker2_status'] = f"OTP Found!"
                                        stats['current_process'] = "OTP ditemukan!"
                                    
                                    # Display OTP found
                                    display_otp_monitoring(username, domain, i+1, checks, True, otp)
                                    
                                    write_log(f"Worker2: OTP found: {otp} for {username}@{domain}", "SUCCESS")
                                    break
                            
                            if otp:
                                break
                        else:
                            # Update stats
                            with lock:
                                stats['worker2_status'] = f"No emails ({i+1}/{checks})"
                    
                    except Exception as e:
                        write_log(f"Worker2: Email check error: {str(e)[:50]}", "WARNING")
                        with lock:
                            stats['worker2_status'] = f"Error: {str(e)[:15]}"
                        continue
                
                if otp:
                    account['otp'] = otp
                    
                    # Update stats
                    with lock:
                        stats['worker2_status'] = f"Sending to verify..."
                        stats['current_process'] = "Mengirim untuk verifikasi OTP"
                    
                    verify_queue.put(account)
                    
                    # Update stats
                    with lock:
                        stats['worker2_status'] = f"Queued for verify"
                    
                    write_log(f"Worker2: Account {uid} queued for verification", "INFO")
                else:
                    write_log(f"Worker2: OTP timeout for {username}@{domain} (UID: {uid})", "WARNING")
                    with lock:
                        stats['total_failed'] += 1
                        stats['cp_count'] += 1
                        stats['total_created'] += 1
                        stats['current_process'] = "OTP timeout"
                    
                    display_failure_reason("OTP tidak ditemukan", "Timeout setelah " + str(timeout) + " detik")
                
                # Update stats
                with lock:
                    stats['worker2_status'] = "Idle"
                    stats['current_process'] = "Menunggu akun berikutnya"
                    self.monitored_count += 1
                
                monitor_queue.task_done()
                
                # Small delay
                time.sleep(0.5)
                
            except Empty:
                with lock:
                    stats['worker2_status'] = "Waiting for account..."
                    stats['current_process'] = "Menunggu akun"
                time.sleep(2)
                continue
            except Exception as e:
                write_log(f"Monitor Worker {self.worker_id} error: {str(e)}", "ERROR")
                with lock:
                    stats['worker2_status'] = f"Error: {str(e)[:20]}"
                    stats['cp_count'] += 1
                    stats['current_process'] = "Error monitoring"
                time.sleep(3)
                continue
        
        write_log(f"Monitor Worker {self.worker_id} stopped. Monitored: {self.monitored_count} accounts", "SYSTEM")

class VerifyWorker(threading.Thread):
    def __init__(self, worker_id):
        super().__init__(daemon=True)
        self.worker_id = worker_id
        self.running = True
        self.verified_count = 0
        self.success_count = 0
    
    def run(self):
        write_log(f"Verify Worker {self.worker_id} started", "SYSTEM")
        
        while self.running:
            try:
                account = verify_queue.get(timeout=1)
                
                if account == "STOP":
                    write_log(f"Verify Worker {self.worker_id} received STOP signal", "SYSTEM")
                    break
                
                email = account['email']
                password = account['password']
                otp = account['otp']
                uid = account.get('uid', 'Unknown')
                full_name = account.get('full_name', 'Unknown')
                
                # Update stats
                with lock:
                    stats['worker3_status'] = f"Verifying: {email[:15]}..."
                    stats['current_account'] = f"{full_name}"
                    stats['current_email'] = email
                    stats['current_process'] = "Verifikasi OTP"
                
                # Display OTP submission
                display_otp_submission(otp, False, "Memulai verifikasi...")
                
                write_log(f"Worker3: Starting verification for {email} with OTP: {otp}", "INFO")
                
                # OTP Verification
                verifier = OTPVerifier(email, password)
                success, msg = verifier.verify_with_otp(otp, max_retries=2)
                
                # Display result
                display_otp_submission(otp, success, msg)
                
                if success:
                    # Update stats
                    with lock:
                        stats['worker3_status'] = "Verification successful!"
                        stats['total_verified'] += 1
                        stats['current_process'] = "OTP berhasil, mengambil cookies"
                    
                    write_log(f"Worker3: Verification successful for {email}", "SUCCESS")
                    
                    time.sleep(random.uniform(1, 2))
                    
                    # Get session and extract cookies
                    verified_session = verifier.get_session()
                    
                    if verified_session:
                        # Update stats
                        with lock:
                            stats['worker3_status'] = "Extracting cookies..."
                        
                        extractor = CookieExtractor(verified_session)
                        cookies = extractor.extract(uid)
                        
                        # Display cookie extraction
                        display_cookie_extraction(uid, cookies is not None, len(cookies) if cookies else 0)
                        
                        if cookies:
                            creation_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                            
                            account_info = {
                                'uid': uid,
                                'email': email,
                                'password': password,
                                'full_name': full_name,
                                'gender': account.get('gender', 'N/A'),
                                'birthday_day': account.get('birthday_day', 'N/A'),
                                'birthday_month': account.get('birthday_month', 'N/A'),
                                'birthday_year': account.get('birthday_year', 'N/A'),
                                'cookies': cookies,
                                'user_agent': W_ueragent() if config.get('endpoint') == 'desktop' else generate_user_agent(get_random_device()),
                                'creation_time': creation_time,
                                'verified_via': 'desktop_with_cookies'
                            }
                            
                            # Save account
                            save_account(account_info)
                            
                            # Update stats
                            with lock:
                                stats['total_with_cookies'] += 1
                                stats['ok_count'] += 1
                                stats['last_success'] = f"{full_name} ({uid})"
                                self.success_count += 1
                                stats['current_process'] = "Akun berhasil disimpan"
                            
                            # Display account
                            with lock:
                                display_account_success(account_info)
                            
                            write_log(f"Worker3: Account {uid} COMPLETE with cookies!", "SUCCESS")
                        else:
                            write_log(f"Worker3: Cookie extraction failed for UID {uid}", "ERROR")
                            with lock:
                                stats['worker3_status'] = "Cookie extract failed"
                                stats['cp_count'] += 1
                                stats['current_process'] = "Gagal mengambil cookies"
                    else:
                        write_log(f"Worker3: No session available for cookie extraction", "ERROR")
                        with lock:
                            stats['worker3_status'] = "No session"
                            stats['cp_count'] += 1
                            stats['current_process'] = "Tidak ada session"
                else:
                    write_log(f"Worker3: Verification failed for {email}: {msg}", "ERROR")
                    with lock:
                        stats['worker3_status'] = f"Failed: {msg[:15]}"
                        stats['total_failed'] += 1
                        stats['cp_count'] += 1
                        stats['current_process'] = "Verifikasi OTP gagal"
                
                # Update total created
                with lock:
                    stats['total_created'] += 1
                    self.verified_count += 1
                    stats['current_process'] = "Menunggu verifikasi berikutnya"
                
                # Update stats
                with lock:
                    stats['worker3_status'] = "Idle"
                
                verify_queue.task_done()
                
                # Delay between verifications
                time.sleep(random.uniform(1, 3))
                
            except Empty:
                with lock:
                    stats['worker3_status'] = "Waiting for verification..."
                    stats['current_process'] = "Menunggu verifikasi"
                time.sleep(2)
                continue
            except Exception as e:
                write_log(f"Verify Worker {self.worker_id} error: {str(e)}", "ERROR")
                with lock:
                    stats['worker3_status'] = f"Error: {str(e)[:20]}"
                    stats['cp_count'] += 1
                    stats['current_process'] = "Error verifikasi"
                time.sleep(3)
                continue
        
        write_log(f"Verify Worker {self.worker_id} stopped. Verified: {self.verified_count}, Success: {self.success_count}", "SYSTEM")

# =============================================================================
# MENU SYSTEM - ENHANCED
# =============================================================================

def menu_main():
    """Main menu with enhanced UI"""
    while True:
        banner()
        
        box("MENU UTAMA", [
            f"{PK}1.{R} Buat Akun {GR}(Pancingan+Tinyhost+OTP){R}",
            f"{PK}2.{R} Konfigurasi {GR}(Pengaturan){R}",
            f"{PK}3.{R} Domain Manager {GR}(Database){R}",
            f"{PK}4.{R} Statistik {GR}(Laporan){R}",
            f"{PK}5.{R} Keluar"
        ], color=P3)
        
        choice = get_input("Pilih opsi")
        
        if choice == "1":
            menu_create()
        elif choice == "2":
            menu_config()
        elif choice == "3":
            menu_domains()
        elif choice == "4":
            menu_stats()
        elif choice == "5":
            clear()
            print(f"\n{P3}{'═' * W}{R}")
            print(f"{B}{CY}Terima kasih telah menggunakan Elite Creator!{R}".center(W + 18))
            print(f"{P3}{'═' * W}{R}\n")
            write_log("Program exited by user", "SYSTEM")
            time.sleep(1)
            break

def menu_create():
    """Create account menu"""
    banner()
    box("SUMBER DOMAIN", [
        f"{P4}1.{R} Pilih berdasarkan TLD",
        f"{P4}2.{R} Gunakan Shortcut",
        f"{P4}0.{R} Kembali"
    ])
    
    choice = get_input("Pilih opsi")
    
    if choice == "1":
        menu_tld_selection()
    elif choice == "2":
        menu_use_shortcut()
    elif choice == "0":
        return

def menu_tld_selection():
    """TLD selection menu"""
    banner()
    box("KATEGORI TLD")
    
    stats_tld = get_tld_stats()
    if not stats_tld:
        print(f"\n{RD}Tidak ada domain tersedia. Sync domain dulu!{R}")
        time.sleep(2)
        return
    
    tlds = list(stats_tld.keys())[:50]
    
    # Display in columns
    cols = 3
    rows = (len(tlds) + cols - 1) // cols
    
    for i in range(rows):
        line = ""
        for j in range(cols):
            idx = i + j * rows
            if idx < len(tlds):
                tld = tlds[idx]
                count = stats_tld[tld]
                line += f"{P4}{idx+1:2d}.{R} .{tld.upper():<8} {GR}({count}){R}    "
        print(line)
    
    print(f"\n{P4} 0.{R} Kembali")
    
    choice = get_input("Pilih TLD")
    if choice == "0":
        return
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(tlds):
            tld = tlds[idx]
            menu_select_domains(tld)
    except:
        print(f"\n{RD}Pilihan tidak valid!{R}")
        time.sleep(1)

def menu_select_domains(tld):
    """Select domains from TLD"""
    page = 1
    selected = []
    
    while True:
        banner()
        domains, total_pages, total = get_domains_by_tld(tld, page)
        
        box(f"PILIH DOMAIN - .{tld.upper()}", [
            f"{CY}Halaman:{R} {page}/{total_pages}",
            f"{CY}Terpilih:{R} {len(selected)} domain",
            f"{CY}Total:{R} {total} tersedia"
        ])
        
        # Display domains in a grid
        print()
        cols = 3
        for i in range(0, len(domains), cols):
            line = ""
            for j in range(cols):
                if i + j < len(domains):
                    domain = domains[i + j]
                    idx = i + j + 1
                    marker = f"{GN}✓{R}" if domain in selected else f"{GR}○{R}"
                    line += f"{marker} {P4}{idx:3d}.{R} {domain:<25}"
            print(line)
        
        print(f"\n{P3}{'═' * W}{R}")
        print(f"{P4}N.{R} Next  {P4}P.{R} Previous  {P4}A.{R} Pilih Semua  {P4}S.{R} Mulai  {P4}0.{R} Kembali")
        
        choice = get_input("Aksi").lower()
        
        if choice == "0":
            return
        elif choice == "n" and page < total_pages:
            page += 1
        elif choice == "p" and page > 1:
            page -= 1
        elif choice == "a":
            selected.extend([d for d in domains if d not in selected])
            print(f"\n{GN}✓{R} {len(domains)} domain dipilih")
            time.sleep(1)
        elif choice == "s":
            if selected:
                start_creation(selected)
                return
            else:
                print(f"\n{RD}Pilih domain terlebih dahulu!{R}")
                time.sleep(1)
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(domains):
                    domain = domains[idx]
                    if domain in selected:
                        selected.remove(domain)
                        print(f"\n{RD}✗{R} Domain dihapus: {domain}")
                    else:
                        selected.append(domain)
                        print(f"\n{GN}✓{R} Domain ditambahkan: {domain}")
                    time.sleep(0.5)
            except:
                pass

def menu_use_shortcut():
    """Use shortcut menu"""
    banner()
    box("SHORTCUT")
    
    shortcuts = load_shortcuts()
    
    if not shortcuts:
        print(f"\n{YL}Tidak ada shortcut tersedia{R}")
        time.sleep(2)
        return
    
    for i, (name, domains) in enumerate(shortcuts.items(), 1):
        print(f"{P4}{i:2d}.{R} {name:<30} {GR}({len(domains)} domain){R}")
    
    print(f"\n{P4} 0.{R} Kembali")
    
    choice = get_input("Pilih shortcut")
    
    if choice != "0":
        try:
            idx = int(choice) - 1
            shortcut_list = list(shortcuts.items())
            if 0 <= idx < len(shortcut_list):
                name, domains = shortcut_list[idx]
                start_creation(domains)
        except:
            print(f"\n{RD}Pilihan tidak valid!{R}")
            time.sleep(1)

def menu_config():
    """Configuration menu"""
    while True:
        banner()
        
        # Display current configuration
        endpoint_display = f"{B}{GN if config['endpoint'] == 'desktop' else CY}{config['endpoint'].title()}{R}"
        gender_display = f"{B}{WH}{config['gender'].title()}{R}"
        name_type_display = f"{B}{WH}{config['name_type'].title()}{R}"
        
        if config.get('password_type') == 'auto':
            password_display = f"{GN}Auto{R} (Nama+Random)"
        else:
            pwd = config.get('custom_password', '')
            password_display = f"{CY}Custom{R} ({'*' * len(pwd) if pwd else 'Not Set'})"
        
        box("KONFIGURASI", [
            f"{PK}1.{R} Endpoint: {endpoint_display}",
            f"{PK}2.{R} Tipe Nama: {name_type_display}",
            f"{PK}3.{R} Gender: {gender_display}",
            f"{PK}4.{R} Password: {password_display}",
            f"{PK}5.{R} Limit Akun: {B}{WH}{config.get('account_limit', 10)}{R}",
            f"{PK}6.{R} Timeout OTP: {B}{WH}{config.get('otp_timeout', 15)} detik{R}",
            f"{PK}7.{R} Simpan & Kembali"
        ])
        
        choice = get_input("Pilih opsi")
        
        if choice == "1":
            print(f"\n{P4}1.{R} Desktop  {P4}2.{R} Mobile")
            ep = get_input("Endpoint")
            if ep == "1":
                config['endpoint'] = "desktop"
                print(f"\n{GN}✓{R} Endpoint diatur ke: Desktop")
                time.sleep(1)
            elif ep == "2":
                config['endpoint'] = "mobile"
                print(f"\n{GN}✓{R} Endpoint diatur ke: Mobile")
                time.sleep(1)
        
        elif choice == "2":
            print(f"\n{P4}1.{R} Filipino  {P4}2.{R} RPW")
            nt = get_input("Tipe Nama")
            if nt == "1":
                config['name_type'] = "filipino"
                print(f"\n{GN}✓{R} Tipe nama diatur ke: Filipino")
                time.sleep(1)
            elif nt == "2":
                config['name_type'] = "rpw"
                print(f"\n{GN}✓{R} Tipe nama diatur ke: RPW")
                time.sleep(1)
        
        elif choice == "3":
            print(f"\n{P4}1.{R} Pria  {P4}2.{R} Wanita  {P4}3.{R} Random")
            gen = get_input("Gender")
            if gen == "1":
                config['gender'] = "male"
                print(f"\n{GN}✓{R} Gender diatur ke: Pria")
                time.sleep(1)
            elif gen == "2":
                config['gender'] = "female"
                print(f"\n{GN}✓{R} Gender diatur ke: Wanita")
                time.sleep(1)
            elif gen == "3":
                config['gender'] = "random"
                print(f"\n{GN}✓{R} Gender diatur ke: Random")
                time.sleep(1)
        
        elif choice == "4":
            print(f"\n{P3}╔{'═' * (W-2)}╗{R}")
            print(f"{P3}║{R} {B}{CY}PENGATURAN PASSWORD{R}{' ' * (W-25)} {P3}║{R}")
            print(f"{P3}╠{'═' * (W-2)}╣{R}")
            print(f"{P3}║{R} {P4}1.{R} Auto (Nama + 4 digit acak){' ' * (W-35)} {P3}║{R}")
            print(f"{P3}║{R} {P4}2.{R} Custom (Sama untuk semua akun){' ' * (W-38)} {P3}║{R}")
            print(f"{P3}║{R} {P4}0.{R} Batal{' ' * (W-11)} {P3}║{R}")
            print(f"{P3}╚{'═' * (W-2)}╝{R}")
            
            pt = get_input("Pilih tipe password")
            
            if pt == "1":
                config['password_type'] = "auto"
                config['custom_password'] = ""
                print(f"\n{GN}✓{R} Password diatur ke: Auto")
                time.sleep(1)
            
            elif pt == "2":
                config['password_type'] = "custom"
                
                print(f"\n{CY}Masukkan password custom:{R}")
                print(f"{GR}(Minimal 6 karakter){R}")
                print(f"{GR}(Akan digunakan untuk SEMUA akun){R}\n")
                
                pwd = get_input("Password")
                
                if len(pwd) >= 6:
                    print(f"\n{CY}Konfirmasi password:{R}")
                    pwd_confirm = get_input("Password")
                    
                    if pwd == pwd_confirm:
                        config['custom_password'] = pwd
                        print(f"\n{GN}✓{R} Password custom disimpan!")
                        print(f"{CY}Password:{R} {'*' * len(pwd)} ({len(pwd)} karakter)")
                        time.sleep(2)
                    else:
                        print(f"\n{RD}✗{R} Password tidak cocok!")
                        time.sleep(1)
                else:
                    print(f"\n{RD}✗{R} Password minimal 6 karakter!")
                    time.sleep(1)
        
        elif choice == "5":
            limit = get_input("Limit akun")
            try:
                config['account_limit'] = max(1, int(limit))
                print(f"\n{GN}✓{R} Limit akun diatur ke: {config['account_limit']}")
                time.sleep(1)
            except:
                print(f"\n{RD}✗{R} Input tidak valid!")
                time.sleep(1)
        
        elif choice == "6":
            timeout = get_input("Timeout OTP (detik)")
            try:
                config['otp_timeout'] = max(5, min(60, int(timeout)))
                print(f"\n{GN}✓{R} Timeout OTP diatur ke: {config['otp_timeout']} detik")
                time.sleep(1)
            except:
                print(f"\n{RD}✗{R} Input tidak valid!")
                time.sleep(1)
        
        elif choice == "7":
            save_config()
            print(f"\n{GN}✓{R} Konfigurasi disimpan")
            write_log("Configuration saved", "INFO")
            time.sleep(1)
            break

def menu_domains():
    """Domain manager menu"""
    while True:
        banner()
        box("MANAJER DOMAIN")
        
        with db_conn() as conn:
            cursor = conn.execute("SELECT COUNT(*) as total FROM domains")
            total = cursor.fetchone()['total']
        
        stats_tld = get_tld_stats()
        
        print(f"\n{CY}Total Domain:{R} {B}{total}{R}")
        print(f"{CY}Kategori TLD:{R} {B}{len(stats_tld)}{R}\n")
        
        print(f"{P4}1.{R} Sync Domain dari Server")
        print(f"{P4}2.{R} Lihat Statistik TLD")
        print(f"{P4}0.{R} Kembali")
        
        choice = get_input("Pilih opsi")
        
        if choice == "1":
            sync_domains()
        elif choice == "2":
            menu_tld_stats()
        elif choice == "0":
            break

def menu_tld_stats():
    """TLD statistics menu"""
    banner()
    box("STATISTIK TLD")
    
    stats_tld = get_tld_stats()
    
    if not stats_tld:
        print(f"\n{YL}Tidak ada data TLD{R}")
        time.sleep(2)
        return
    
    # Sort by count
    sorted_tlds = sorted(stats_tld.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\n{CY}TLD{R}           {CY}Jumlah{R}")
    print(f"{GR}{'─' * 20}{R}")
    
    for tld, count in sorted_tlds[:20]:
        print(f".{tld.upper():<12} {B}{WH}{count:>5}{R}")
    
    total = sum(stats_tld.values())
    print(f"{GR}{'─' * 20}{R}")
    print(f"{CY}Total:{R}       {B}{WH}{total:>5}{R}")
    
    input(f"\n{P4}Tekan Enter untuk kembali...{R}")

def sync_domains():
    """Sync domains from server"""
    banner()
    box("SYNCHRONISASI DOMAIN", None, P2)
    
    print()
    loading_animation("Menghubungi server Tinyhost", 1.0)
    
    domains = email_api.get_all_domains(show_progress=True)
    
    if not domains:
        print(f"\n{RD}✗{R} Tidak ada domain diterima dari server")
        time.sleep(2)
        return
    
    print(f"\n{P4}⚡{R} {B}Memproses domain...{R}\n")
    
    added = 0
    
    with db_conn() as conn:
        for i, domain in enumerate(domains):
            tld = domain.split('.')[-1]
            try:
                cursor = conn.execute("SELECT id FROM domains WHERE domain = ?", (domain,))
                if not cursor.fetchone():
                    conn.execute("INSERT INTO domains (domain, tld) VALUES (?, ?)", (domain, tld))
                    added += 1
                
                if (i + 1) % 100 == 0:
                    progress = int((i + 1) / len(domains) * 40)
                    bar = f"{P3}{'█' * progress}{P1}{'░' * (40 - progress)}{R}"
                    print(f"\r{CY}Memproses{R} {bar} {B}{i+1}/{len(domains)}{R}", end='', flush=True)
            except:
                pass
        
        print(f"\r{CY}Memproses{R} {P3}{'█' * 40}{R} {B}{len(domains)}/{len(domains)}{R}")
    
    print(f"\n\n{GN}{'═' * W}{R}")
    print(f"  {GN}✓{R} {B}Domain baru ditambahkan:{R} {added}")
    print(f"  {CY}✓{R} {B}Total dalam database:{R} {added}")
    print(f"{GN}{'═' * W}{R}\n")
    
    time.sleep(2)

def menu_stats():
    """Statistics menu"""
    banner()
    box("STATISTIK")
    
    try:
        if not os.path.exists(OUTPUT_FILE):
            print(f"\n{YL}Belum ada akun yang dibuat{R}")
            time.sleep(2)
            return
        
        with open(OUTPUT_FILE, 'r') as f:
            lines = f.readlines()
        
        total = len(lines)
        with_cookies = sum(1 for line in lines if line.count('|') >= 3 and len(line.split('|')[3].strip()) > 20)
        
        print(f"\n{CY}Total Akun:{R} {B}{total}{R}")
        print(f"{GN}Dengan Cookies:{R} {B}{with_cookies}{R}")
        
        if total > 0:
            success_rate = (with_cookies / total) * 100
            print(f"{CY}Success Rate:{R} {B}{success_rate:.1f}%{R}")
        
        print(f"\n{CY}File Output:{R} {OUTPUT_FILE}")
        print(f"{CY}File Log:{R} {LOG_FILE}")
        
        if total > 0:
            print(f"\n{CY}Contoh Akun:{R}")
            for i, line in enumerate(lines[:3]):
                parts = line.strip().split('|')
                if len(parts) >= 4:
                    print(f"  {P4}{i+1}.{R} UID: {parts[0]}, Email: {parts[2][:20]}...")
        
    except Exception as e:
        write_log(f"Stats error: {str(e)}", "ERROR")
        print(f"\n{RD}Error membaca statistik: {str(e)}{R}")
    
    input(f"\n{P4}Tekan Enter untuk kembali...{R}")

# =============================================================================
# CREATION PROCESS WITH ULTRA LIVE MONITOR
# =============================================================================

def start_creation(domains):
    """Start creation process with ultra live monitor"""
    clear()
    banner()
    
    box("PROSES PEMBUATAN - SISTEM OTP ENHANCED", [
        f"{CY}Domain:{R} {B}{len(domains)}{R}",
        f"{CY}Target:{R} {B}{config.get('account_limit', 10)} akun{R}",
        f"{CY}Endpoint:{R} {B}{config.get('endpoint', 'desktop').title()}{R}",
        f"{CY}Metode:{R} {B}Pancingan → Change → Desktop OTP → Via Browser{R}"
    ])
    
    print()
    loading_animation("Memulai Worker 1 (Creation)", 0.5)
    worker1 = CreationWorker(1)
    worker1.start()
    
    loading_animation("Memulai Worker 2 (Monitor)", 0.5)
    worker2 = MonitorWorker(2)
    worker2.start()
    
    loading_animation("Memulai Worker 3 (Verifier)", 0.5)
    worker3 = VerifyWorker(3)
    worker3.start()
    
    account_limit = config.get('account_limit', 10)
    domain_index = 0
    
    # Reset stats
    with lock:
        stats.update({
            "total_created": 0,
            "total_verified": 0,
            "total_with_cookies": 0,
            "total_failed": 0,
            "worker1_status": "Starting...",
            "worker2_status": "Starting...",
            "worker3_status": "Starting...",
            "ok_count": 0,
            "cp_count": 0,
            "rejected_count": 0,
            "current_account": None,
            "last_success": None,
            "success_rate": 0.0,
            "current_process": "Starting workers...",
            "current_email": "None",
            "current_pancingan": "None",
            "start_time": time.time()
        })
    
    # Queue all tasks
    for i in range(account_limit):
        domain = domains[domain_index % len(domains)]
        creation_queue.put(domain)
        domain_index += 1
    
    print(f"\n{GN}{'='*W}{R}")
    print(f"{B}{WH}MEMBUAT {account_limit} AKUN DENGAN LIVE MONITOR{R}".center(W + 18))
    print(f"{GN}{'='*W}{R}")
    
    write_log(f"Creation started - Target: {account_limit} accounts", "SYSTEM")
    
    input(f"\n{P4}>>> Tekan Enter untuk memulai live monitor...{R}")
    
    start_time = time.time()
    last_display_time = time.time()
    
    # Initial display
    display_live_monitor_ultra(start_time, account_limit)
    
    # Main monitoring loop
    try:
        while True:
            current_time = time.time()
            
            # Check if we should stop
            with lock:
                total_created = stats['total_created']
            
            if total_created >= account_limit:
                # Check if queues are empty
                if (creation_queue.empty() and 
                    monitor_queue.empty() and 
                    verify_queue.empty()):
                    # Wait for workers to finish
                    time.sleep(2)
                    break
            
            # Update display every 3 seconds
            if current_time - last_display_time >= 2.0:
                display_live_monitor_ultra(start_time, account_limit)
                last_display_time = current_time
            
            # Short sleep to prevent CPU overload
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print(f"\n\n{RD}! PROSES DIINTERUPSI OLEH USER{R}")
        write_log("Process interrupted by user (Ctrl+C)", "SYSTEM")
    
    except Exception as e:
        print(f"\n\n{RD}! ERROR MONITOR: {str(e)}{R}")
        write_log(f"Monitor loop error: {str(e)}", "ERROR")
    
    # Stop workers
    print(f"\n{YL}Menghentikan semua worker...{R}")
    creation_queue.put("STOP")
    monitor_queue.put("STOP")
    verify_queue.put("STOP")
    
    # Give workers time to stop
    time.sleep(2)
    
    # Final display
    clear()
    display_live_monitor_ultra(start_time, account_limit)
    
    # Final stats
    duration = time.time() - start_time
    mins = int(duration // 60)
    secs = int(duration % 60)
    
    print(f"\n{GN}{'='*W}{R}")
    print(f"{B}{GN}{'PROSES SELESAI!':^60}{R}")
    print(f"{GN}{'='*W}{R}")
    
    print(f"\n  {GN}✓ HIDUP (Dengan Cookies):{R} {B}{stats['ok_count']}{R}")
    print(f"  {RD}✗ MATI (CP/Gagal):{R} {B}{stats['cp_count']}{R}")
    print(f"  {YL}✗ REJECT (No Email/OTP):{R} {B}{stats['rejected_count']}{R}")
    print(f"  {CY}• Total Diproses:{R} {B}{stats['total_created']}{R}")
    print(f"  {BL}⏱ Durasi:{R} {B}{mins:02d}m {secs:02d}s{R}")
    
    # Success rate
    if stats['total_created'] > 0:
        success_rate = (stats['ok_count'] / stats['total_created']) * 100
        print(f"  {PK}📊 Success Rate:{R} {B}{success_rate:.1f}%{R}")
    
    print(f"  {WH}📁 File Output:{R} {OUTPUT_FILE}")
    print(f"\n{GN}{'='*W}{R}")
    
    # Reset stats for next run
    with lock:
        stats.update({
            "total_created": 0,
            "total_verified": 0,
            "total_with_cookies": 0,
            "total_failed": 0,
            "worker1_status": "Idle",
            "worker2_status": "Idle",
            "worker3_status": "Idle",
            "ok_count": 0,
            "cp_count": 0,
            "rejected_count": 0,
            "current_account": None,
            "last_success": None,
            "success_rate": 0.0,
            "current_process": "Waiting...",
            "current_email": "None",
            "current_pancingan": "None",
            "start_time": None
        })
    
    input(f"\n{P4}>>> Tekan Enter untuk kembali ke menu...{R}")

# =============================================================================
# WELCOME SCREEN - ENHANCED
# =============================================================================

def welcome_screen():
    """Enhanced welcome screen with ASCII art"""
    clear()
    
    # ASCII Art Banner
    ascii_banner = [
        f"{P1}╔═══════════════════════════════════════════════════════════╗",
        f"{P1}║{P2}███████╗██████╗      ██████╗██████╗ ███████╗ █████╗ ████████╗ {P1}║",
        f"{P1}║{P3}██╔════╝██╔══██╗    ██╔════╝██╔══██╗██╔════╝██╔══██╗╚══██╔══╝ {P1}║",
        f"{P1}║{P4}█████╗  ██████╔╝    ██║     ██████╔╝█████╗  ███████║   ██║    {P1}║",
        f"{P1}║{P5}██╔══╝  ██╔══██╗    ██║     ██╔══██╗██╔══╝  ██╔══██║   ██║    {P1}║",
        f"{P1}║{PK}███████╗██║  ██║    ╚██████╗██║  ██║███████╗██║  ██║   ██║    {P1}║",
        f"{P1}║{P2}╚══════╝╚═╝  ╚═╝     ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝    {P1}║",
        f"{P1}║{P2}═══════════════════════════════════════════════════════{P1}║",
        f"{P1}║{MG}         ELITE FACEBOOK CREATOR - ULTRA EDITION        {P1}║",
        f"{P1}║{CY}       Pancingan → Tinyhost → OTP → Cookies           {P1}║",
        f"{P1}╚═══════════════════════════════════════════════════════════╝{R}",
        "",
        f"{P3}╔═══════════════════════════════════════════════════════════╗{R}",
        f"{P3}║{R}      {B}{PK}Developer: ZeeTheFounder • Version: Ultra{R}       {P3}║{R}",
        f"{P3}╚═══════════════════════════════════════════════════════════╝{R}",
        ""
    ]
    
    for line in ascii_banner:
        print(line)
        time.sleep(0.03)
    
    time.sleep(0.5)
    
    print(f"{B}{CY}Selamat datang di Elite Facebook Creator!{R}")
    print(f"{P4}Sistem Verifikasi OTP Enhanced{R}\n")
    time.sleep(0.5)
    
    loading_animation("Menginisialisasi Sistem Inti", 1.5)
    loading_animation("Memuat Modul Keamanan", 1.2)
    loading_animation("Mempersiapkan Worker Threads", 1.0)
    
    print(f"\n{GN}{'═' * W}{R}")
    print(f"{B}{WH}Sistem Siap!{R}".center(W + 18))
    print(f"{GN}{'═' * W}{R}\n")
    time.sleep(1)

# =============================================================================
# INITIALIZATION
# =============================================================================

def init_system():
    """Initialize system with enhanced UI"""
    try:
        banner()
        box("INISIALISASI SISTEM", [
            f"{BL}Arsitektur Triple-Worker{R}",
            f"{P4}Worker 1: Pembuatan Akun (Pancingan){R}",
            f"{P4}Worker 2: Monitoring OTP (Tinyhost){R}",
            f"{P4}Worker 3: Desktop OTP + Via Browser Extract{R}"
        ])
        
        print()
        loading_animation("Menginisialisasi database", 1.0)
        init_db()
        
        loading_animation("Memuat konfigurasi", 0.8)
        load_config()
        
        loading_animation("Membersihkan log lama", 0.5)
        clear_logs()
        
        with db_conn() as conn:
            cursor = conn.execute("SELECT COUNT(*) as total FROM domains")
            total = cursor.fetchone()['total']
        
        if total == 0:
            print(f"\n{YL}!{R} {B}Tidak ada domain di database lokal{R}")
            loading_animation("Menghubungi server", 1.0)
            
            domains = email_api.get_all_domains(show_progress=True)
            
            if domains:
                print(f"\n{P4}⚡{R} {B}Menyimpan domain...{R}")
                with db_conn() as conn:
                    stored = 0
                    for domain in domains:
                        tld = domain.split('.')[-1]
                        try:
                            conn.execute("INSERT OR IGNORE INTO domains (domain, tld) VALUES (?, ?)", (domain, tld))
                            stored += 1
                        except:
                            pass
                print(f"\n{GN}✓{R} {B}Domain tersimpan: {stored}{R}")
        else:
            print(f"\n{GN}✓{R} {B}Domain ditemukan: {total}{R}")
        
        print()
        loading_animation("Sistem siap", 1.0)
        
        print(f"\n{GN}{'═' * W}{R}")
        print(f"{B}{GN}✓ Inisialisasi Selesai!{R}".center(W + 24))
        print(f"{GN}{'═' * W}{R}\n")
        time.sleep(1.5)
        return True
    except Exception as e:
        print(f"\n{RD}✗{R} {B}Inisialisasi gagal: {str(e)}{R}")
        write_log(f"Init failed: {str(e)}", "ERROR")
        time.sleep(3)
        return False

# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main function"""
    try:
        welcome_screen()
        
        if not init_system():
            print(f"\n{RD}✗{R} {B}Startup gagal{R}")
            return
        
        menu_main()
        
    except KeyboardInterrupt:
        clear()
        print(f"\n{P3}{'═' * W}{R}")
        print(f"{B}{YL}! Diinterupsi oleh user{R}".center(W + 20))
        print(f"{P3}{'═' * W}{R}\n")
        write_log("Interrupted by user", "SYSTEM")
        time.sleep(1)
    except Exception as e:
        print(f"\n{RD}✗{R} {B}Fatal error: {str(e)}{R}")
        write_log(f"Fatal error: {str(e)}", "ERROR")
        time.sleep(2)

if __name__ == "__main__":
    main()
