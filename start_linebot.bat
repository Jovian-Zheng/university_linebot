@echo off
chcp 65001 >nul
echo ===============================================
echo   東吳大學 LINE Bot 啟動工具（真實 LINE 版）
echo ===============================================
echo.
echo 請確認你已經在 .env 裡填好下面三個：
echo   LINE_CHANNEL_ACCESS_TOKEN
echo   LINE_CHANNEL_SECRET
echo   HUGGINGFACE_API_TOKEN
echo.
pause

echo.
echo [1/2] 啟動 Flask webhook 伺服器...
start "東吳大學 LINE Bot" cmd /k "cd /d %~dp0 && python app.py"

timeout /t 3 >nul

echo.
echo [2/2] 請在「另一個」視窗手動執行下面其中一種 tunnel：
echo.
echo   === 推薦：cloudflared（不用 ngrok） ===
echo   cloudflared tunnel --url http://localhost:5000
echo.
echo   複製 cloudflared 給你的 https://... 網址
echo   然後在 LINE Console 設定成：
echo   https://你的網址/webhook
echo.
echo 伺服器已經在背景啟動，按任意鍵關閉這個視窗...
pause >nul
