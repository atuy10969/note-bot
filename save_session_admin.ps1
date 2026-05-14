Set-Location "C:\Users\11yut\note_bot"
$env:PYTHONIOENCODING = "utf-8"
$result = python save_session.py 2>&1
$result | Out-File "C:\Users\11yut\note_bot\session_log.txt" -Encoding utf8
Write-Output "Done"
