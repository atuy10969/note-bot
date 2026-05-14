"""
Chromeをデバッグモードで起動してnote.comにログインし、セッションを自動保存します。
ログインが検知されると自動でセッションを保存して終了します。
"""
import subprocess
import time
import os
from playwright.sync_api import sync_playwright

SESSION_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "note_session.json")
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DEBUG_PROFILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chrome_debug_profile")

def save_session():
    print("=" * 50)
    print("note.com セッション保存ツール")
    print("=" * 50)
    print("\nChromeが開きます。note.comにログインしてください。")
    print("ログインが完了すると自動でセッションが保存されます。\n")

    proc = subprocess.Popen([
        CHROME_PATH,
        "--remote-debugging-port=9222",
        f"--user-data-dir={DEBUG_PROFILE}",
        "--no-first-run",
        "--no-default-browser-check",
        "https://note.com/login"
    ])
    time.sleep(4)

    print("ログイン待機中... (note.comにログインしてください)")

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
        except Exception as e:
            print(f"Chrome接続エラー: {e}")
            proc.terminate()
            return

        # ログイン完了を自動検知（最大5分待機）
        for i in range(60):
            try:
                contexts = browser.contexts
                if contexts:
                    pages = contexts[0].pages
                    for page in pages:
                        url = page.url
                        # note.comのトップやダッシュボードに遷移したらログイン成功
                        if "note.com" in url and "login" not in url and url != "https://note.com/":
                            print(f"\nログイン検知: {url}")
                            print("セッションを保存中...")
                            contexts[0].storage_state(path=SESSION_FILE)
                            print(f"完了！セッションを保存しました。")
                            browser.close()
                            proc.terminate()
                            return
                        elif url == "https://note.com/" or url == "https://note.com":
                            # トップページもログイン済みの可能性
                            pages_count = len(pages)
                            if pages_count > 0:
                                print(f"\nnote.comトップページを検知...")
                                print("セッションを保存中...")
                                contexts[0].storage_state(path=SESSION_FILE)
                                print(f"完了！セッションを保存しました。")
                                browser.close()
                                proc.terminate()
                                return
            except Exception:
                pass

            print(f"  待機中... {(i+1)*5}秒経過 (最大300秒)", end="\r")
            time.sleep(5)

        print("\nタイムアウト。再度実行してください。")
        browser.close()
        proc.terminate()

if __name__ == "__main__":
    save_session()
