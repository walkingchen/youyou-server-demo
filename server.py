from flask import Flask, request, render_template, Response, jsonify, send_from_directory
from picamera import PiCamera
import io
import os
from datetime import datetime
from threading import Lock, Condition
import time

app = Flask(__name__)

# 摄像头相关配置
SHOTS_DIR = "shots"
os.makedirs(SHOTS_DIR, exist_ok=True)

# 全局摄像头对象和锁
camera = None
camera_lock = Lock()

class StreamingOutput:
    """用于流式输出的类"""
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # 新的帧开始
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

def init_camera():
    """初始化摄像头"""
    global camera
    try:
        if camera is None:
            camera = PiCamera()
            camera.resolution = (640, 480)
            camera.framerate = 24
            print("摄像头初始化成功！")
            time.sleep(2)  # 等待摄像头稳定
    except Exception as e:
        print(f"摄像头初始化失败: {e}")
        return None
    return camera

def generate_frames():
    """生成视频帧用于流式传输"""
    global camera

    # 确保摄像头已初始化
    if camera is None:
        init_camera()

    if camera is None:
        # 如果摄像头仍然为空，返回错误信息
        yield b'Camera initialization failed'
        return

    try:
        # 创建流输出对象
        output = StreamingOutput()

        # 开始连续捕获
        camera.start_recording(output, format='mjpeg')

        try:
            while True:
                with output.condition:
                    output.condition.wait()
                    frame = output.frame

                # 以multipart格式返回帧
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        finally:
            camera.stop_recording()

    except Exception as e:
        print(f"视频流错误: {e}")

# 初始化摄像头
init_camera()

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
    return '''
        <html>
            <p>Daddy is not an asshole!</p>
        </html>
    '''

@app.route("/test")
def test():
    print(request.method)
    print(request.path)
    print(request.headers)
    return "ok"

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
    # 获取所有照片
    photos = []
    if os.path.exists(SHOTS_DIR):
        photos = [f for f in os.listdir(SHOTS_DIR) if f.endswith(('.jpg', '.png', '.jpeg'))]
        photos.sort(reverse=True)  # 最新的在前面
    return render_template('gallery.html', photos=photos)

@app.route('/video_feed')
def video_feed():
    """视频流路由"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/camera/take_photo', methods=['POST'])
def take_photo():
    """拍照API"""
    global camera

    try:
        if camera is None:
            init_camera()

        if camera is None:
            return jsonify({
                'success': False,
                'message': '摄像头未初始化'
            })

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"photo_{timestamp}.jpg"
        filepath = os.path.join(SHOTS_DIR, filename)

        # 拍照
        with camera_lock:
            camera.capture(filepath)

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
    """提供照片文件"""
    return send_from_directory(SHOTS_DIR, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
