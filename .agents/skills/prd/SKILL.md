---
name: prd
description: Generate a concise Product Requirements Document for the AI chatbot project
---

# /prd

你的任務是為目前專案產出 `docs/PRD.md`。

## 專案背景

這是一個課堂作業專案，需要完成一個具備前後端的 AI 聊天機器人，並使用 Skill 引導開發。

## 必須包含的產品需求

1. 使用 HTML 前端
2. 使用 FastAPI 後端
3. 使用 SQLite 儲存資料
4. 支援多聊天室（session）
5. 訊息需包含：
   - role
   - content
   - timestamp
6. 可查看與切換歷史對話
7. 支援上傳圖片或文件
8. 支援重新生成回答
9. 支援中止回應
10. 支援跨對話的使用者偏好記憶
11. 至少整合一個外部工具/API
12. UI 需可用、可實際操作

## 文件格式要求

請產出一份結構清楚、精簡但完整的 PRD，至少包含：

- Product Overview
- Goals
- Non-Goals
- Target Users
- Core Features
- User Stories
- Functional Requirements
- Non-Functional Requirements
- Success Criteria
- Risks / Constraints

## 輸出要求

- 直接建立或覆蓋 `docs/PRD.md`
- 內容使用 Markdown
- 不要輸出多餘說明
