---
name: test
description: Generate a manual test checklist for the AI chatbot project
---

# /test

你的任務是產出一份手動測試清單，內容請直接寫入 `docs/MANUAL_TEST_CHECKLIST.md`。

## 測試範圍
1. 首頁是否可開啟
2. 是否可建立新 session
3. 是否可切換歷史 session
4. 訊息是否正確顯示 role/content/timestamp
5. 是否可送出聊天訊息
6. 是否可得到 AI 回答
7. 是否可上傳圖片或文件
8. 上傳後是否有被記錄或顯示
9. 是否可重新生成回答
10. 是否可中止回應
11. 是否可儲存與讀取使用者偏好
12. 外部工具/API 是否真的有被呼叫
13. 重整頁面後資料是否仍存在
14. 錯誤情境是否有基本處理（API key 缺失、空訊息、錯誤檔案等）

## 格式要求
- 使用 checklist 格式
- 每個測試案例包含：
  - 測試項目
  - 前置條件
  - 操作步驟
  - 預期結果

## 輸出要求
- 直接建立或覆蓋 `docs/MANUAL_TEST_CHECKLIST.md`
- 使用 Markdown
- 不要輸出多餘解釋