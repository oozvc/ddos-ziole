#!/usr/bin/env python3
# Advanced DDoS Protection System v10.0 - Fixed Version

import os
import time
import sys
import socket
import struct
import fcntl
import select
import argparse
import threading
import signal
import json
import re
import subprocess
import datetime
import traceback
from collections import defaultdict, deque

# ======================
# FIXED NETWORK INTERFACE DETECTION
# ======================
def get_network_interfaces():
    """Mendapatkan daftar interface jaringan secara aman"""
    try:
        # Metode 1: Gunakan /proc/net/dev jika akses /sys diblokir
        interfaces = []
        with open('/proc/net/dev', 'r') as f:
            for line in f.readlines()[2:]:  # Lewati header
                if ':' in line:
                    iface = line.split(':')[0].strip()
                    if iface != 'lo':  # Abaikan loopback
                        interfaces.append(iface)
        return interfaces
    except Exception as e:
        print(f"⚠️ Error reading interfaces: {e}")
        return ['eth0']  # Fallback ke antarmuka default

# ======================
# KONFIGURASI UTAMA
# ======================
DEFAULT_CONFIG = {
    "interface": "eth0",
    "threshold_pps": 1000,
    "threshold_bps": 100000000,  # 100 Mbps
    "ban_time": 300,  # 5 menit
    "whitelist": ["192.168.1.0/24", "10.0.0.0/8"],
    "log_file": "/var/log/antiddos.log",
    "syslog_server": None,
    "debug": False
}

def get_user_config():
    """Membaca konfigurasi dari file atau menggunakan default"""
    config_path = "/etc/antiddos.conf"
    config = DEFAULT_CONFIG.copy()
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
            config.update(user_config)
    except Exception as e:
        print(f"⚠️ Config error: {e}. Using defaults.")
    
    # Deteksi interface jaringan
    interfaces = get_network_interfaces()
    if interfaces and config['interface'] not in interfaces:
        config['interface'] = interfaces[0]
        print(f"ℹ️ Using detected interface: {config['interface']}")
    
    return config

# ======================
# UTILITAS JARINGAN
# ======================
def get_mac_address(interface):
    """Mendapatkan alamat MAC antarmuka"""
    try:
        with open(f'/sys/class/net/{interface}/address', 'r') as f:
            return f.read().strip()
    except:
        return "00:00:00:00:00:00"

def ip_to_int(ip):
    """Konversi IP string ke integer"""
    return struct.unpack("!I", socket.inet_aton(ip))[0]

def int_to_ip(ip_int):
    """Konversi integer ke IP string"""
    return socket.inet_ntoa(struct.pack("!I", ip_int))

def is_whitelisted(ip, whitelist):
    """Cek apakah IP ada di whitelist"""
    ip_int = ip_to_int(ip)
    for net in whitelist:
        net_addr, bits = net.split('/')
        net_int = ip_to_int(net_addr)
        mask = (0xFFFFFFFF << (32 - int(bits))) & 0xFFFFFFFF
        if (ip_int & mask) == (net_int & mask):
            return True
    return False

# ======================
# DETECTION ENGINE
# ======================
class TrafficMonitor:
    def __init__(self, config):
        self.config = config
        self.interface = config['interface']
        self.pps_threshold = config['threshold_pps']
        self.bps_threshold = config['threshold_bps']
        self.ban_time = config['ban_time']
        self.whitelist = config['whitelist']
        
        self.pps_count = defaultdict(lambda: deque(maxlen=10))
        self.bps_count = defaultdict(int)
        self.banned_ips = {}
        self.last_reset = time.time()
        
        # Setup socket raw
        self.sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))
        self.sock.bind((self.interface, 0))
        
        # Non-blocking socket
        self.sock.setblocking(False)
        
        print(f"🔥 Starting DDoS protection on {self.interface}")
        print(f"├─ Threshold: {self.pps_threshold} PPS | {self.bps_threshold/1e6:.1f} Mbps")
        print(f"├─ Ban time: {self.ban_time} seconds")
        print(f"└─ Whitelist: {len(self.whitelist)} networks")
    
    def update_banned_ips(self):
        """Hapus IP yang sudah habis masa bannya"""
        current_time = time.time()
        expired = [ip for ip, ban_time in self.banned_ips.items() 
                  if current_time > ban_time + self.ban_time]
        
        for ip in expired:
            del self.banned_ips[ip]
            self.unblock_ip(ip)
    
    def block_ip(self, ip):
        """Blokir IP menggunakan iptables"""
        if not is_whitelisted(ip, self.whitelist) and ip not in self.banned_ips:
            os.system(f"iptables -A INPUT -s {ip} -j DROP")
            self.banned_ips[ip] = time.time()
            self.log_attack(ip, "BLOCKED")
    
    def unblock_ip(self, ip):
        """Hapus blokir IP"""
        os.system(f"iptables -D INPUT -s {ip} -j DROP")
        self.log_attack(ip, "UNBLOCKED")
    
    def log_attack(self, ip, action):
        """Catat serangan ke file log"""
        log_msg = f"[{datetime.datetime.now()}] {action} {ip} on {self.interface}"
        print(log_msg)
        
        try:
            with open(self.config['log_file'], 'a') as f:
                f.write(log_msg + "\n")
        except:
            pass
    
    def process_packet(self, packet):
        """Proses paket jaringan untuk deteksi serangan"""
        # Ekstrak header Ethernet
        eth_header = packet[:14]
        eth = struct.unpack('!6s6sH', eth_header)
        eth_protocol = socket.ntohs(eth[2])
        
        # Hanya proses paket IP
        if eth_protocol != 0x0800:
            return
        
        # Ekstrak header IP
        ip_header = packet[14:34]
        iph = struct.unpack('!BBHHHBBH4s4s', ip_header)
        s_addr = socket.inet_ntoa(iph[8])
        
        # Skip whitelisted IPs
        if is_whitelisted(s_addr, self.whitelist):
            return
        
        # Hitung ukuran paket
        version_ihl = iph[0]
        ihl = version_ihl & 0xF
        iph_length = ihl * 4
        packet_size = len(packet) - 14
        
        # Update counters
        current_time = time.time()
        self.pps_count[s_addr].append(current_time)
        self.bps_count[s_addr] += packet_size
        
        # Reset counters setiap 1 detik
        if current_time - self.last_reset >= 1.0:
            for ip in list(self.bps_count.keys()):
                # Hitung PPS
                timestamps = self.pps_count[ip]
                while timestamps and current_time - timestamps[0] > 1.0:
                    timestamps.popleft()
                pps = len(timestamps)
                
                # Hitung BPS
                bps = self.bps_count[ip]
                self.bps_count[ip] = 0  # Reset counter
                
                # Deteksi serangan
                if pps > self.pps_threshold or bps > self.bps_threshold:
                    self.block_ip(ip)
            
            self.last_reset = current_time
            self.update_banned_ips()
    
    def start(self):
        """Mulai monitoring lalu lintas"""
        try:
            while True:
                ready, _, _ = select.select([self.sock], [], [], 1)
                if ready:
                    packet = self.sock.recv(65535)
                    self.process_packet(packet)
        except KeyboardInterrupt:
            print("\n🛑 Stopping DDoS protection")
        finally:
            self.sock.close()
            # Bersihkan iptables
            for ip in list(self.banned_ips.keys()):
                self.unblock_ip(ip)

# ======================
# MAIN EXECUTION
# ======================
def main():
    print("╔═╗┬ ┬┌─┐┌┬┐┌─┐┌─┐┌─┐┬─┐  ╔╦╗┌─┐┌┬┐┌─┐┌┬┐┌─┐┌─┐")
    print("║  ├─┤├┤  │ ├┤ └─┐├┤ ├┬┘   ║║├┤  │ ├─┤ │ ├┤ └─┐")
    print("╚═╝┴ ┴└─┘ ┴ └─┘└─┘└─┘┴└─  ═╩╝└─┘ ┴ ┴ ┴ ┴ └─┘└─┘")
    print("Advanced DDoS Protection System v10.1 - Fixed\n")
    
    try:
        config = get_user_config()
        monitor = TrafficMonitor(config)
        monitor.start()
    except Exception as e:
        print(f"💥 Critical error: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # Pastikan dijalankan sebagai root
    if os.geteuid() != 0:
        print("❌ Error: Script must be run as root!")
        sys.exit(1)
    
    main()