#!/bin/bash

# 数据库创建脚本
# 使用方法: ./create_db.sh

echo "正在创建数据库 kids_english..."

# 使用psql命令创建数据库
psql -U sql -h localhost -p 5432 -c "CREATE DATABASE kids_english;"

if [ $? -eq 0 ]; then
    echo "✅ 数据库创建成功！"
    echo ""
    echo "现在运行数据库初始化："
    echo "uv run python init_db.py"
else
    echo "❌ 数据库创建失败"
    echo ""
    echo "请检查:"
    echo "1. PostgreSQL服务是否运行"
    echo "2. 用户名和密码是否正确"
    echo "3. 是否有创建数据库的权限"
    echo ""
    echo "如果仍然失败，请手动执行以下命令："
    echo "psql -U sql -h localhost -p 5432 -c \"CREATE DATABASE kids_english;\""
fi
