#!/usr/bin/env bash
set -euo pipefail

# 安装运行依赖（生产环境）
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt gunicorn

# 使用 gunicorn 启动 Flask（单进程，避免摄像头被多进程重复占用）
exec gunicorn --bind 0.0.0.0:8000 \
  --workers 1 \
  --threads 2 \
  --timeout 0 \
  server:app
