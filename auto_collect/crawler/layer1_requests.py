import requests
import re
from bs4 import BeautifulSoup

TG_LINK_RE = re.compile(r"(https?://t\.me/[A-Za-z0-9_/?=-]+)", re.I)

def extract_tg_links_from_text(text: str):
    return list(set(m.group(0) for m in TG_LINK_RE.finditer(text)))

def search_mobile(keyword: str, max_pages: int = 1, proxy: dict = None, log_callback=None):
    if log_callback:
        log_callback(f"[Layer1] 开始抓取 mobile.twitter.com")
    results = []
    session = requests.Session()
    if proxy:
        session.proxies.update(proxy)

    for page in range(max_pages):
        q = requests.utils.quote(keyword)
        url = f"https://mobile.twitter.com/search?q={q}&src=typed_query&f=live"
        try:
            resp = session.get(url, timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15"
            })
            if resp.status_code != 200:
                if log_callback:
                    log_callback(f"[Layer1] 请求失败: {resp.status_code}")
                continue
            text = BeautifulSoup(resp.text, "html.parser").get_text(" ", strip=True)
            links = extract_tg_links_from_text(text)
            for link in links:
                results.append({"source": url, "link": link})
            if log_callback:
                log_callback(f"[Layer1] 本页抓取到 {len(links)} 条 t.me 链接")
        except Exception as e:
            if log_callback:
                log_callback(f"[Layer1] 请求出错: {e}")
    return results