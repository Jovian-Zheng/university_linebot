# 東吳大學 LINE Bot（Python 版）

專為東吳大學（外雙溪 / 城中校區）學生設計的實用 LINE Bot。

**⚠️ 作業重點**：本專案已準備好部署到 **Hugging Face Spaces**（Docker 方式），符合「架到 Hugging Face」的要求。LINE Bot webhook 會跑在 HF Space 提供的公開網址上，並使用 Hugging Face Inference API 處理智能回覆。

## 主要功能

- 📚 **查課表**：輸入「課表」看所有科系，或「課表 法律學系」「課表 中一Ａ」查特定課表（114-2 學期資料）
- 🍽️ **看餐廳**：輸入「餐廳」或「吃什麼」列出校園餐廳（餐憶食堂、據德食堂、蒲家廚房等），可加關鍵字搜尋
- 🚌 **看公車 / 交通**：輸入「公車」列出周邊常見路線（557、紅30、255、校車等），可查特定路線
- ❓ **幫助**：隨時輸入「幫助」顯示完整說明

附帶主選單快速回覆按鈕，操作超簡單。

## 為什麼改用 Python？

原 JS 版因為缺少 package.json + 依賴安裝問題 + 執行環境，容易一直失敗。Python 版本使用 Flask + 官方 line-bot-sdk，安裝簡單、相容性好，在 Windows / mac / Linux 都容易跑。

## 本地測試（開發時強烈建議先用這個）

完全不用公開網址、不用 LINE token，就能測試所有功能（含 Hugging Face AI）。

```powershell
cd C:\Users\AUSER\Desktop\university_linebot

pip install -r requirements.txt

# 你的 .env 已經有 token，直接執行即可
python local_chat.py
```

直接在終端機輸入：
- `課表`
- `課表 法律學系` 或 `課表 中一Ａ`
- `餐廳`
- `餐廳 咖啡`
- `公車`
- `公車 557`
- 任何自然語言問題（AI 會自動參考校園資料）

輸入 `exit` 或 `離開` 結束。

---

## 部署到 Hugging Face Spaces（作業要求）

**這是本專案為「架到 Hugging Face」作業要求準備的主要部署方式。**

你的 LINE Bot webhook 會跑在 Hugging Face Spaces 提供的公開網址上，並使用 Hugging Face Inference API（Mistral-7B）處理智能回覆。

**重要**：你的 `.env` 已經有內容，**千萬不要**把 `.env` 檔案上傳或 commit。我們會用 Hugging Face Space 的 Secrets 安全存放 token。

### 部署前準備

1. 確認你的 `.env` 裡有以下三個 key（如果缺少 `HUGGINGFACE_API_TOKEN` 請自行加上）：
   - `LINE_CHANNEL_ACCESS_TOKEN`
   - `LINE_CHANNEL_SECRET`
   - `HUGGINGFACE_API_TOKEN`

2. 執行下面指令查看你 .env 裡有哪些 key（只顯示名稱，不顯示值）：
   ```powershell
   cd C:\Users\AUSER\Desktop\university_linebot
   Get-Content .env | Select-String '^[A-Z_]+=' | ForEach-Object { $_.Line.Split('=')[0] }
   ```

3. 確保資料夾內有這些檔案（我們已準備好）：
   - `app.py`
   - `Dockerfile`
   - `requirements.txt`
   - `university_bot.db`
   - `.dockerignore`（會自動排除 .env）

### 完整部署步驟

1. **建立 GitHub Repo（強烈建議）**
   - 把這個資料夾 push 到一個新的 GitHub repository（記得 `.env` 已被 `.gitignore` 忽略，不會上傳）。

2. **在 Hugging Face 建立 Space**
   - 前往 https://huggingface.co/spaces
   - 點擊「Create new Space」
   - Space 名稱自己取（例如 `scu-linebot`）
   - **SDK** 選擇 **Docker**
   - 建立 Space

3. **連線 GitHub（或手動上傳）**
   - Space 建立後，進入 Settings → 「Repository」連線你的 GitHub repo（之後改程式碼會自動重新部署）。
   - 或直接在 Space 的 Files 頁面手動上傳必要檔案。

4. **設定 Secrets（最關鍵步驟）**
   - 前往 Space → **Settings → Variables and secrets**
   - 新增以下三個變數，把你本地 `.env` 裡的**實際值**貼上去：
     - `LINE_CHANNEL_ACCESS_TOKEN`
     - `LINE_CHANNEL_SECRET`
     - `HUGGINGFACE_API_TOKEN`
   - （可選）新增 `PORT=7860`

5. **等待建置完成**
   - HF 會自動根據 `Dockerfile` 建置（使用 gunicorn + port 7860）。
   - 建置成功後，你的公開網址格式為：
     `https://<你的用戶名>-<space名稱>.hf.space`

6. **設定 LINE Webhook**
   - 前往 [LINE Developers Console](https://developers.line.biz/)
   - 選擇你的 Messaging API Channel
   - **Webhook URL** 填入完整路徑：
     ```
     https://<你的用戶名>-<space名稱>.hf.space/webhook
     ```
   - 點擊 **Verify**，確認成功後儲存並啟用 Webhook。

7. **測試**
   - 把你的 LINE Bot 加為好友
   - 傳送「課表」「餐廳」「公車」「幫助」測試精準功能
   - 傳送其他問題測試 Hugging Face AI 回覆（會自動帶入校園資料）

### 注意事項

- **免費 Space 會 sleep**：長時間沒流量會進入睡眠狀態，webhook 暫時無法使用。作業展示前請先去 Space 頁面點擊「Restart」或訪問一次網址讓它醒來。
- 你的 `.env` 檔案永遠不會被上傳（已被 `.dockerignore` 和 `.gitignore` 保護）。
- Hugging Face 免費 Inference API 有 rate limit，回答偶爾會較慢，這是正常現象。我們已用背景執行緒處理，不會影響 LINE webhook 回應。

---

## Hugging Face 整合說明

- AI 部分使用 `mistralai/Mistral-7B-Instruct-v0.3` 透過 Hugging Face Inference API。
- 非精準指令（課表/餐廳/公車）時，會自動從資料庫抓取相關校園資料（系所、餐廳、公車）作為 context 給 AI，減少幻覺。
- 所有長時間處理（HF 呼叫）都放在背景執行緒，確保 webhook 能立即回 200 給 LINE。

---

## 專案結構

```
university_bot.db      # 課表 + 餐廳 + 公車資料（已內建）
app.py                 # 真實 LINE Bot webhook（Flask + gunicorn）
Dockerfile             # 用於 Hugging Face Spaces 部署
.dockerignore
requirements.txt
local_chat.py          # 本地測試模式（推薦開發時使用）
seed_data.py
.env.example
README.md
legacy-js/             # 舊 JS 檔案（已移除）
```

---

## 資料來源與注意事項

- 課表資料來自既有 university_bot.db（114-2 學期，約 3000+ 筆，含法律、英文、企管、日文、經濟等系）。實際最新課表請以學校官方系統為準：
  - https://web.sys.scu.edu.tw/class40.asp?option=1
- 餐廳、公車資料為人工整理的常見資訊，會隨實際營業狀況變動。
- 沒有個人化「我的課表」（需要登入學校系統），目前提供系所/班級查詢。

## 常見問題

**Q: 部署到 Hugging Face 後 webhook 沒反應？**
- 確認 Space 已經建置成功且沒有 sleep。
- 確認 Webhook URL 是 `https://...hf.space/webhook`（不是只有 domain）。
- 檢查 Space 的 Variables and secrets 是否正確填入三個 token。
- 免費 Space 可能需要先訪問 Space 頁面讓它醒來。

**Q: Hugging Face AI 回覆很慢或沒回？**
- 免費 Inference API 有時需要載入模型（第一次會比較慢）。
- 我們已使用背景執行緒處理，LINE 不會超時。
- 精準功能請直接用「課表」「餐廳」「公車」指令（走資料庫，最快最準）。

**Q: local_chat.py 跑起來但 AI 沒回覆？**
- 確認 `.env` 裡的 `HUGGINGFACE_API_TOKEN` 是否正確。
- 第一次呼叫 HF API 常需要載入模型，請多等幾秒再試。

**Q: 想讓更多問題都走 Hugging Face？**
- 目前是 hybrid 設計（精準指令走資料庫 + 其他走 AI）。
- 如果作業需要更「純 HF」，告訴我，我可以調整讓大多數訊息都預設走 AI + 校園資料 context。

**Q: 課表資料不完整？**
- 這是 114-2 學期的既有資料，實際請以學校官方課表系統為主：https://web.sys.scu.edu.tw/class40.asp?option=1

## 授權 / 貢獻

這個專案是給東吳大學同學實用的校園小工具。資料僅供參考，請愛惜使用。

有問題或想貢獻，隨時修改 code 再跑！

---

祝使用愉快！🎓🚌🍱
東吳大學生活小幫手
