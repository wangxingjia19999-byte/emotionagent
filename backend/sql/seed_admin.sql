-- 管理员账号种子数据（admins 表，与 users 表独立）
-- 密码: admin123 (bcrypt-sha256 哈希)
-- 使用方法: mysql -u root -p emotion_platform < backend/sql/seed_admin.sql

INSERT INTO admins (username, password_hash, nickname, role, status) VALUES
('admin', '$bcrypt-sha256$v=2,t=2b,r=12$RonE.HmCRfn1BXbKSMfMF.$qFnDQQN1lkQMiJskTJ3aWxoqQw/T2RK', '系统管理员', 'super_admin', 'active')
ON DUPLICATE KEY UPDATE username=username;
