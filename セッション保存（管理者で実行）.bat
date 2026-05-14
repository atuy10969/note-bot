@echo off
echo 管理者権限でセッションを保存します...
cd /d C:\Users\11yut\note_bot
python save_session.py
if %errorlevel% neq 0 (
    echo.
    echo エラーが発生しました。
    pause
) else (
    echo.
    echo 完了しました！
    pause
)
