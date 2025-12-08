#!/usr/bin/env python3
"""
数据库初始化脚本

功能：
1. 创建kids_english数据库（如果不存在）
2. 创建所有数据表
3. 验证数据库连接

使用方法：
python init_db.py
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from app.db.database import Base
from app.models.models import User, Progress, Checkin, Achievement
from app.config import get_settings


def create_database():
    """创建数据库（如果不存在）"""
    settings = get_settings()

    # 从DATABASE_URL提取连接信息
    db_url = settings.database_url
    # postgresql://sql:123456@localhost:5432/kids_english
    # 提取为: postgresql://sql:123456@localhost:5432
    base_url = '/'.join(db_url.split('/')[:-1])
    db_name = db_url.split('/')[-1]

    print(f"正在创建数据库: {db_name}")

    # 使用psycopg2直接创建数据库
    try:
        # 连接到postgres数据库
        conn = psycopg2.connect(
            base_url + '/postgres',
            user='sql',
            password='123456'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # 检查数据库是否存在
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (db_name,)
        )

        if not cursor.fetchone():
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            print(f"✅ 数据库 {db_name} 创建成功")
        else:
            print(f"ℹ️ 数据库 {db_name} 已存在")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"⚠️ 创建数据库时出错: {e}")
        print("  请手动创建数据库或使用其他方式")


def create_tables():
    """创建所有数据表"""
    settings = get_settings()

    print("\n正在创建数据表...")
    engine = create_engine(settings.database_url)

    # 创建所有表
    Base.metadata.create_all(bind=engine)

    print("✅ 数据表创建成功")

    # 验证表
    with engine.connect() as conn:
        tables = [
            'users', 'progress', 'checkins', 'achievements'
        ]

        print("\n验证数据表:")
        for table in tables:
            result = conn.execute(text(
                f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = :table"
            ), {"table": table})

            if result.fetchone()[0]:
                print(f"  ✅ {table}")
            else:
                print(f"  ❌ {table} (未找到)")


def test_connection():
    """测试数据库连接"""
    settings = get_settings()

    print("\n测试数据库连接...")
    try:
        engine = create_engine(settings.database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
            print("✅ 数据库连接成功")
            return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("儿童英语学习应用 - 数据库初始化")
    print("=" * 60)

    # 先创建数据库（连接到postgres数据库）
    try:
        create_database()
    except Exception as e:
        print(f"⚠️ 创建数据库时出错: {e}")
        print("  可能需要管理员权限或数据库已存在")

    # 等待一秒让数据库创建完成
    import time
    time.sleep(1)

    # 测试连接
    if not test_connection():
        print("\n❌ 无法连接到数据库，请检查:")
        print("  1. PostgreSQL服务是否运行")
        print("  2. .env文件中的DATABASE_URL是否正确")
        print("  3. 用户名和密码是否正确")
        sys.exit(1)

    # 创建表
    try:
        create_tables()
    except Exception as e:
        print(f"❌ 创建数据表时出错: {e}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("✅ 数据库初始化完成！")
    print("=" * 60)
    print("\n现在可以启动后端服务了:")
    print("  ./start.sh")
    print("  或")
    print("  uv run uvicorn app.main:app --host 0.0.0.0 --port 20000 --reload")


if __name__ == "__main__":
    main()
