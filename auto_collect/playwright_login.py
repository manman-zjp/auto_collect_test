# auto_collect/playwright_login.py
from playwright.sync_api import sync_playwright

def save_login_state():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # 打开可见浏览器
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://x.com/login")
        print("请在打开的浏览器里手动登录你的 X(Twitter) 账号...")
        page.wait_for_timeout(30000)  # 给 30 秒时间手动登录
        context.storage_state(path="storage_state.json")
        print("✅ 登录状态已保存到 storage_state.json")
        browser.close()

if __name__ == "__main__":
    save_login_state()