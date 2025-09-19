import platform
import subprocess
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
import re
import sys
import json
import time
import random
import sqlite3

# 导入数据库管理模块
TG_LINK_RE = re.compile(r"((?:https?://)?t\.me/[A-Za-z0-9_+/?=-]+)", re.I)


class DatabaseManager:
    def __init__(self, db_path: str = "telegram_links.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """初始化数据库和表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS telegram_links
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               link
                               TEXT
                               UNIQUE
                               NOT
                               NULL,
                               source
                               TEXT,
                               keyword
                               TEXT,
                               created_at
                               TIMESTAMP
                               DEFAULT
                               CURRENT_TIMESTAMP,
                               updated_at
                               TIMESTAMP
                               DEFAULT
                               CURRENT_TIMESTAMP
                           )
                           ''')

            # 创建索引提高查询性能
            cursor.execute('''
                           CREATE INDEX IF NOT EXISTS idx_link ON telegram_links(link)
                           ''')
            cursor.execute('''
                           CREATE INDEX IF NOT EXISTS idx_keyword ON telegram_links(keyword)
                           ''')

            conn.commit()

    def save_link(self, link_info: dict, keyword: str) -> bool:
        """
        保存单个链接到数据库
        返回是否成功保存（True表示新保存，False表示已存在）
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                               INSERT
                               OR IGNORE INTO telegram_links (link, source, keyword)
                    VALUES (?, ?, ?)
                               ''', (link_info['link'], link_info.get('source', ''), keyword))

                conn.commit()
                return cursor.rowcount > 0  # 如果插入成功返回True
        except Exception as e:
            print(f"[DB] 保存链接 {link_info['link']} 时出错: {e}", flush=True)
            return False

    def link_exists(self, link: str) -> bool:
        """检查链接是否已存在"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                           SELECT 1
                           FROM telegram_links
                           WHERE link = ? LIMIT 1
                           ''', (link,))

            return cursor.fetchone() is not None


def extract_tg_links_from_text(text):
    matches = set(m.group(0) for m in TG_LINK_RE.finditer(text))
    # 标准化链接，确保都有 https:// 前缀
    normalized_links = set()
    for match in matches:
        if not match.startswith('http'):
            normalized_links.add('https://' + match)
        else:
            normalized_links.add(match)
    return normalized_links


# ---------------- 启动系统浏览器让用户登录 ----------------
def launch_browser_for_login(port=9222, profile_dir=None):
    system = platform.system()
    user_home = str(Path.home())
    if profile_dir is None:
        profile_dir = str(Path(user_home) / ".x_debug_profile")

    if system == "Darwin":
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    elif system == "Windows":
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    else:
        chrome_path = "/usr/bin/google-chrome"

    # 检查浏览器是否存在
    if not Path(chrome_path).exists():
        print(f"[Worker] 错误: 找不到Chrome浏览器在路径 {chrome_path}", flush=True)
        print("[Worker] 请确保已安装Google Chrome浏览器", flush=True)
        return

    cmd = [chrome_path, f"--remote-debugging-port={port}", f"--user-data-dir={profile_dir}"]
    print(f"[Worker] 启动浏览器命令: {' '.join(cmd)}", flush=True)

    try:
        # 使用列表形式的命令和preexec_fn来避免僵尸进程
        process = subprocess.Popen(cmd,
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL,
                                   start_new_session=True)
        time.sleep(3)
        print(f"[Worker] 浏览器已启动，PID: {process.pid}", flush=True)
    except Exception as e:
        print(f"[Worker] 启动浏览器失败: {e}", flush=True)


# ---------------- attach 浏览器保存登录态 ----------------
def attach_and_save_login(storage_state="storage_state.json", port=9222):
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(f"http://localhost:{port}")
            context = browser.contexts[0]
            context.storage_state(path=storage_state)
            print(f"[Worker] 登录态已保存到 {storage_state}", flush=True)
    except Exception as e:
        print(f"[Worker] 保存登录态失败: {e}", flush=True)


# ---------------- 抓取 t.me 链接（新策略） ----------------
def search_keyword(keyword, storage_state="storage_state.json", keep_browser_open=False):
    """
    使用新策略搜索Telegram链接

    Args:
        keyword: 搜索关键词
        storage_state: 登录状态文件路径
        keep_browser_open: 是否在搜索完成后保持浏览器打开
    """
    # 初始化数据库
    db_manager = DatabaseManager()

    # 用于跟踪本轮已发现的链接，避免重复处理


本轮_links_found = set()

# 使用不同的搜索参数和时间参数来获取更多结果
base_urls = [
    f"https://x.com/search?q={keyword}",
    f"https://x.com/search?q={keyword}&f=live",
]

# 添加时间过滤参数以获取更多历史数据
time_filters = [
    "",  # 无时间过滤
    "&f=live",  # 实时
]

urls = []
for base_url in base_urls:
    for time_filter in time_filters:
        urls.append(base_url + time_filter)

if not Path(storage_state).exists():
    print("[Worker] 登录态不存在，请先登录", flush=True)
    return []

browser = None
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-gpu",
                "--disable-software-rasterizer",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-web-security"
            ]
        )
        context = browser.new_context(storage_state=storage_state)

        # 添加随机User-Agent以减少被识别为机器人的可能性
        context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """)

        page = context.new_page()
        page.set_viewport_size({
            "width": random.randint(1200, 1920),
            "height": random.randint(800, 1080)
        })

        total_saved_count = 0  # 总共保存到数据库的链接数

        # 尝试多个搜索URL
        for url_index, url in enumerate(urls):
            print(f"[Worker] 正在打开搜索页面 {url_index + 1}/{len(urls)}: {url}", flush=True)
            try:
                page.goto(url, wait_until="load", timeout=30000)
                print(f"[Worker] 页面加载完成", flush=True)
            except Exception as e:
                print(f"[Worker] 页面加载失败: {e}", flush=True)
                continue

            # 等待初始内容加载
            time.sleep(5)

            # 尝试等待推文加载
            try:
                page.wait_for_selector("[data-testid='tweet']", timeout=10000)
                print("[Worker] 推文内容已加载", flush=True)
            except Exception as e:
                print(f"[Worker] 等待推文加载超时: {e}", flush=True)

            # 滚动加载更多内容 - 分多轮进行，每轮30次滚动后刷新
            print("[Worker] 开始滚动加载更多内容...", flush=True)
            rounds = 3  # 进行3轮滚动
            scrolls_per_round = 30  # 每轮30次滚动

            for round_num in range(rounds):
                print(f"[Worker] 开始第 {round_num + 1} 轮滚动 (每轮30次)", flush=True)

                last_height = 0
                same_height_count = 0

                for scroll_count in range(scrolls_per_round):
                    print(f"[Worker] 第 {round_num + 1} 轮, 第 {scroll_count + 1} 次滚动", flush=True)

                    # 获取当前页面高度
                    current_height = page.evaluate("document.body.scrollHeight")
                    print(f"[Worker] 当前页面高度: {current_height}", flush=True)

                    # 滚动到页面底部
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

                    # 等待新内容加载 (4-8秒随机时间，增加等待时间)
                    wait_time = random.uniform(4, 8)
                    print(f"[Worker] 等待 {wait_time:.1f} 秒让新内容加载...", flush=True)
                    time.sleep(wait_time)

                    # 检查页面是否还在增长
                    new_height = page.evaluate("document.body.scrollHeight")
                    print(f"[Worker] 新页面高度: {new_height}", flush=True)

                    if new_height == current_height:
                        same_height_count += 1
                        print(f"[Worker] 页面高度未变化 ({same_height_count}/3)", flush=True)
                        if same_height_count >= 3:
                            print("[Worker] 页面高度连续3次未变化，停止本轮滚动", flush=True)
                            break
                    else:
                        same_height_count = 0

                    # 每次滚动后都检查链接
                    print(f"[Worker] 滚动后检查链接...", flush=True)

                    # 分析当前页面上的推文
                    tweet_elements = page.query_selector_all("[data-testid='tweet']")
                    print(f"[Worker] 当前找到 {len(tweet_elements)} 个推文元素", flush=True)

                    # 分析所有推文
                    for i, tweet in enumerate(tweet_elements):
                        try:
                            tweet_html = tweet.inner_html()
                            if "t.me" in tweet_html:
                                print(f"[Worker] 在推文 {i + 1} 中发现 t.me", flush=True)
                                links = extract_tg_links_from_text(tweet_html)
                                # 处理每个发现的链接
                                for link in links:
                                    # 检查本轮是否已处理过
                                    if link in 本轮_links_found:
                                        continue

                                    # 检查数据库中是否已存在
                                    if db_manager.link_exists(link):
                                        print(f"[Worker] 链接 {link} 已存在于数据库中", flush=True)
                                        本轮_links_found.add(link)
                                        continue

                                    # 保存新链接到数据库
                                    link_info = {"link": link, "source": url}
                                    if db_manager.save_link(link_info, keyword):
                                        本轮_links_found.add(link)
                                        total_saved_count += 1
                                        print(f"[DB] 成功保存新链接: {link}", flush=True)
                                    else:
                                        本轮_links_found.add(link)
                                        print(f"[DB] 链接已存在或保存失败: {link}", flush=True)
                        except Exception as e:
                            continue

                    print(
                        f"[Worker] 当前本轮已发现 {len(本轮_links_found)} 个链接，总共保存 {total_saved_count} 个到数据库",
                        flush=True)

                # 每轮结束后，如果还有下一轮，刷新页面
                if round_num < rounds - 1:
                    print(f"[Worker] 第 {round_num + 1} 轮滚动完成，刷新页面继续...", flush=True)
                    try:
                        page.reload(wait_until="load", timeout=30000)
                        print("[Worker] 页面刷新完成", flush=True)
                        time.sleep(5)  # 等待页面重新加载
                    except Exception as e:
                        print(f"[Worker] 页面刷新失败: {e}", flush=True)

            # 每个URL之间暂停更长时间
            if url_index < len(urls) - 1:
                pause_time = random.uniform(15, 20)
                print(f"[Worker] 切换到下一个搜索URL前暂停 {pause_time:.1f} 秒...", flush=True)
                time.sleep(pause_time)

        # 最后从整个页面提取一次
        print("[Worker] 最终从整个页面提取链接...", flush=True)
        page_content = page.content()
        page_links = extract_tg_links_from_text(page_content)

        # 处理页面中找到的链接
        for link in page_links:
            # 检查本轮是否已处理过
            if link in 本轮_links_found:
                continue

            # 检查数据库中是否已存在
            if db_manager.link_exists(link):
                print(f"[Worker] 链接 {link} 已存在于数据库中", flush=True)
                本轮_links_found.add(link)
                continue

            # 保存新链接到数据库
            link_info = {"link": link, "source": "page_content"}
            if db_manager.save_link(link_info, keyword):
                本轮_links_found.add(link)
                total_saved_count += 1
                print(f"[DB] 成功保存新链接: {link}", flush=True)
            else:
                本轮_links_found.add(link)
                print(f"[DB] 链接已存在或保存失败: {link}", flush=True)

        print(f"[Worker] 搜索完成，本轮总共保存 {total_saved_count} 个新链接到数据库", flush=True)
        print(f"[Worker] 本轮总共发现 {len(本轮_links_found)} 个链接", flush=True)

        # 根据参数决定是否关闭浏览器
        if not keep_browser_open:
            browser.close()
            browser = None
            print("[Worker] 浏览器已关闭", flush=True)
        else:
            print("[Worker] 浏览器保持打开状态", flush=True)
            # 等待用户按键后关闭
            input("[Worker] 按回车键关闭浏览器...")
            browser.close()
            browser = None

except Exception as e:
    print(f"[Worker] 抓取失败: {e}", flush=True)
    import traceback

    print(f"[Worker] 错误详情: {traceback.format_exc()}", flush=True)
    # 出错时确保关闭浏览器
    if browser:
        browser.close()

# 返回本轮发现的所有链接
return [{"link": link, "source": "unknown"} for link in 本轮_links_found]

# ---------------- CLI 调用 ----------------
if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "login":
        launch_browser_for_login()
    elif cmd == "save_login":
        attach_and_save_login()
    elif cmd == "search":
        keyword = sys.argv[2]
        # 检查是否有keep_browser_open参数
        keep_open = len(sys.argv) > 3 and sys.argv[3] == "--keep-open"
        results = search_keyword(keyword, keep_browser_open=keep_open)
        print(json.dumps(results, ensure_ascii=False), flush=True)
