# PRD - AI Chatbot

## Product Overview

一個以 FastAPI + HTML + SQLite 建構的 AI 聊天機器人，支援多聊天室、歷史紀錄、檔案上傳、使用者偏好記憶與外部工具整合。

## Goals

- 建立可操作的聊天機器人
- 支援多 session 對話管理
- 儲存對話與偏好資料
- 展示 AI 輔助開發流程與 skill 設計能力

## Non-Goals

- 不追求正式商用等級部署
- 不實作複雜權限系統
- 不做高併發架構

## Target Users

- 課程助教與教師
- 開發者/學生

## Core Features

- 多聊天室
- 歷史訊息
- 檔案上傳
- regenerate / stop
- preference memory
- tool integration

## User Stories

- 作為使用者，我可以建立新聊天並保留歷史內容
- 作為使用者，我可以上傳文件輔助提問
- 作為使用者，我可以重新生成回答
- 作為使用者，我希望 AI 記住我的偏好
