# MODELS - AI Chatbot

## 1. UserPreference

**Purpose**  
儲存跨對話持續存在的使用者偏好，例如姓名、語言、回覆風格。

| Field      | Type    | Constraints               | Description                             |
| ---------- | ------- | ------------------------- | --------------------------------------- |
| id         | INTEGER | PRIMARY KEY AUTOINCREMENT | 主鍵                                    |
| key        | TEXT    | NOT NULL, UNIQUE          | 偏好鍵，例如 `name`, `language`, `tone` |
| value      | TEXT    | NOT NULL                  | 偏好值                                  |
| created_at | TEXT    | NOT NULL                  | 建立時間                                |
| updated_at | TEXT    | NOT NULL                  | 更新時間                                |

**Relationships**
- 無直接外鍵，作為全域偏好資料使用。

---

## 2. ChatSession

**Purpose**  
儲存每個聊天室的基本資訊，用於多 session 對話切換與歷史管理。

| Field      | Type    | Constraints               | Description  |
| ---------- | ------- | ------------------------- | ------------ |
| id         | INTEGER | PRIMARY KEY AUTOINCREMENT | 主鍵         |
| title      | TEXT    | NOT NULL                  | 聊天室標題   |
| created_at | TEXT    | NOT NULL                  | 建立時間     |
| updated_at | TEXT    | NOT NULL                  | 最後更新時間 |

**Relationships**
- 一個 ChatSession 對多個 Message
- 一個 ChatSession 對多個 UploadedFile

---

## 3. Message

**Purpose**  
儲存對話中的每一則訊息，包括 user、assistant、system 與 tool。

| Field               | Type    | Constraints                  | Description                         |
| ------------------- | ------- | ---------------------------- | ----------------------------------- |
| id                  | INTEGER | PRIMARY KEY AUTOINCREMENT    | 主鍵                                |
| session_id          | INTEGER | NOT NULL, FOREIGN KEY        | 所屬聊天室                          |
| role                | TEXT    | NOT NULL                     | 訊息角色                            |
| content             | TEXT    | NOT NULL                     | 訊息內容                            |
| timestamp           | TEXT    | NOT NULL                     | 訊息時間                            |
| status              | TEXT    | NOT NULL DEFAULT 'completed' | 訊息狀態                            |
| attachment_id       | INTEGER | NULL, FOREIGN KEY            | 對應上傳檔案                        |
| regenerated_from_id | INTEGER | NULL, FOREIGN KEY            | 若為重新生成，指向原 assistant 訊息 |

**Relationships**
- 多個 Message 屬於一個 ChatSession
- Message 可選擇關聯一個 UploadedFile
- Message 可自我關聯 `regenerated_from_id`

**Allowed values for `role`**
- `user`
- `assistant`
- `system`
- `tool`

**Allowed values for `status`**
- `completed`
- `streaming`
- `stopped`
- `error`

---

## 4. UploadedFile

**Purpose**  
儲存使用者上傳的圖片或文件資料，讓聊天系統可在訊息中引用檔案資訊。

| Field         | Type    | Constraints               | Description    |
| ------------- | ------- | ------------------------- | -------------- |
| id            | INTEGER | PRIMARY KEY AUTOINCREMENT | 主鍵           |
| session_id    | INTEGER | NOT NULL, FOREIGN KEY     | 所屬聊天室     |
| original_name | TEXT    | NOT NULL                  | 原始檔名       |
| stored_path   | TEXT    | NOT NULL                  | 實際儲存路徑   |
| mime_type     | TEXT    | NULL                      | 檔案 MIME type |
| uploaded_at   | TEXT    | NOT NULL                  | 上傳時間       |

**Relationships**
- 多個 UploadedFile 屬於一個 ChatSession
- UploadedFile 可被 Message 透過 `attachment_id` 關聯

---

## Table Relationships Summary
- `chat_sessions (1) -> (N) messages`
- `chat_sessions (1) -> (N) uploaded_files`
- `uploaded_files (1) -> (N) messages`（邏輯上可被引用，多數情況一則訊息對一個附件）
- `messages (1) -> (N) messages` via `regenerated_from_id`

---

## Index Suggestions
建議為以下欄位建立索引：
- `messages.session_id`
- `messages.timestamp`
- `uploaded_files.session_id`
- `chat_sessions.updated_at`
- `user_preferences.key`

這能改善：
- session 歷史載入
- 訊息排序
- 偏好查詢
- 檔案列表查詢

---

## SQLite Notes
- SQLite 適合本機與小型課堂專案。
- 時間欄位使用 ISO 8601 字串，方便排序與顯示。
- 使用外鍵時需注意 SQLite 的 foreign key pragma。
- 若未來資料量增加，可改用 PostgreSQL。