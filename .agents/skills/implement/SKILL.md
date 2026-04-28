---
name: implement
description: Implement the full-stack AI chatbot using HTML frontend, FastAPI backend, and SQLite database
---

# /implement

你的任務是直接實作本專案程式碼。

## 技術要求（必須遵守）
- 前端：HTML + CSS + JavaScript
- 後端：FastAPI
- 資料庫：SQLite
- 模板：Jinja2 templates
- 檔案上傳：儲存在本地 `uploads/`
- LLM：Gemini API
- 專案進入點：`app.py`

## 必做功能
1. 多聊天室 session 管理
2. 訊息資料結構包含：
   - role
   - content
   - timestamp
3. 可查看並切換歷史對話
4. 可上傳圖片或文件並作為對話內容的一部分
5. 可重新生成 assistant 回答
6. 可中止回應
7. 可儲存使用者偏好（記憶機制）
8. 至少整合一個外部 API/tool
9. 首頁可直接操作聊天功能

## 介面需求
- 左側：session 歷史列表
- 右側：聊天視窗
- 可建立新對話
- 可顯示訊息時間
- 有上傳按鈕
- 有 regenerate 按鈕
- 有 stop 按鈕
- 有簡單但整潔的樣式

## 後端建議 API
- `GET /`
- `GET /api/sessions`
- `POST /api/sessions`
- `GET /api/sessions/{session_id}/messages`
- `POST /api/chat`
- `POST /api/upload`
- `POST /api/messages/{message_id}/regenerate`
- `POST /api/stop`
- `GET /api/preferences`
- `POST /api/preferences`

## 實作原則
- 程式需可執行
- 避免過度複雜
- 優先完成作業需求
- 若 streaming 太複雜，可用輪詢或狀態旗標模擬 stop
- 資料庫可使用 sqlite3 或 SQLAlchemy，選一種即可
- 需提供 `requirements.txt`
- 需提供 `.env.example`
- 程式中不可硬編碼 API key

## 產出要求
請直接建立或修改至少以下檔案：
- `app.py`
- `templates/index.html`
- `static/app.js`
- `static/style.css`
- `requirements.txt`
- `.env.example`

必要時可自行新增輔助檔案，但不要偏離上述技術要求。
不要只給片段，請完成可運行版本。