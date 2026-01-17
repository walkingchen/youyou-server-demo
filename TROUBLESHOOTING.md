# 故障排除快速指南

## ⚠️ 常见错误：ModuleNotFoundError

### 错误信息 1：picamera2 未找到

```
ModuleNotFoundError: No module named 'picamera2'
```

### 快速修复

```bash
# 1. 安装 picamera2 及其依赖
sudo apt install -y python3-picamera2 python3-numpy python3-pil

# 2. 如果在虚拟环境中，退出虚拟环境
deactivate

# 3. 使用系统 Python 运行程序
python3 camera_local.py
# 或
python3 server.py
```

### 错误信息 2：numpy 或 PIL 未找到

```
ModuleNotFoundError: No module named 'numpy'
ModuleNotFoundError: No module named 'PIL'
```

### 快速修复

```bash
# 安装依赖库
sudo apt install -y python3-numpy python3-pil

# 退出虚拟环境
deactivate

# 使用系统 Python
python3 camera_local.py
```

### 为什么会出现这个错误？

- `picamera2` 需要 `numpy` 和 `Pillow` 作为依赖
- 虚拟环境中通过 pip 安装可能缺少系统依赖
- 树莓派系统包提供预编译的二进制文件，更可靠

### 最佳实践

**不要在虚拟环境中使用 picamera2！**

```bash
# ✅ 正确方式：使用系统包
sudo apt install python3-picamera2 python3-numpy python3-pil
python3 your_script.py

# ❌ 错误方式：在虚拟环境中 pip 安装
source venv/bin/activate
pip install picamera2  # 可能会缺少依赖或编译失败！
```

---

## 🎥 摄像头未检测到

### 检查摄像头连接

```bash
vcgencmd get_camera
```

应该显示：`supported=1 detected=1`

### 如果显示 detected=0

1. 检查摄像头排线是否正确连接
2. 确保蓝色部分朝向网口方向
3. 排线插入到位并锁紧

### 启用摄像头

```bash
sudo raspi-config
```

选择：`Interface Options` → `Camera` → `Enable`

**注意**：picamera2 使用新的 libcamera 系统，不需要启用 Legacy Camera

重启：
```bash
sudo reboot
```

---

## 🔒 权限错误

### 错误信息

```
PermissionError: [Errno 13] Permission denied
```

### 解决方案

```bash
# 将用户添加到 video 组
sudo usermod -a -G video $USER

# 重新登录生效
exit
# 重新 SSH 登录
```

---

## 🌐 网页无法访问

### 检查 Flask 是否运行

```bash
python3 server.py
```

应该看到：
```
* Running on http://0.0.0.0:8000
```

### 查找树莓派 IP 地址

```bash
hostname -I
```

### 在浏览器中访问

```
http://<树莓派IP地址>:8000/
```

例如：`http://192.168.1.100:8000/`

---

## 📦 依赖安装问题

### Flask 未安装

```bash
pip3 install Flask --break-system-packages
```

### picamera2 导入失败

```bash
# 重新安装系统包
sudo apt install -y python3-picamera2 python3-numpy python3-pil

# 验证安装
python3 -c "from picamera2 import Picamera2; print('OK')"
```

---

## 🔧 完整重装（最后手段）

如果以上都不行，执行完整重装：

```bash
# 1. 卸载虚拟环境
deactivate
rm -rf venv

# 2. 安装系统包
sudo apt update
sudo apt install -y python3-pip python3-picamera2 python3-numpy python3-pil

# 3. 安装 Flask
pip3 install Flask --break-system-packages

# 4. 测试
python3 camera_local.py
```

---

## 💡 需要更多帮助？

1. 检查 `/var/log/syslog` 查看系统日志
2. 运行 `dmesg | grep camera` 查看摄像头日志
3. 查看 [Raspberry Pi 官方文档](https://www.raspberrypi.com/documentation/accessories/camera.html)
