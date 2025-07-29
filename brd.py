#!/usr/bin/env python3
"""
Python UDP广播示例
演示BROADCAST网络中的UDP广播功能

# 机器A (192.168.3.10)
python3 brd.py receiver

# 机器B (192.168.3.11) 
python3 brd.py receiver

# 机器C (192.168.3.12)
python3 brd.py sender

"""

import socket
import threading
import time
import json
from datetime import datetime

class UDPBroadcastSender:
    """UDP广播发送端"""
    
    def __init__(self, port=8888):
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # 关键：开启广播权限
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        print(f"📡 广播发送端初始化完成，目标端口: {port}")
    
    def send_broadcast(self, message, broadcast_ip="255.255.255.255"):
        """发送广播消息"""
        try:
            # 发送到广播地址
            self.sock.sendto(message.encode('utf-8'), (broadcast_ip, self.port))
            print(f"📤 已广播: {message} → {broadcast_ip}:{self.port}")
            return True
        except Exception as e:
            print(f"❌ 广播发送失败: {e}")
            return False
    
    def close(self):
        self.sock.close()

class UDPBroadcastReceiver:
    """UDP广播接收端"""
    
    def __init__(self, port=8888, device_name="Python接收器"):
        self.port = port
        self.device_name = device_name
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # 允许多个程序绑定同一端口（用于广播接收）
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # 绑定到所有接口，接收广播
        self.sock.bind(('', port))  # 空字符串 = INADDR_ANY
        print(f"📻 {device_name} 开始监听广播，端口: {port}")
    
    def listen_for_broadcasts(self):
        """监听广播消息"""
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                message = data.decode('utf-8')
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                print(f"📥 [{timestamp}] {self.device_name} 收到来自 {addr[0]}:{addr[1]} 的广播:")
                print(f"    {message}")
                    
            except Exception as e:
                print(f"❌ 接收广播失败: {e}")
    
    def close(self):
        self.sock.close()

def demo_broadcast_sender():
    """演示广播发送"""
    print("=" * 50)
    print("📡 UDP广播发送端演示")
    print("=" * 50)
    
    sender = UDPBroadcastSender()
    
    try:
        # 发送几个测试广播
        sender.send_broadcast("Hello, 局域网内的所有设备!")
        time.sleep(1)
        sender.send_broadcast("这是第二条广播消息")
        time.sleep(1)
        sender.send_broadcast("广播测试完成")
        
    finally:
        sender.close()

def demo_broadcast_receiver():
    """演示广播接收"""
    print("=" * 50)
    print("📻 UDP广播接收端演示")
    print("=" * 50)
    
    device_name = f"设备-{socket.gethostname()}"
    receiver = UDPBroadcastReceiver(device_name=device_name)
    
    try:
        print("等待广播消息... (Ctrl+C 停止)")
        receiver.listen_for_broadcasts()
    except KeyboardInterrupt:
        print("\n🛑 停止监听广播")
    finally:
        receiver.close()

def demo_multiple_receivers():
    """演示多个接收端 - 使用不同端口"""
    print("=" * 50)
    print("📻 多端口接收端演示")
    print("=" * 50)
    
    # 创建3个不同端口的接收器
    receivers = []
    threads = []
    ports = [8888, 8889, 8890]
    
    for i, port in enumerate(ports):
        device_name = f"设备-{i+1}"
        try:
            receiver = UDPBroadcastReceiver(port=port, device_name=device_name)
            receivers.append(receiver)
            
            # 每个接收器在独立线程中运行
            thread = threading.Thread(
                target=receiver.listen_for_broadcasts,
                daemon=True
            )
            thread.start()
            threads.append(thread)
            
        except Exception as e:
            print(f"❌ 创建 {device_name} (端口{port}) 失败: {e}")
    
    try:
        print(f"已启动 {len(receivers)} 个接收端，分别监听端口: {ports}")
        print("要测试，请运行: python3 brd.py multi_sender")
        
        # 主线程等待
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 停止所有接收端")
    finally:
        for receiver in receivers:
            receiver.close()

def demo_multi_port_sender():
    """向多个端口发送广播"""
    print("=" * 50)
    print("📡 多端口广播发送")
    print("=" * 50)
    
    ports = [8888, 8889, 8890]
    
    for port in ports:
        print(f"\n--- 向端口 {port} 发送广播 ---")
        sender = UDPBroadcastSender(port=port)
        message = f"这是发送到端口 {port} 的广播消息"
        sender.send_broadcast(message)
        sender.close()
        time.sleep(0.5)

def demo_simple_test():
    """简单快速测试"""
    print("=" * 50)
    print("🚀 简单测试")
    print("=" * 50)
    
    # 创建一个发送端和接收端在同一个程序中
    receiver = UDPBroadcastReceiver(device_name="测试接收器")
    
    # 在后台线程启动接收
    def receive_in_background():
        try:
            receiver.listen_for_broadcasts()
        except:
            pass
    
    receiver_thread = threading.Thread(target=receive_in_background, daemon=True)
    receiver_thread.start()
    
    # 等待接收器启动
    time.sleep(1)
    
    # 发送测试消息
    sender = UDPBroadcastSender()
    print("发送测试广播...")
    sender.send_broadcast("测试广播消息 - 如果你看到这条消息，说明广播工作正常！")
    
    # 等待消息被接收
    time.sleep(2)
    
    sender.close()
    receiver.close()
    print("测试完成！")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 brd.py sender        # 发送端")
        print("  python3 brd.py receiver      # 接收端")
        print("  python3 brd.py multi         # 多端口接收端")
        print("  python3 brd.py multi_sender  # 多端口发送端")
        print("  python3 brd.py test          # 简单测试")
        sys.exit(1)
    
    mode = sys.argv[1].lower()
    
    if mode == "sender":
        demo_broadcast_sender()
    elif mode == "receiver":
        demo_broadcast_receiver()
    elif mode == "multi":
        demo_multiple_receivers()
    elif mode == "multi_sender":
        demo_multi_port_sender()
    elif mode == "test":
        demo_simple_test()
    else:
        print("未知模式！")
