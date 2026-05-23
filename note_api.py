"""
note.com 内部APIを使った記事投稿モジュール（ブラウザ不要）
note_session.json（Playwright storage state）からクッキーを読み込んで使用する
"""
import json
import os
import requests

SESSION_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "note_session.json")

NOTE_API_BASE = "https://note.com/api/v1"


def _load_cookies() -> dict:
    """note_session.json からクッキーをrequests用の辞書で返す"""
    if not os.path.exists(SESSION_FILE):
        raise FileNotFoundError(
            f"セッションファイルが見つかりません: {SESSION_FILE}\n"
            "ローカルPCで save_session.py を実行してセッションを保存してください。"
        )
    with open(SESSION_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)

    cookies = {}
    for c in state.get("cookies", []):
        if "note.com" in c.get("domain", ""):
            cookies[c["name"]] = c["value"]
    return cookies


def _get_csrf_token(session: requests.Session) -> str:
    """トップページからCSRFトークンを取得する"""
    resp = session.get("https://note.com", timeout=10)
    # Cookieにxsrf-tokenがあればそれを使う
    xsrf = session.cookies.get("XSRF-TOKEN") or session.cookies.get("xsrf-token")
    if xsrf:
        return xsrf
    # metaタグから取得を試みる
    import re
    match = re.search(r'<meta name="csrf-token" content="([^"]+)"', resp.text)
    if match:
        return match.group(1)
    return ""


def post_draft(title: str, body: str) -> bool:
    """記事を下書き保存する。成功したらTrue、失敗したらFalseを返す"""
    try:
        cookies = _load_cookies()
    except FileNotFoundError as e:
        print(f"[note_api] エラー: {e}")
        return False

    session = requests.Session()
    session.cookies.update(cookies)
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://note.com/",
        "Origin": "https://note.com",
    })

    csrf = _get_csrf_token(session)
    if csrf:
        session.headers["X-XSRF-TOKEN"] = csrf

    payload = {
        "name": title,
        "body": body,
        "status": "draft",
    }

    try:
        resp = session.post(
            f"{NOTE_API_BASE}/text_notes",
            json=payload,
            timeout=15,
        )

        if resp.status_code in (200, 201):
            data = resp.json()
            note_key = data.get("data", {}).get("key") or data.get("key", "")
            print(f"[note_api] 下書き保存成功！ https://note.com/notes/{note_key}")
            return True

        # 401 → セッション切れ
        if resp.status_code == 401:
            print("[note_api] セッション切れです。ローカルPCで save_session.py を再実行してください。")
            return False

        print(f"[note_api] APIエラー: HTTP {resp.status_code}")
        print(f"[note_api] レスポンス: {resp.text[:300]}")
        return False

    except requests.RequestException as e:
        print(f"[note_api] 通信エラー: {e}")
        return False


if __name__ == "__main__":
    print("=== note API 動作テスト ===")
    result = post_draft(
        "【テスト】API経由の下書き保存テスト",
        "これはAPIテスト用の投稿です。自動で削除してください。"
    )
    print("結果:", "成功" if result else "失敗")
