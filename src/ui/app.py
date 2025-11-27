import streamlit as st
import sys
import os
import browser_cookie3
import tempfile
from pathlib import Path
try:
    import tkinter as tk
    from tkinter import filedialog
except Exception:
    tk = None
    filedialog = None

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.core.scraper import FanqieScraper
from src.core.utils import clean_filename, UA_CHROME, UA_EDGE, UA_FIREFOX, UA_MACOS_CHROME, UA_SAFARI, log_debug
from src.core.path_utils import get_desktop_path
from src.core.path_utils import get_documents_path
import platform
import time
import threading
from streamlit.web.server.server import Server

# --- Auto Shutdown Logic ---
def auto_shutdown_loop():
    time.sleep(2)
    idle_start = None
    had_session = False
    while True:
        try:
            current_server = Server.get_current()
            session_infos = current_server._session_info_by_id
            active_count = len(session_infos)
        except Exception:
            active_count = 1
        if active_count > 0:
            had_session = True
            idle_start = None
        else:
            if had_session:
                if idle_start is None:
                    idle_start = time.time()
                elif time.time() - idle_start > 2.0:
                    try:
                        if len(Server.get_current()._session_info_by_id) == 0:
                            os._exit(0)
                    except Exception:
                        os._exit(0)
        time.sleep(0.5)

# Start background thread singleton
found_thread = False
for t in threading.enumerate():
    if t.name == "StreamlitAutoShutdown":
        found_thread = True
        break

if not found_thread:
    t = threading.Thread(target=auto_shutdown_loop, name="StreamlitAutoShutdown", daemon=True)
    t.start()
# ---------------------------

st.set_page_config(page_title="洋柿子小说下载器", page_icon="🍅")

# --- Theme Management ---
if 'theme' not in st.session_state:
    st.session_state.theme = "活力橙"
allowed_themes = ["豆沙绿", "活力橙"]
if st.session_state.get('theme') not in allowed_themes:
    st.session_state.theme = "活力橙"

def get_theme_css(theme_name):
    themes = {
        
        "豆沙绿": {
            "bg": "#C7EDCC",
            "card_bg": "rgba(255, 255, 255, 0.4)",
            "text": "#2E4033",
            "border": "1px solid rgba(199, 237, 204, 0.8)",
            "shadow": "0 8px 32px 0 rgba(0, 100, 0, 0.05)",
            "input_bg": "rgba(255, 255, 255, 0.5)",
            "dropdown_bg": "#f0f9f0",
            "placeholder": "rgba(46,64,51,0.6)",
            "accent": "#2AA96B"
        },
        "活力橙": {
            "bg": "linear-gradient(120deg, #f6d365 0%, #fda085 100%)",
            "card_bg": "rgba(255, 255, 255, 0.45)",
            "text": "#4A2C2A",
            "border": "1px solid rgba(255, 255, 255, 0.5)",
            "shadow": "0 8px 32px 0 rgba(255, 100, 0, 0.15)",
            "input_bg": "rgba(255, 255, 255, 0.6)",
            "dropdown_bg": "#fff5e6",
            "placeholder": "rgba(74,44,42,0.55)",
            "accent": "#FF9800"
        }
    }
    
    t = themes.get(theme_name, themes["活力橙"])
    
    # Text color handling for dark mode vs light mode components
    input_text_color = t['text']
    
    return f"""
    <style>
    /* Global Background */
    .stApp {{
        background: {t['bg']};
        background-attachment: fixed;
        color: {t['text']};
    }}
    
    /* Liquid Glass Effect for Containers */
    div[data-testid="stExpander"], div[data-testid="stForm"] {{
        background: {t['card_bg']};
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 16px;
        border: {t['border']};
        box-shadow: {t['shadow']};
        padding: 10px;
    }}

    /* Inputs and Selectboxes */
    .stTextInput > div > div, .stSelectbox > div > div {{
        background: {t['input_bg']} !important;
        backdrop-filter: blur(10px);
        border-radius: 12px;
        border: {t['border']} !important;
        color: {input_text_color} !important;
    }}
    .stMultiSelect > div > div, .stNumberInput > div > div, .stTextArea > div > div {{
        background: {t['input_bg']} !important;
        border: {t['border']} !important;
        color: {t['text']} !important;
    }}
    input, textarea {{
        color: {t['text']} !important;
        background: transparent !important;
    }}
    input::placeholder, textarea::placeholder {{
        color: {t['placeholder']} !important;
        opacity: 1 !important;
    }}
    .stMultiSelect > div > div, .stNumberInput > div > div, .stTextArea > div > div {{
        background: {t['input_bg']} !important;
        border: {t['border']} !important;
        color: {t['text']} !important;
    }}
    input, textarea {{
        color: {t['text']} !important;
        background: transparent !important;
    }}
    input::placeholder, textarea::placeholder {{
        color: {t['placeholder']} !important;
        opacity: 1 !important;
    }}
    
    /* Fix Dropdown Menu Visibility (especially for Dark Mode) */
    div[data-baseweb="popover"] {{
        background-color: {t['dropdown_bg']} !important;
        border-radius: 12px !important;
        border: {t['border']} !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.25) !important;
    }}
    div[data-baseweb="popover"] * {{
        color: {t['text']} !important;
    }}
    ul[data-baseweb="menu"], ul[role="listbox"] {{
        background-color: {t['dropdown_bg']} !important;
    }}
    div[data-baseweb="menu"], div[role="listbox"] {{
        background-color: {t['dropdown_bg']} !important;
    }}
    li[data-baseweb="menu-item"], li[role="option"] {{
        color: {t['text']} !important;
    }}
    li[data-baseweb="menu-item"] div, li[role="option"] div {{
        color: {t['text']} !important;
    }}
    li[role="option"][aria-disabled="true"] {{
        opacity: 0.7 !important;
        color: {t['text']} !important;
    }}
    li[data-baseweb="menu-item"]:hover, li[role="option"]:hover {{
        background: rgba(255,255,255,0.12) !important;
    }}
    li[aria-selected="true"][data-baseweb="menu-item"], li[aria-selected="true"][role="option"] {{
        background: rgba(255,255,255,0.18) !important;
    }}
    div[data-baseweb="select"] *, div[data-baseweb="select"] svg {{
        color: {t['text']} !important;
        fill: {t['text']} !important;
    }}
    div[data-testid="stExpander"] > div[role="button"] {{
        background: {t['card_bg']} !important;
        color: {t['text']} !important;
        border: {t['border']} !important;
    }}
    div[data-testid="stExpander"] svg {{
        fill: {t['text']} !important;
    }}
    
    /* Text Color overrides */
    h1, h2, h3, p, label, .stMarkdown, .stText, span, div {{
        color: {t['text']} !important;
    }}
    .stSelectbox label, .stTextInput label, .stMultiSelect label, .stNumberInput label {{
        color: {t['text']} !important;
    }}
    
    /* Button Styling to match */
    .stButton > button {{
        background: {t['card_bg']} !important;
        color: {t['text']} !important;
        border: {t['border']} !important;
        border-radius: 12px;
        backdrop-filter: blur(5px);
        transition: all 0.3s ease;
        font-weight: bold;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        filter: brightness(1.1);
    }}
    .stDownloadButton > button {{
        background: {t['card_bg']} !important;
        color: {t['text']} !important;
        border: {t['border']} !important;
        border-radius: 12px !important;
    }}
    .stAlert {{
        border-radius: 12px !important;
        border: {t['border']} !important;
        background: {t['card_bg']} !important;
        color: {t['text']} !important;
    }}
    
    /* Hide Deploy/Toolbar */
    [data-testid="stToolbar"] {{visibility: hidden; height: 0; position: fixed;}}
    .viewerBadge_container__1QSob {{display: none;}}
    .viewerBadge_container__2Ynd {{display: none;}}
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    </style>
    """

st.markdown(get_theme_css(st.session_state.theme), unsafe_allow_html=True)

st.title("🍅 洋柿子小说下载器")

# 安装成功提醒（首次在 /Applications 路径运行时）
try:
    exe_path = sys.executable
    if '/Applications/' in exe_path:
        marker_dir = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'YangShiziDownloader')
        os.makedirs(marker_dir, exist_ok=True)
        marker = os.path.join(marker_dir, 'installed.flag')
        if not os.path.exists(marker):
            with open(marker, 'w') as f:
                f.write('ok')
            st.success("安装成功，已就绪！")
except Exception:
    pass

with st.expander("⚙️ 软件设置", expanded=False):
    st.write("🎨 **界面主题**")
    st.selectbox(
        "选择主题",
        ["豆沙绿", "活力橙"],
        key="theme",
        label_visibility="collapsed"
    )

    with st.expander("📝 启动日志", expanded=False):
        p = os.path.join(tempfile.gettempdir(), "fanqie_startup.log")
        try:
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                content_tail = content[-5000:]
                st.code(content_tail if content_tail else "暂无日志")
            else:
                st.info("暂无日志")
        except Exception:
            st.info("暂无日志")

    # 默认保存位置设置
    with st.expander("🗃️ 文件保存位置", expanded=True):
        if 'save_dir_choice' not in st.session_state:
            st.session_state.save_dir_choice = "自动识别桌面"
        if 'custom_save_dir' not in st.session_state:
            st.session_state.custom_save_dir = ""
        if 'save_dir' not in st.session_state:
            st.session_state.save_dir = None

        st.radio(
            "默认保存位置",
            ["自动识别桌面", "文档目录", "自定义目录"],
            key="save_dir_choice",
            help="为避免在不同电脑上使用绝对路径，建议选择自动识别或文档目录；如需自定义，请确保路径存在且有写入权限。"
        )

        def pick_directory_dialog():
            if tk is None or filedialog is None:
                return None
            try:
                root = tk.Tk()
                root.withdraw()
                path = filedialog.askdirectory(title="选择保存目录")
                root.destroy()
                return path or None
            except Exception:
                return None

        if st.session_state.save_dir_choice == "自定义目录":
            col_sd1, col_sd2 = st.columns([3, 1])
            with col_sd1:
                st.text_input("自定义目录路径", key="custom_save_dir", placeholder=r"例如 C:\\Users\\你的用户名\\Downloads")
            with col_sd2:
                st.write("")
                if st.button("选择目录"):
                    selected = pick_directory_dialog()
                    if selected:
                        st.session_state.custom_save_dir = selected
                        st.success(f"已选择目录：{selected}")
                    else:
                        st.info("无法打开系统目录选择，已启用手动输入")

            if st.button("保存并验证目录"):
                target = st.session_state.custom_save_dir.strip()
                if target:
                    try:
                        os.makedirs(target, exist_ok=True)
                        st.session_state.save_dir = target
                        st.success(f"默认保存位置已设置：{target}")
                    except Exception as e:
                        st.error(f"目录不可用：{e}")
                else:
                    st.error("请输入或选择有效目录路径")
        else:
            try:
                if st.session_state.save_dir_choice == "自动识别桌面":
                    detected = get_desktop_path()
                else:
                    detected = get_documents_path()
                os.makedirs(detected, exist_ok=True)
                st.session_state.save_dir = detected
                st.info(f"默认保存位置：{detected}")
            except Exception as e:
                st.error(f"保存位置不可用：{e}")

# Sidebar for app control
# Removed as per user request
# with st.sidebar:
#     st.header("程序控制")
#     if st.button("🔴 关闭程序"):
#         st.warning("正在关闭程序...")
#         os._exit(0)
#     st.info("如果下载出现问题，请先尝试点击上方按钮彻底关闭程序，然后重新打开。")

st.markdown("""
**说明**: 
1. 输入小说主页链接。
2. 点击“获取信息”查看小说详情。
3. 下载 VIP 章节前，请务必使用您选择的浏览器先登录番茄小说网的会员账号；完成登录后点击“🖥️ 自动获取 Cookie”，再开始下载。
4. **如仍失败**：请在该浏览器里手动打开任意一章 VIP 内容刷新一次，然后关闭页面回到本程序重试。
""")

def get_browser_cookies(domain_name):
    """Try to load cookies from common browsers with robust fallbacks."""
    log_debug(f"Attempting to load cookies for domain: {domain_name}")
    cookies = []

    def filter_domain(jar):
        try:
            lst = [c for c in list(jar) if (c.domain and ("fanqie" in c.domain or "fqnovel" in c.domain or "fanqienovel" in c.domain))]
            return lst
        except Exception:
            return []

    # Try Chrome
    try:
        log_debug("Checking Chrome...")
        cj = browser_cookie3.chrome(domain_name=domain_name)
        found = list(cj)
        if len(found) == 0:
            cj_all = browser_cookie3.chrome()
            found = filter_domain(cj_all)
        if len(found) > 0:
            log_debug(f"Found {len(found)} cookies in Chrome")
            cookies.append(("Chrome", found))
        else:
            log_debug("Chrome cookies empty for domain")
    except Exception as e:
        log_debug(f"Chrome cookie error: {e}")
    
    # Try Edge
    try:
        log_debug("Checking Edge...")
        cj = browser_cookie3.edge(domain_name=domain_name)
        found = list(cj)
        if len(found) == 0:
            cj_all = browser_cookie3.edge()
            found = filter_domain(cj_all)
        if len(found) > 0:
            log_debug(f"Found {len(found)} cookies in Edge")
            cookies.append(("Edge", found))
        else:
            log_debug("Edge cookies empty for domain")
    except Exception as e:
        log_debug(f"Edge cookie error: {e}")
        
    # Try Firefox
    try:
        log_debug("Checking Firefox...")
        cj = browser_cookie3.firefox(domain_name=domain_name)
        found = list(cj)
        if len(found) == 0:
            cj_all = browser_cookie3.firefox()
            found = filter_domain(cj_all)
        if len(found) > 0:
            log_debug(f"Found {len(found)} cookies in Firefox")
            cookies.append(("Firefox", found))
        else:
            log_debug("Firefox cookies empty for domain")
    except Exception as e:
        log_debug(f"Firefox cookie error: {e}")
        
    return cookies

def format_cookie_str(cookie_jar):
    return "; ".join([f"{c.name}={c.value}" for c in cookie_jar])

url = st.text_input("小说主页链接", placeholder="https://fanqienovel.com/page/...")

# Cookie handling
st.markdown("### 🔑 VIP 登录 (可选)")

# Add Browser Selection
browser_type = st.selectbox(
    "Cookie 来源浏览器 (必须与登录浏览器一致)",
    ["Chrome / Edge", "Safari", "Firefox"],
    help="请务必选择你登录番茄小说会员的浏览器。选择错误将无法下载 VIP 章节"
)
st.warning("下载 VIP 章节前，请确保上方浏览器选择与您实际登录的浏览器完全一致。否则将无法下载。")

col_c1, col_c2 = st.columns([3, 1])

with col_c1:
    cookie_str = st.text_input("Cookie (手动输入)", type="password", help="在浏览器控制台输入 document.cookie 获取")

with col_c2:
    st.write("") # Spacer
    st.write("") 
    if st.button("🖥️ 自动获取 Cookie"):
        with st.spinner("正在从浏览器获取 Cookie..."):
            # 根据用户选择限制尝试范围，避免无关错误
            found_cookies = []
            try:
                if browser_type == "Chrome / Edge":
                    # 优先 Chrome，其次 Edge
                    try:
                        cj = browser_cookie3.chrome(domain_name="fanqienovel.com")
                        lst = list(cj)
                        if not lst:
                            lst = [c for c in list(browser_cookie3.chrome()) if (c.domain and ("fanqie" in c.domain or "fqnovel" in c.domain or "fanqienovel" in c.domain))]
                        if lst:
                            found_cookies.append(("Chrome", lst))
                    except Exception:
                        pass
                    if not found_cookies:
                        try:
                            cj = browser_cookie3.edge(domain_name="fanqienovel.com")
                            lst = list(cj)
                            if not lst:
                                lst = [c for c in list(browser_cookie3.edge()) if (c.domain and ("fanqie" in c.domain or "fqnovel" in c.domain or "fanqienovel" in c.domain))]
                            if lst:
                                found_cookies.append(("Edge", lst))
                        except Exception:
                            pass
                elif browser_type == "Firefox":
                    try:
                        cj = browser_cookie3.firefox(domain_name="fanqienovel.com")
                        lst = list(cj)
                        if not lst:
                            lst = [c for c in list(browser_cookie3.firefox()) if (c.domain and ("fanqie" in c.domain or "fqnovel" in c.domain or "fanqienovel" in c.domain))]
                        if lst:
                            found_cookies.append(("Firefox", lst))
                    except Exception:
                        pass
                else:
                    st.warning("Safari 暂不支持自动读取 Cookie，请在上方手动输入。")
            except Exception as e:
                st.error(f"读取浏览器 Cookie 失败：{e}")

            if found_cookies:
                name, jar = found_cookies[0]
                cookie_str_val = format_cookie_str(jar)
                ua = None
                if name == "Chrome":
                    ua = UA_MACOS_CHROME if platform.system() == 'Darwin' else UA_CHROME
                elif name == "Edge":
                    ua = UA_EDGE
                elif name == "Firefox":
                    ua = UA_FIREFOX

                st.session_state['auto_cookie'] = cookie_str_val
                st.session_state['auto_ua'] = ua
                st.success(f"已从 {name} 获取 Cookie! (长度: {len(cookie_str_val)} 字符)")
            else:
                st.error("未找到番茄小说 Cookie，请确认已在对应浏览器登录番茄账号并访问过 VIP 章节。")
                st.info("可在浏览器控制台输入 document.cookie 复制后粘贴到上方输入框。")

# Use session state cookie if available and input is empty
if 'auto_cookie' in st.session_state and not cookie_str:
    cookie_str = st.session_state['auto_cookie']
    st.info("已自动填充 Cookie")

if 'novel_data' not in st.session_state:
    st.session_state.novel_data = None
if 'chapters' not in st.session_state:
    st.session_state.chapters = []

    if st.button("获取信息"):
        if not url:
            st.error("请输入链接")
        else:
            with st.spinner("正在获取小说信息..."):
                user_agent = st.session_state.get('auto_ua')
                if not user_agent:
                    if browser_type == "Safari":
                        user_agent = UA_SAFARI
                    elif browser_type == "Firefox":
                        user_agent = UA_FIREFOX
                    else:
                        user_agent = UA_MACOS_CHROME if platform.system() == 'Darwin' else UA_CHROME
            
            save_dir = st.session_state.get('save_dir') or get_desktop_path()
            scraper = FanqieScraper(cookie_str, user_agent, save_dir=save_dir)
            metadata = scraper.get_novel_metadata(url)
            if metadata:
                st.session_state.novel_data = metadata
                st.session_state.chapters = scraper.get_chapter_list(url)
                st.success("获取成功！")
            else:
                st.error("获取失败，请检查链接或网络。")

if st.session_state.novel_data:
    novel = st.session_state.novel_data
    st.divider()
    col1, col2 = st.columns([1, 3])
    with col1:
        if novel.get('cover_url'):
            st.image(novel['cover_url'], width=150)
    with col2:
        st.subheader(novel['title'])
        st.write(f"**作者**: {novel['author']}")
        st.write(f"**章节数**: {len(st.session_state.chapters)}")

    st.divider()
    
    # Range selection
    chapter_options = [f"{i+1}. {c['title']}" for i, c in enumerate(st.session_state.chapters)]
    
    # Select All Checkbox
    select_all = st.checkbox("全选所有章节", value=True)
    
    if select_all:
        selected_chapters = st.multiselect("选择章节", chapter_options, default=chapter_options)
    else:
        selected_chapters = st.multiselect("选择章节", chapter_options)
    
    if st.button("开始下载"):
        user_agent = st.session_state.get('auto_ua')
        if not user_agent:
            if browser_type == "Safari":
                user_agent = UA_SAFARI
            elif browser_type == "Firefox":
                user_agent = UA_FIREFOX
            else:
                user_agent = UA_MACOS_CHROME if platform.system() == 'Darwin' else UA_CHROME
                
        save_dir = st.session_state.get('save_dir') or get_desktop_path()
        scraper = FanqieScraper(cookie_str, user_agent, save_dir=save_dir)
        
        # Determine chapters to download
        chapters_to_download = []
        if not selected_chapters:
            # Fallback if somehow nothing selected but list is empty, though 'select all' handles this
            chapters_to_download = [] 
            st.warning("请至少选择一个章节")
        else:
            indices = [int(s.split('.')[0]) - 1 for s in selected_chapters]
            chapters_to_download = [st.session_state.chapters[i] for i in sorted(indices)]

        if chapters_to_download:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Prepare result list
            downloaded_content = []
            
            completed_count = 0
            failed_count = 0
            
            import random
            
            # Single-threaded download
            for i, chapter in enumerate(chapters_to_download):
                try:
                    # Random delay to avoid detection
                    time.sleep(random.uniform(0.5, 1.5))
                    
                    content = scraper.get_chapter_content(chapter['url'])
                    if content:
                        content['title'] = chapter['title']
                        downloaded_content.append(content)
                        completed_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    log_debug(f"Error fetching {chapter['title']}: {e}")
                    failed_count += 1
                
                # Update progress
                progress = (i + 1) / len(chapters_to_download)
                progress_bar.progress(progress)
                status_text.text(f"进度: {i + 1}/{len(chapters_to_download)} (成功: {completed_count}, 失败: {failed_count})")
            
            # Filter out failed downloads (already filtered by append logic)
            valid_content = downloaded_content
            
            if not valid_content:
                st.error("所有章节下载失败！请检查：\n1. 网络连接\n2. 是否需要更新 Cookie (VIP章节)")
                status_text.text("下载失败")
            else:
                if failed_count > 0:
                    st.warning(f"下载完成，但有 {failed_count} 个章节失败。")
                else:
                    st.success("所有章节下载完成！")
                
                status_text.text("正在生成文件...")
                
                filename = clean_filename(novel['title'])
                
                file_content = scraper.generate_txt(novel, valid_content)
                file_ext = "txt"
                mime_type = "text/plain"
                    
                # 自动保存到用户选择的目录（或自动识别的桌面/文档）
                try:
                    save_dir = st.session_state.get('save_dir') or get_desktop_path()
                    save_path = os.path.join(save_dir, f"{filename}.{file_ext}")
                    with open(save_path, "w", encoding="utf-8") as f:
                        f.write(file_content)
                    st.success(f"✅ 文件已保存到: **{save_path}**")
                except Exception as e:
                    st.error(f"自动保存失败: {e}")

                st.download_button(
                    label=f"点击下载 {file_ext.upper()} 文件 (另存为)",
                    data=file_content,
                    file_name=f"{filename}.{file_ext}",
                    mime=mime_type
                )
                st.balloons()
