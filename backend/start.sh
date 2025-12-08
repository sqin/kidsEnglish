#!/bin/bash

# 启动后端开发服务器

# 检查uv是否安装
if ! command -v uv &> /dev/null; then
    echo "错误: 未找到uv。请先安装uv: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

# 启动开发服务器
uv run uvicorn app.main:app --host 0.0.0.0 --port 20000 --reload
