-- 创建数据库
CREATE DATABASE IF NOT EXISTS emotion_platform
DEFAULT CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE emotion_platform;

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nickname VARCHAR(50),
    avatar VARCHAR(255) DEFAULT '',
    occupation VARCHAR(100),
    age INT,
    gender VARCHAR(20),
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 初始化管理员账号
-- 注意: 密码为加密后的哈希值
INSERT INTO users (
    username,
    email,
    password_hash,
    nickname,
    avatar,
    occupation,
    age,
    gender,
    role,
    status,
    created_at,
    updated_at
) VALUES
(
    'admin',
    'admin@emotion.com',
    '$bcrypt-sha256$v=2,t=2b,r=12$ydIK9Wq0q2BwL9zvbLLlIO$vCz1S8VbJO.TvTQQkJtK1NDHYGmPm4a',
    '管理员',
    '',
    '系统管理员',
    NULL,
    NULL,
    'admin',
    'active',
    NOW(),
    NOW()
),
(
    'superadmin',
    'superadmin@emotion.com',
    '$bcrypt-sha256$v=2,t=2b,r=12$j79FStk1kdTCKotgQXPdru$HyPvPR5Oi.SX2uOPew27QnTffZWiL/W',
    '系统管理员',
    '',
    '系统管理员',
    NULL,
    NULL,
    'super_admin',
    'active',
    NOW(),
    NOW()
);
