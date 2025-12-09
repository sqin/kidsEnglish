import asyncio
import sys
from app.db.database import AsyncSessionLocal
from app.models.models import User
from app.routers.auth import get_password_hash, verify_password
from sqlalchemy import select

async def test_auth():
    print("开始测试认证系统...")
    async with AsyncSessionLocal() as db:
        username = "testuser"
        password = "password123"
        
        # 1. 清理旧数据
        print(f"正在清理用户 {username}...")
        result = await db.execute(select(User).where(User.nickname == username))
        user = result.scalar_one_or_none()
        if user:
            await db.delete(user)
            await db.commit()
            print("旧用户已删除")
            
        # 2. 注册
        print(f"正在注册用户 {username}...")
        hashed_password = get_password_hash(password)
        new_user = User(nickname=username, hashed_password=hashed_password)
        db.add(new_user)
        await db.commit()
        print("用户注册成功")
        
        # 3. 验证
        print("正在验证登录...")
        result = await db.execute(select(User).where(User.nickname == username))
        user = result.scalar_one_or_none()
        
        if not user:
            print("错误：无法从数据库找到刚注册的用户！")
            return
            
        print(f"找到用户: {user.nickname}")
        print(f"数据库中的哈希: {user.hashed_password}")
        
        if verify_password(password, user.hashed_password):
            print("SUCCESS: 密码验证通过！后端逻辑正常。")
        else:
            print("FAILURE: 密码验证失败！")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_auth())
