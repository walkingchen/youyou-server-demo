from flask import Flask, request, render_template, Response, jsonify, send_from_directory
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
import io
import os
from datetime import datetime
from threading import Lock, Condition
import time

# 创建一个 Web 应用（就像开了一家“服务小店”）
app = Flask(__name__)

# 摄像头相关配置：拍的照片会放在 shots/ 里
SHOTS_DIR = "shots"
os.makedirs(SHOTS_DIR, exist_ok=True)

# 全局摄像头对象和锁
# camera 只有一个，避免多处同时操作造成冲突
camera = None
camera_lock = Lock()
# 视频流输出缓存（保存最新的 JPEG 帧）
stream_output = None
# 启动录制时的保护锁，避免重复启动
recording_lock = Lock()
# 标记是否已经开始录制（开始推流）
recording_started = False


class StreamingOutput(io.BufferedIOBase):
    """保存最新一帧 JPEG，并用条件变量唤醒等待的线程"""
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        # 摄像头把编码后的 JPEG 写进来时会调用这里
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

def init_camera():
    """初始化摄像头（只做一次）"""
    global camera, stream_output, recording_started
    try:
        if camera is None:
            camera = Picamera2()
            # 配置摄像头用于视频流和拍照
            # 分辨率低一点、帧率低一点，CPU 压力小
            config = camera.create_video_configuration(
                main={"size": (320, 240), "format": "YUV420"},
                controls={"FrameRate": 10}
            )
            camera.configure(config)
            camera.start()
            # 准备接收 JPEG 帧的缓存
            stream_output = StreamingOutput()
            recording_started = False
            print("摄像头初始化成功！")
            time.sleep(2)  # 等待摄像头稳定
    except Exception as e:
        print(f"摄像头初始化失败: {e}")
        return None
    return camera

def generate_frames():
    """生成视频帧用于流式传输（浏览器会一直拉取）"""
    global camera, recording_started

    # 确保摄像头已初始化
    if camera is None:
        init_camera()

    if camera is None:
        # 如果摄像头仍然为空，返回错误信息
        yield b'Camera initialization failed'
        return

    try:
        # 第一次有人观看视频时，启动 JPEG 编码的录制
        if not recording_started:
            with recording_lock:
                if not recording_started:
                    # 使用硬件编码输出 JPEG，避免 Python 里做图片转换
                    camera.start_recording(JpegEncoder(), FileOutput(stream_output))
                    recording_started = True

        while True:
            # 等待新的一帧 JPEG 到来
            with stream_output.condition:
                stream_output.condition.wait()
                frame = stream_output.frame

            # 以multipart格式返回帧
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    except Exception as e:
        print(f"视频流错误: {e}")

# 注意：不要在模块加载时就初始化摄像头。
# Flask 的调试模式会启动两个进程，导致摄像头被初始化两次而失败。
# 改为“按需初始化”：在真正访问视频/拍照接口时再启动。

@app.route("/", methods=['GET'])
def index():
    """主页 - 显示所有课程"""
    return render_template('index.html')

@app.route("/old", methods=['GET'])
def hello():
    """保留原来的路由作为参考"""
    args = request.args.get('name', '').lower()
    print(args)
    if args == 'dad':
        return "dady is NOT an asshole!"
    else:
        return "youyou IS an ASSHOLE!"


@app.route('/login', methods=['GET', 'POST'])
def login():
    """简单的登录示例（教学用途）"""
    if request.method == 'POST':
        # 获取表单数据
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 简单的验证
        if username == 'shayou' and password == '123456':
            return f'Login successful! Welcome {username}'
        else:
            return 'Invalid credentials!'
    
    # GET 请求时显示登录表单
    html_form = '''
    <h1>Login Form</h1>
    <form method="POST">
        <label>Username:</label><br>
        <input type="text" name="username" required><br><br>
        
        <label>Password:</label><br>
        <input type="password" name="password" required><br><br>
        
        <input type="submit" value="Login">
    </form>
    '''
    return html_form

@app.route("/hi/")
def hi():
    """一个最简单的 HTML 页面示例"""
    return '''
        <html>
            <p>Daddy is not an asshole!</p>
        </html>
    '''

@app.route("/test")
def test():
    """打印请求信息，方便调试"""
    print(request.method)
    print(request.path)
    print(request.headers)
    return "ok"

@app.route("/mama")
def mama():
    """显示 mama.jpg 图片"""
    return send_from_directory(SHOTS_DIR, 'mama.jpg')

# ========== 摄像头相关路由 ==========

@app.route('/camera/preview')
def camera_preview():
    """第1课：摄像头预览"""
    return render_template('preview.html')

@app.route('/camera/capture')
def camera_capture():
    """第2课：预览 + 拍照"""
    return render_template('capture.html')

@app.route('/camera/gallery')
def camera_gallery():
    """第3课：完整功能（预览 + 拍照 + 相册）"""
    # 获取所有照片文件
    photos = []
    if os.path.exists(SHOTS_DIR):
        photos = [f for f in os.listdir(SHOTS_DIR) if f.endswith(('.jpg', '.png', '.jpeg'))]
        photos.sort(reverse=True)  # 最新的在前面
    return render_template('gallery.html', photos=photos)

@app.route('/video_feed')
def video_feed():
    """视频流路由（浏览器用 <img> 持续刷新显示）"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/camera/take_photo', methods=['POST'])
def take_photo():
    """拍照API（点击按钮时触发）"""
    global camera

    try:
        if camera is None:
            init_camera()

        if camera is None:
            return jsonify({
                'success': False,
                'message': '摄像头未初始化'
            })

        # 生成文件名（时间戳，避免重名）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"photo_{timestamp}.jpg"
        filepath = os.path.join(SHOTS_DIR, filename)

        # 拍照（加锁，避免和视频流抢摄像头）
        with camera_lock:
            camera.capture_file(filepath)

        return jsonify({
            'success': True,
            'message': '照片拍摄成功！',
            'filename': filename
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'拍照失败: {str(e)}'
        })

@app.route('/shots/<filename>')
def serve_photo(filename):
    """提供照片文件（相册里点击查看时会用到）"""
    return send_from_directory(SHOTS_DIR, filename)

if __name__ == "__main__":
    # 0.0.0.0 表示任何设备都能访问这个服务
    app.run(host="0.0.0.0", port=8000, debug=True)
