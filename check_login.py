from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    )
    page = browser.new_page()
    page.goto("https://note.com/login", wait_until="domcontentloaded")
    time.sleep(4)
    page.screenshot(path="login_page.png")

    elems = page.locator("a, button").all()
    print("ボタン/リンク一覧:")
    for el in elems[:25]:
        try:
            txt = el.inner_text().strip()
            if txt:
                print(f"  - [{el.evaluate('e => e.tagName')}] {txt}")
        except Exception:
            pass

    browser.close()
    print("スクリーンショット: login_page.png")
