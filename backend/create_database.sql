-- 创建数据库的SQL脚本
-- 请使用以下方式执行：

-- 方式1: 使用psql连接默认postgres数据库
-- psql -U sql -h localhost -p 5432 postgres -f create_database.sql

-- 方式2: 直接执行
-- psql -U sql -h localhost -p 5432 postgres -c "CREATE DATABASE kids_english;"

-- 方式3: 使用超级用户postgres（如果有权限）
-- psql -U postgres -h localhost -p 5432 -c "CREATE DATABASE kids_english OWNER sql;"

-- 如果上述方法都不行，请手动创建数据库，然后运行：
-- uv run python init_db.py

-- 以下是创建数据库的命令
CREATE DATABASE kids_english;
