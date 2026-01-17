# 树莓派摄像头教学系统

这是一个运行在 Raspberry Pi Zero W 上的摄像头控制教学项目，用于学习 Python、Flask 和摄像头编程。

## 项目特点

- 📚 **分步教学**：每个页面逐步增加功能，便于理解
- 🎥 **实时预览**：网页实时显示摄像头画面
- 📸 **拍照功能**：点击按钮即可拍照并保存
- 🖼️ **照片相册**：展示所有已拍摄的照片
- 💻 **命令行版本**：额外提供本地命令行控制程序

## 系统要求

- Raspberry Pi Zero W（或其他树莓派型号）
- Raspberry Pi Camera Module（通过 CSI 接口连接）
- Raspberry Pi OS（推荐最新版本）
- Python 3.7+

## 安装步骤

### 1. 确保摄像头已正确连接

将摄像头模块连接到树莓派的 CSI Camera Connector 接口。

### 2. 启用摄像头

```bash
sudo raspi-config
```

选择 `Interface Options` -> `Camera` -> `Enable`

### 3. 安装依赖

```bash
# 更新系统
sudo apt update
sudo apt upgrade

# 安装系统依赖
sudo apt install -y python3-pip python3-picamera2 python3-opencv

# 克隆或下载项目
cd ~
git clone <your-repo-url>
cd youyou-server-demo

# 安装 Python 依赖
pip3 install -r requirements.txt
```

### 4. 运行项目

#### 方式一：运行 Web 服务器

```bash
python3 server.py
```

然后在浏览器中访问：
- 主页：`http://<树莓派IP地址>:8000/`
- 第1课：`http://<树莓派IP地址>:8000/camera/preview`
- 第2课：`http://<树莓派IP地址>:8000/camera/capture`
- 第3课：`http://<树莓派IP地址>:8000/camera/gallery`

#### 方式二：运行本地命令行程序

```bash
python3 camera_local.py
```

按 `s` 键拍照，按 `q` 键退出。

## 项目结构

```
youyou-server-demo/
├── server.py              # Flask 主程序
├── camera_local.py        # 本地命令行程序
├── requirements.txt       # Python 依赖
├── shots/                 # 照片保存目录
├── templates/             # HTML 模板
│   ├── base.html         # 基础模板
│   ├── index.html        # 首页
│   ├── preview.html      # 第1课：预览
│   ├── capture.html      # 第2课：拍照
│   └── gallery.html      # 第3课：相册
└── static/               # 静态资源
    └── css/
        └── style.css     # 样式表
```

## 教学内容

### 第1课：摄像头实时预览

学习如何启动摄像头并在网页中显示实时画面。

**知识点**：
- 视频流的概念
- Flask Response 流式传输
- HTML `<img>` 标签显示视频流

### 第2课：预览 + 拍照功能

在预览的基础上添加拍照功能。

**知识点**：
- JavaScript fetch API
- Flask POST 路由
- 异步请求处理
- 用户反馈提示

### 第3课：完整功能（预览 + 拍照 + 相册）

整合所有功能，展示照片相册。

**知识点**：
- 文件系统操作
- 动态内容渲染
- 图片网格布局
- 完整的用户体验设计

## 核心代码说明

### 摄像头初始化（server.py）

```python
def init_camera():
    global camera
    camera = Picamera2()
    config = camera.create_video_configuration(
        main={"size": (640, 480), "format": "RGB888"}
    )
    camera.configure(config)
    camera.start()
```

### 视频流生成

```python
def generate_frames():
    while True:
        frame = camera.capture_array()
        img = Image.fromarray(frame)
        # 转换为 JPEG 并发送
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + img_data + b'\r\n')
```

### 拍照功能

```python
@app.route('/camera/take_photo', methods=['POST'])
def take_photo():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"photo_{timestamp}.jpg"
    camera.capture_file(f"shots/{filename}")
    return jsonify({'success': True, 'filename': filename})
```

## 故障排除

### 问题1：摄像头未检测到

```bash
# 检查摄像头是否被识别
vcgencmd get_camera

# 应该显示：
# supported=1 detected=1
```

### 问题2：权限错误

```bash
# 将用户添加到 video 组
sudo usermod -a -G video $USER

# 重新登录以应用更改
```

### 问题3：picamera2 导入错误

```bash
# 确保使用 Python 3
python3 --version

# 重新安装 picamera2
sudo apt install -y python3-picamera2
```

### 问题4：网页无法访问

- 确保防火墙允许 8000 端口
- 检查树莓派的 IP 地址：`hostname -I`
- 确保树莓派和电脑在同一网络

## 扩展练习

1. 添加视频录制功能
2. 实现照片删除功能
3. 添加照片下载按钮
4. 实现照片滤镜效果
5. 添加定时拍照功能
6. 实现人脸检测（使用 OpenCV）

## 技术栈

- **后端**：Python 3, Flask
- **摄像头库**：picamera2
- **图像处理**：Pillow
- **前端**：HTML5, CSS3, JavaScript
- **硬件**：Raspberry Pi, Camera Module

## 许可证

本项目仅用于教学目的。

## 作者

教学项目 - Raspberry Pi 摄像头控制

## 更新日志

### v1.0.0 (2026-01-17)
- 初始版本
- 实现摄像头预览功能
- 实现拍照功能
- 实现照片相册
- 添加本地命令行程序
