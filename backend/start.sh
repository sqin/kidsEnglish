#!/bin/bash

# 启动后端开发服务器

# 检查uv是否安装
if ! command -v uv &> /dev/null; then
    echo "错误: 未找到uv。请先安装uv: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

# 启动开发服务器（自动检测SSL证书）
if [ -f "../frontend/ssl/server.key" ] && [ -f "../frontend/ssl/server.crt" ]; then
    echo "检测到SSL证书，启动HTTPS服务器..."
    uv run python -m uvicorn app.main:app --host 0.0.0.0 --port 20000 --reload --ssl-keyfile ../frontend/ssl/server.key --ssl-certfile ../frontend/ssl/server.crt
else
    echo "未检测到SSL证书，启动HTTP服务器..."
    uv run uvicorn app.main:app --host 0.0.0.0 --port 20000 --reload
fi
