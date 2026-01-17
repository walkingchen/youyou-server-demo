#!/usr/bin/env python3
"""
本地摄像头控制脚本 - 教学示例
功能：启动摄像头预览，按's'键拍照保存到shots文件夹
按键：
  - 's': 拍摄照片
  - 'q': 退出程序
"""

import os
from datetime import datetime
from picamera2 import Picamera2
import time

# 确保shots文件夹存在
SHOTS_DIR = "shots"
os.makedirs(SHOTS_DIR, exist_ok=True)

def main():
    print("=" * 50)
    print("摄像头本地控制程序")
    print("=" * 50)
    print("按 's' 键拍照，按 'q' 键退出")
    print("-" * 50)

    # 初始化摄像头
    print("正在初始化摄像头...")
    picam2 = Picamera2()

    # 配置摄像头
    # preview_config 适用于预览和拍照
    camera_config = picam2.create_preview_configuration()
    picam2.configure(camera_config)

    # 启动摄像头
    picam2.start()
    print("摄像头已启动！")
    print("等待摄像头稳定...")
    time.sleep(2)
    print("\n提示：由于这是命令行程序，预览窗口可能不会显示")
    print("但拍照功能正常工作。\n")

    try:
        photo_count = 0
        while True:
            # 等待用户输入
            print("请输入命令 (s=拍照, q=退出): ", end='', flush=True)
            user_input = input().strip().lower()

            if user_input == 's':
                # 拍摄照片
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"photo_{timestamp}.jpg"
                filepath = os.path.join(SHOTS_DIR, filename)

                # 捕获图像
                picam2.capture_file(filepath)
                photo_count += 1

                print(f"✓ 照片已保存: {filepath}")
                print(f"  已拍摄 {photo_count} 张照片\n")

            elif user_input == 'q':
                print("\n正在退出...")
                break
            else:
                print("无效命令，请输入 's' 或 'q'\n")

    except KeyboardInterrupt:
        print("\n\n检测到 Ctrl+C，正在退出...")

    finally:
        # 清理资源
        picam2.stop()
        print("摄像头已关闭")
        print(f"总共拍摄了 {photo_count} 张照片")
        print("程序结束")

if __name__ == "__main__":
    main()
