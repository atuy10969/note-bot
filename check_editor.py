import time, subprocess, os
from playwright.sync_api import sync_playwright

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DEBUG_PROFILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chrome_debug_profile")

proc = subprocess.Popen([CHROME_PATH, "--remote-debugging-port=9222",
    f"--user-data-dir={DEBUG_PROFILE}", "--no-first-run", "about:blank"])
time.sleep(3)

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    context = browser.contexts[0]
    page = context.new_page()

    page.goto("https://note.com", wait_until="networkidle")
    time.sleep(3)

    # 右上の「投稿」ボタンをクリック
    page.locator('button:has-text("投稿")').first.click()
    time.sleep(2)
    page.screenshot(path="after_click.png")
    print(f"クリック後URL: {page.url}")

    # ドロップダウンが出た場合「テキスト」を選択
    text_options = page.locator('a:has-text("テキスト"), button:has-text("テキスト"), li:has-text("テキスト")').all()
    print(f"テキスト選択肢: {len(text_options)}個")
    if text_options:
        text_options[0].click()
        time.sleep(3)

    page.screenshot(path="editor_page.png")
    print(f"最終URL: {page.url}")

    # 入力要素を確認
    elems = page.evaluate("""() => {
        const result = [];
        document.querySelectorAll('[contenteditable],[placeholder]').forEach(el => {
            result.push({
                tag: el.tagName,
                placeholder: el.placeholder || el.getAttribute('data-placeholder') || '',
                contenteditable: el.contentEditable,
            });
        });
        return result;
    }""")
    print(f"入力要素: {len(elems)}個")
    for e in elems:
        print(f"  {e}")

    browser.close()
proc.terminate()
