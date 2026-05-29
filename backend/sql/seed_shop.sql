-- 解压商城初始数据
-- 使用方法: mysql -u root -p emotion_platform < backend/sql/seed_shop.sql

-- 商品分类
INSERT INTO product_categories (id, name, description, icon, sort_order) VALUES
(1, '解压玩具', '捏一捏，揉一揉，让压力从指尖溜走', 'toy', 1),
(2, '香薰好物', '用气味治愈心灵，给生活一点仪式感', 'aroma', 2),
(3, '解压服务', '专业陪伴，让紧绷的神经得到舒缓', 'service', 3),
(4, '身心好物', '从指尖到心间，给自己一份温柔的照料', 'wellness', 4);

-- 解压玩具
INSERT INTO products (id, category_id, name, description, price, original_price, image_url, stock, sales_count, product_type, is_on_sale, sort_order) VALUES
(1, 1, '慢回弹减压捏捏乐', '超大号慢回弹材质，手感软糯Q弹，捏下去慢慢回弹，烦躁时反复揉捏超解压。办公桌、床头必备。', 29.90, 39.90, '/static/products/p1.jpg', 999, 2340, 'physical', 1, 1),
(2, 1, '指尖无限魔方', '小巧便携，6面不同机关（按钮、摇杆、滚轮、开关、转盘、齿轮），开会焦虑时偷偷玩，停不下来。', 35.00, 45.00, '/static/products/p2.jpg', 500, 1820, 'physical', 1, 2),
(3, 1, '3D金属拼图·星月夜', '梵高星月夜主题金属拼图，激光切割精密零件，拼装过程极度专注忘我，成品可做桌面摆件。', 89.00, 119.00, '/static/products/p3.jpg', 300, 980, 'physical', 1, 3),
(4, 1, '毛绒暖手抱枕·卡皮巴拉', '可插手的大号卡皮巴拉毛绒抱枕，软fufu的触感，冬天暖手、趴桌小憩当枕头两用。', 59.00, 79.00, '/static/products/p4.jpg', 400, 1560, 'physical', 1, 4);

-- 香薰好物
INSERT INTO products (id, category_id, name, description, price, original_price, image_url, stock, sales_count, product_type, is_on_sale, sort_order) VALUES
(5, 2, '天然大豆蜡香薰蜡烛·雨后森林', '100%天然大豆蜡，雨后森林香型，燃烧时散发清新的松木与青草气息，仿佛置身雨后的山林。燃烧时长约40小时。', 68.00, 88.00, '/static/products/p5.jpg', 600, 1120, 'physical', 1, 1),
(6, 2, '超声波静音香薰机', '500ml大容量，超静音超声波雾化，7色呼吸灯，自动断电保护。睡前滴两滴薰衣草精油，一夜好眠。', 129.00, 169.00, '/static/products/p6.jpg', 350, 890, 'physical', 1, 2),
(7, 2, '减压精油滚珠·深呼吸', '10ml便携滚珠设计，含真正薰衣草、甜橙、佛手柑精油，涂在手腕和太阳穴，随时随地来一次深呼吸。', 49.00, 65.00, '/static/products/p7.jpg', 800, 2100, 'physical', 1, 3);

-- 解压服务
INSERT INTO products (id, category_id, name, description, price, original_price, image_url, stock, sales_count, product_type, is_on_sale, sort_order) VALUES
(8, 3, '正念冥想引导·21天入门', '专业冥想导师录制的21天系统课程，每天10-15分钟，从呼吸觉察到身体扫描，帮你建立正念习惯。附赠练习手册PDF。', 99.00, 199.00, '/static/products/p8.jpg', 9999, 3200, 'service', 1, 1),
(9, 3, '1v1 线上心理倾听·30分钟', '持证心理咨询师30分钟线上倾听陪伴，不评判不说教，你只需要把想说的都说出来。视频/语音/文字任选。', 150.00, 200.00, '/static/products/p9.jpg', 9999, 1560, 'service', 1, 2),
(10, 3, 'ASMR 助眠音频包·50首精选', '专业录制的50首高品质ASMR音频：雨声、海浪、翻书声、耳语触发音……配合降噪耳机效果更佳，睡不着的时候打开它。', 19.90, 29.90, '/static/products/p10.jpg', 9999, 5600, 'service', 1, 3),
(11, 3, '情绪书写疗愈课·7天训练营', '7天线上社群陪伴式书写训练，每天一个情绪主题引导写作。不需要文笔好，只需要对自己诚实。', 79.00, 129.00, '/static/products/p11.jpg', 9999, 2400, 'service', 1, 4);

-- 身心好物
INSERT INTO products (id, category_id, name, description, price, original_price, image_url, stock, sales_count, product_type, is_on_sale, sort_order) VALUES
(12, 4, '重力毯·深压触感助眠被', '6.8kg科学配重重力毯，模拟被拥抱的深压触感，促进血清素和褪黑素分泌。焦虑失眠者的福音。150×200cm。', 299.00, 399.00, '/static/products/p12.jpg', 200, 680, 'physical', 1, 1),
(13, 4, '成人涂色书·治愈花园', '50幅精美线稿，从花草到曼陀罗，每一页都是一次静心之旅。附赠12色彩铅。', 39.90, 49.90, '/static/products/p13.jpg', 450, 1890, 'physical', 1, 2),
(14, 4, '泡脚桶·恒温按摩足浴盆', '智能恒温加热、气泡按摩、红光理疗，睡前泡20分钟，从脚底暖到心里。折叠收纳不占地方。', 199.00, 259.00, '/static/products/p14.jpg', 280, 750, 'physical', 1, 3);
