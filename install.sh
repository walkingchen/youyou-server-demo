#!/bin/bash

# 树莓派摄像头教学系统 - 自动安装脚本
# 适用于 Raspberry Pi OS

set -e  # 遇到错误立即退出

echo "=================================="
echo "树莓派摄像头教学系统 - 安装向导"
echo "=================================="
echo ""

# 检查是否在树莓派上运行
if [ ! -f /proc/device-tree/model ]; then
    echo "警告：此脚本设计用于树莓派系统"
    read -p "是否继续？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "步骤 1/5: 更新系统包..."
sudo apt update

echo ""
echo "步骤 2/5: 安装系统依赖..."
echo "  - Python 3"
echo "  - picamera2（摄像头库）"
echo "  - numpy 和 Pillow（图像处理）"
sudo apt install -y python3-pip python3-picamera2 python3-numpy python3-pil

echo ""
echo "步骤 3/5: 检查摄像头支持..."
echo "  ℹ️  picamera2 适用于最新的 Raspberry Pi OS"
echo "  ℹ️  确保摄像头已在 raspi-config 中启用"

echo ""
echo "步骤 4/5: 安装 Flask..."
# 检查是否在虚拟环境中
if [ -z "$VIRTUAL_ENV" ]; then
    echo "  在系统 Python 中安装..."
    pip3 install -r requirements.txt --break-system-packages 2>/dev/null || pip3 install Flask --break-system-packages
else
    echo "  在虚拟环境中安装..."
    pip install -r requirements.txt
fi

echo ""
echo "步骤 5/5: 验证安装..."
python3 -c "import flask; print(f'  ✓ Flask {flask.__version__}')" 2>/dev/null || echo "  ✗ Flask 未安装"
python3 -c "from picamera2 import Picamera2; print('  ✓ picamera2')" 2>/dev/null || echo "  ✗ picamera2 未安装 (可能需要退出虚拟环境)"
python3 -c "import numpy; print(f'  ✓ numpy {numpy.__version__}')" 2>/dev/null || echo "  ✗ numpy 未安装"
python3 -c "from PIL import Image; print('  ✓ Pillow')" 2>/dev/null || echo "  ✗ Pillow 未安装"

echo ""
echo "=================================="
echo "安装完成！"
echo "=================================="
echo ""
echo "下一步操作："
echo "  1. 确保摄像头已连接到 CSI 接口"
echo "  2. 运行 'sudo raspi-config' 启用摄像头"
echo "  3. 运行 'python3 server.py' 启动 Web 服务器"
echo "  4. 或运行 'python3 camera_local.py' 测试本地程序"
echo ""
echo "Web 访问地址: http://$(hostname -I | awk '{print $1}'):8000/"
echo ""
