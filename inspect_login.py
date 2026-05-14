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

    # 全inputフィールドの情報を取得
    inputs = page.locator("input").all()
    print(f"input要素数: {len(inputs)}")
    for i, inp in enumerate(inputs):
        try:
            visible = inp.is_visible()
            attrs = page.evaluate("""(el) => ({
                type: el.type,
                name: el.name,
                id: el.id,
                placeholder: el.placeholder,
                class: el.className.substring(0, 50)
            })""", inp.element_handle())
            print(f"  [{i}] visible={visible} type={attrs['type']} name={attrs['name']} placeholder={attrs['placeholder'][:40]}")
        except Exception as e:
            print(f"  [{i}] error: {e}")

    browser.close()
