# ARCHITECTURE - AI Chatbot

## Architecture Overview
本系統採用單體式 Web 應用架構，前端使用 HTML + CSS + JavaScript，後端使用 FastAPI 提供頁面與 API，資料以 SQLite 持久化儲存。檔案上傳採本地目錄保存，AI 回答由 Gemini API 提供，並透過 World Time API 作為外部工具整合示範。

## Tech Stack
- Frontend: HTML, CSS, JavaScript
- Backend: FastAPI
- Template Engine: Jinja2Templates
- Database: SQLite
- File Storage: local `uploads/`
- AI Model Provider: Gemini API
- External Tool API: World Time API
- Environment Management: python-dotenv

## Component Diagram
### Frontend
- `templates/index.html`
- `static/style.css`
- `static/app.js`

### Backend
- `app.py`
  - 頁面路由
  - Session API
  - Message API
  - Upload API
  - Preference API
  - Chat orchestration
  - Tool integration
  - SQLite access

### Storage
- SQLite:
  - chat_sessions
  - messages
  - uploaded_files
  - user_preferences
- Local folder:
  - uploads/

### External Services
- Gemini API
- World Time API

## Request Flow
### 1. 開啟首頁
1. Browser 請求 `GET /`
2. FastAPI 回傳 `index.html`
3. 前端載入後請求 sessions 與 preferences API

### 2. 建立新聊天
1. 前端送出 `POST /api/sessions`
2. 後端建立 chat_sessions 資料
3. 前端更新左側 session 列表並切換到新 session

### 3. 送出聊天訊息
1. 使用者在前端輸入訊息
2. 若有附件，先呼叫 `POST /api/upload`
3. 前端呼叫 `POST /api/chat`
4. 後端：
   - 儲存 user message
   - 讀取 session 歷史
   - 讀取 user preferences
   - 檢查是否需要呼叫外部工具
   - 組合 prompt
   - 呼叫 Gemini API
   - 儲存 assistant message
   - 回傳結果
5. 前端顯示 assistant 回答並刷新歷史訊息

### 4. 重新生成回答
1. 前端對某則 assistant 訊息呼叫 `POST /api/messages/{message_id}/regenerate`
2. 後端取得該訊息之前最近的 user 訊息與對話上下文
3. 重新呼叫 Gemini API 產生新回答
4. 寫入新 assistant message，保留 `regenerated_from_id`

### 5. 中止回應
1. 前端按下 stop 呼叫 `POST /api/stop`
2. 後端將指定 session 的 stop flag 設為 true
3. chat 流程在呼叫前或後檢查 flag，回傳 stopped 結果

## Data Storage Design
### chat_sessions
儲存每個聊天室的基本資訊：
- id
- title
- created_at
- updated_at

### messages
儲存對話內容：
- session_id
- role
- content
- timestamp
- status
- attachment_id
- regenerated_from_id

### uploaded_files
儲存使用者上傳檔案資訊與儲存路徑。

### user_preferences
以 key-value 方式記錄跨對話偏好，例如：
- name
- language
- tone

## API Endpoints
- `GET /`
- `GET /api/sessions`
- `POST /api/sessions`
- `GET /api/sessions/{session_id}/messages`
- `POST /api/upload`
- `POST /api/chat`
- `POST /api/messages/{message_id}/regenerate`
- `POST /api/stop`
- `GET /api/preferences`
- `POST /api/preferences`

## File Upload Design
- 前端使用 multipart/form-data 上傳檔案。
- 後端檢查檔名並產生唯一檔名存入 `uploads/`。
- 在 uploaded_files 表保存原始名稱、實際路徑與 MIME type。
- 聊天訊息可帶入 attachment_id，讓後端知道該訊息與哪個檔案有關。

## Memory Design
- 使用 `user_preferences` 資料表儲存偏好。
- 每次聊天前，系統讀取所有 preference 並轉成 system context。
- 範例：
  - name: Allen
  - language: zh-TW
  - tone: concise
- 這些偏好不依附單一 session，因此可跨對話持續生效。

## Regenerate / Stop Design
### Regenerate
- 對指定 assistant message 進行重新生成。
- 後端會尋找該訊息前一則 user message 與當前 session 上下文。
- 新生成訊息作為新紀錄寫入 messages 表。

### Stop
- 系統以記憶體中的 `stop_flags` 字典保存 session 的 stop 狀態。
- 此機制不是 token 級別串流中斷，而是簡化版流程控制。
- 適合課堂作業展示，不適合高併發正式環境。

## Error Handling
- API key 缺失時回傳友善錯誤訊息。
- 空訊息送出時回傳 400。
- session 不存在時回傳 404。
- 外部工具 API 失敗時回傳 fallback 內容。
- Gemini API 呼叫失敗時，assistant 訊息狀態標記為 error。

## Security Considerations
- API key 透過 `.env` 管理，不寫死在程式碼中。
- 上傳檔案檔名會重新命名，降低覆蓋風險。
- 本專案未做登入與權限驗證，故僅適合本機或教學環境。
- 未加入嚴格檔案格式驗證與防毒掃描，不適合生產環境。

## Scalability / Future Work
- 可改用 SQLAlchemy 管理模型與 migration。
- 可加入使用者系統與登入認證。
- 可改為 WebSocket / SSE 實作真正 streaming 與 stop。
- 可將檔案儲存改到雲端物件儲存。
- 可加入更多工具，例如天氣、搜尋、摘要與 OCR。
