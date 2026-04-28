---
name: models
description: Generate the data model documentation for the AI chatbot system
---

# /models

你的任務是產出 `docs/MODELS.md`，描述本專案的資料模型。

## 必須涵蓋的資料實體
1. UserPreference
2. ChatSession
3. Message
4. UploadedFile

## 每個模型至少描述
- purpose
- fields
- field type
- constraints
- relationships

## 必須包含的欄位建議
### UserPreference
- id
- key
- value
- created_at
- updated_at

### ChatSession
- id
- title
- created_at
- updated_at

### Message
- id
- session_id
- role
- content
- timestamp
- status
- attachment_id（可為空）
- regenerated_from_id（可為空）

### UploadedFile
- id
- session_id
- original_name
- stored_path
- mime_type
- uploaded_at

## 補充要求
- 說明 role 的可用值（例如 user / assistant / system / tool）
- 說明 status 的可用值（例如 completed / streaming / stopped / error）
- 說明資料表之間的關聯
- 補充索引建議與 SQLite 注意事項

## 輸出要求
- 直接建立或覆蓋 `docs/MODELS.md`
- 使用 Markdown 表格呈現欄位
- 不要輸出多餘說明