import time
import os
import sys
import subprocess
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DEBUG_PROFILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chrome_debug_profile")
SESSION_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "note_session.json")


def _is_windows() -> bool:
    return sys.platform == "win32"


def post_to_note(title, body, publish=True):
    # クラウド環境（非Windows）またはnote_session.jsonがある場合はAPI方式を使う
    if not _is_windows() or os.path.exists(SESSION_FILE):
        from note_api import post_draft
        if publish:
            # API方式では現時点で下書き保存のみ対応（公開は手動）
            print("[note_poster] API方式: 下書き保存で実行します")
        return post_draft(title, body)

    # Windows + CDPモード（ローカルPC用）
    proc = subprocess.Popen([
        CHROME_PATH,
        "--remote-debugging-port=9222",
        f"--user-data-dir={DEBUG_PROFILE}",
        "--no-first-run",
        "--no-default-browser-check",
        "--no-restore-last-session",
        "--restore-last-session=0",
        "about:blank"
    ])
    time.sleep(4)

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            page = context.new_page()

            # ホームページへ
            print("note.com にアクセス中...")
            page.goto("https://note.com", wait_until="networkidle")
            time.sleep(3)

            if "login" in page.url:
                raise Exception("セッション切れ。save_session.py を再実行してください。")
            print("ログイン済み確認")

            # 投稿ボタンをクリック前の既存タブURLを記録
            existing_urls = set(pg.url for pg in context.pages)

            # 「投稿」ボタンをクリック
            print("投稿ボタンをクリック中...")
            page.locator('a[href="/notes/new"]').first.click()
            time.sleep(6)

            # 新しく開いたeditor.note.comタブを探す（既存URLと異なるもの）
            editor_page = None
            for pg in context.pages:
                if "editor.note.com" in pg.url and "/edit/" in pg.url and pg.url not in existing_urls:
                    editor_page = pg
                    break

            # 新しいタブが見つからない場合は既存も含めて探す
            if not editor_page:
                for pg in context.pages:
                    if "editor.note.com" in pg.url and "/edit/" in pg.url:
                        editor_page = pg
                        break

            if editor_page:
                page = editor_page
            # editor.note.com にいない場合は現在のページを使う

            page.bring_to_front()
            page.wait_for_load_state("domcontentloaded")
            time.sleep(5)
            print(f"エディタURL: {page.url}")
            page.screenshot(path="debug_editor.png")
            print("エディタ画面スクリーンショット保存: debug_editor.png")

            # タイトル入力（複数セレクターを試す）
            print("タイトルを入力中...")
            title_selectors = [
                '[placeholder*="タイトル"]',
                '[data-placeholder*="タイトル"]',
                'h1[contenteditable]',
                '.title',
                'textarea',
            ]
            title_el = None
            for sel in title_selectors:
                try:
                    el = page.locator(sel).first
                    el.wait_for(timeout=3000, state="visible")
                    title_el = el
                    print(f"タイトル欄発見: {sel}")
                    break
                except Exception:
                    continue

            if not title_el:
                page.screenshot(path="debug_no_title.png")
                raise Exception("タイトル欄が見つかりません。debug_no_title.png を確認してください。")

            title_el.click()
            title_el.fill(title)
            time.sleep(1)

            # 本文入力
            print("本文を入力中...")
            body_selectors = [
                '.ProseMirror',
                '[contenteditable="true"]:not([placeholder*="タイトル"])',
                '[data-placeholder*="本文"]',
                '.editor__body',
            ]
            body_el = None
            for sel in body_selectors:
                try:
                    el = page.locator(sel).first
                    el.wait_for(timeout=3000, state="visible")
                    body_el = el
                    print(f"本文欄発見: {sel}")
                    break
                except Exception:
                    continue

            if not body_el:
                # タイトル欄からTabキーで移動
                title_el.press("Tab")
                time.sleep(0.5)
            else:
                body_el.click()
                time.sleep(0.5)

            for paragraph in body.split('\n'):
                if paragraph.strip():
                    page.keyboard.type(paragraph)
                page.keyboard.press("Enter")
            time.sleep(2)

            if publish:
                print("公開ボタンをクリック中...")
                pub_btn = page.locator('button:has-text("公開"), button:has-text("投稿する")').first
                pub_btn.click()
                time.sleep(2)
                try:
                    confirm = page.locator('button:has-text("公開する")').first
                    if confirm.is_visible(timeout=3000):
                        confirm.click()
                        time.sleep(3)
                except Exception:
                    pass
                page.wait_for_load_state("networkidle")
                print(f"投稿完了: {page.url}")
            else:
                # 下書き保存
                draft_btn = page.locator('button:has-text("下書き"), a:has-text("下書き")').first
                if draft_btn.is_visible(timeout=2000):
                    draft_btn.click()
                    time.sleep(2)
                print("下書き保存完了")

            time.sleep(2)
            return True

        except Exception as e:
            print(f"エラー: {e}")
            try:
                page.screenshot(path="error_screenshot.png")
                print("スクリーンショット保存: error_screenshot.png")
            except Exception:
                pass
            return False
        finally:
            try:
                browser.close()
            except Exception:
                pass
            proc.terminate()
            time.sleep(2)
            # Chrome残存プロセスを確実に終了
            import subprocess as sp
            sp.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True)
            time.sleep(3)

if __name__ == "__main__":
    result = post_to_note("【テスト】メンズ洗顔料おすすめ5選", "これはテスト投稿です。自動投稿の動作確認用です。", publish=False)
    print("結果:", "成功" if result else "失敗")
