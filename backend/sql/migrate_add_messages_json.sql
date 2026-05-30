-- ============================================================
-- 迁移: ai_chat_sessions 表新增 messages_json 列
-- 使用方法: mysql -u root -p emotion_platform < backend/sql/migrate_add_messages_json.sql
-- ============================================================

USE emotion_platform;

ALTER TABLE ai_chat_sessions
ADD COLUMN IF NOT EXISTS messages_json TEXT COMMENT 'JSON 格式存储本轮对话';
