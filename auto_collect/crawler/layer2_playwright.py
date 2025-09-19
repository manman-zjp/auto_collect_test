import requests
import re

TG_LINK_RE = re.compile(r"(https?://t\.me/[A-Za-z0-9_/?=-]+)", re.I)

def extract_tg_links_from_text(text: str):
    return list(set(m.group(0) for m in TG_LINK_RE.finditer(text)))

def search_web(keyword: str, max_pages: int = 1, proxy: dict = None, log_callback=None):
    if log_callback:
        log_callback(f"[Layer2] 开始抓取 x.com Web 页面")
    results = []
    session = requests.Session()
    if proxy:
        session.proxies.update(proxy)

    for page in range(max_pages):
        q = requests.utils.quote(keyword)
        url = f"https://x.com/search?q={q}&f=live"
        try:
            resp = session.get(url, timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
            })
            if resp.status_code != 200:
                if log_callback:
                    log_callback(f"[Layer2] 请求失败: {resp.status_code}")
                continue
            text = resp.text
            links = extract_tg_links_from_text(text)
            for link in links:
                results.append({"source": url, "link": link})
            if log_callback:
                log_callback(f"[Layer2] 本页抓取到 {len(links)} 条 t.me 链接")
        except Exception as e:
            if log_callback:
                log_callback(f"[Layer2] 请求出错: {e}")
    return results