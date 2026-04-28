---
name: architecture
description: Generate system architecture documentation for the AI chatbot project
---

# /architecture

你的任務是根據此專案需求產出 `docs/ARCHITECTURE.md`。

## 技術限制
- Frontend: HTML + CSS + JavaScript
- Backend: FastAPI
- Database: SQLite
- Template engine: Jinja2（可用 FastAPI templates）
- File storage: local uploads folder
- LLM provider: Gemini API
- 外部工具/API：至少整合一項，例如 weather API、time API、Wikipedia API 等

## 必須描述的內容
1. 系統總覽
2. 前後端架構
3. 資料流程
4. 主要模組
5. API 設計
6. 資料庫設計概念
7. 檔案上傳流程
8. 記憶機制設計
9. regenerate / stop response 的處理方式
10. 安全性與限制
11. 未來可擴充方向

## 文件格式要求
至少包含：
- Architecture Overview
- Tech Stack
- Component Diagram（文字描述即可）
- Request Flow
- Data Storage Design
- API Endpoints
- File Upload Design
- Memory Design
- Error Handling
- Security Considerations
- Scalability / Future Work

## 輸出要求
- 直接建立或覆蓋 `docs/ARCHITECTURE.md`
- 使用 Markdown
- 不要輸出程式碼，重點放在設計說明