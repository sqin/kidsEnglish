#!/bin/bash

# 启动后端服务器

# 检查uv是否安装
if ! command -v uv &> /dev/null; then
    echo "错误: 未找到uv。请先安装uv: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

# 生产环境：始终使用 HTTP（Nginx 处理 HTTPS）
# 开发环境：如果需要 HTTPS，可以通过 Vite 代理处理
echo "启动 HTTP 服务器（端口 20000）..."
uv run uvicorn app.main:app --host 0.0.0.0 --port 20000 --reload
