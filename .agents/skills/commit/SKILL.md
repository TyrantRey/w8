---
name: commit
description: Commit and push the current project changes using the default Antigravity git identity
---

# /commit

你的任務是將目前專案變更自動 commit 並 push。

## Git 要求

- 使用 Antigravity 預設 git user 與 email
- 先檢查 git status
- 將所有變更加入追蹤
- 產生清楚的 commit message
- push 到目前 branch

## Commit message 規則

採用簡潔格式，例如：

- `feat: add chatbot sessions and message history`
- `docs: add PRD, architecture, and models`
- `fix: resolve file upload and regenerate flow`

## 執行步驟

1. 檢查工作樹狀態
2. `git add .`
3. `git commit -m "<message>"`
4. `git push`

## 注意

- 若沒有變更則不要 commit
- 若 push 失敗，明確回報原因
- 不要修改程式內容，只做版本控制動作
