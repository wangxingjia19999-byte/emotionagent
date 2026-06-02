
-- ============================================================
-- 迁移: 新增 ai_chat_sessions 表 (AI 聊天会话记录)
-- 数据库: MySQL (utf8mb4)
-- 使用方法: mysql -u root -p emotion_platform < backend/sql/migrate_add_ai_chat_sessions.sql
-- ============================================================

USE emotion_platform;

CREATE TABLE IF NOT EXISTS ai_chat_sessions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    title VARCHAR(200) NOT NULL DEFAULT '',
    agent_used VARCHAR(50) NOT NULL DEFAULT 'emotion_companion',
    message_count INT NOT NULL DEFAULT 0,
    first_message TEXT,
    last_message TEXT,
    crisis_detected INT NOT NULL DEFAULT 0 COMMENT '是否触发危机检测: 0=否 1=是',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_ai_chat_sessions_user_id (user_id),
    INDEX idx_ai_chat_sessions_created_at (created_at),
    CONSTRAINT fk_ai_chat_sessions_user_id FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
