
#!/usr/bin/env python3
"""
██████╗ ██╗  ██╗██╗ ██████╗ ██╗      ██████╗ ███████╗
██╔══██╗██║  ██║██║██╔═══██╗██║     ██╔═══██╗██╔════╝
██████╔╝███████║██║██║   ██║██║     ██║   ██║█████╗  
██╔═══╝ ██╔══██║██║██║   ██║██║     ██║   ██║██╔══╝  
██║     ██║  ██║██║╚██████╔╝███████╗╚██████╔╝██║     
╚═╝     ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝     
"""
import os
import sys
import time
import random
import secrets
import subprocess
import requests
import threading
import socket
import struct
import fcntl
from collections import deque

# ===== KONSTANTA WARNA =====
RED = "\033[91m"
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"
BANNER = f"""
{CYAN + BOLD}
╔═╗┬ ┬┌─┐┌┬┐┌─┐┌─┐┌─┐┬─┐  ╔╦╗┌─┐┌┬┐┌─┐┌┬┐┌─┐┌─┐
║  ├─┤├┤  │ ├┤ └─┐├┤ ├┬┘   ║║├┤  │ ├─┤ │ ├┤ └─┐
╚═╝┴ ┴└─┘ ┴ └─┘└─┘└─┘┴└─  ═╩╝└─┘ ┴ ┴ ┴ ┴ └─┘└─┘
Advanced DDoS Protection System v10.0
{RESET}"""

# ===== FUNGSI UTILITAS =====
def clear_screen():
    """Bersihkan layar konsol"""
    os.system('clear' if os.name == 'posix' else 'cls')

def show_banner():
    """Tampilkan banner sistem"""
    clear_screen()
    print(BANNER)
    print(f"{YELLOW}╞═══════════════════════════════════════════════════════╡{RESET}")

def run_command(cmd):
    """Jalankan perintah shell"""
    try:
        subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        return False

def is_root():
    """Periksa apakah dijalankan sebagai root"""
    return os.geteuid() == 0

def get_network_interfaces():
    """Dapatkan daftar interface jaringan yang tersedia"""
    interfaces = []
    for device in os.listdir('/sys/class/net'):
        if device != 'lo':  # Skip loopback
            interfaces.append(device)
    return interfaces

def get_ip_address(ifname):
    """Dapatkan IP address dari interface"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15].encode())
        )[20:24])
    except:
        return None

# ===== SISTEM KONFIGURASI INTERAKTIF =====
def get_user_config():
    """Dapatkan konfigurasi langsung dari pengguna"""
    show_banner()
    config = {}
    
    # Pilih interface jaringan
    interfaces = get_network_interfaces()
    if not interfaces:
        print(f"{RED}Tidak ditemukan interface jaringan!{RESET}")
        sys.exit(1)
    
    print(f"{GREEN}🌐 KONFIGURASI JARINGAN{RESET}")
    print("="*50)
    print("Pilih interface jaringan:")
    for i, iface in enumerate(interfaces, 1):
        ip = get_ip_address(iface)
        print(f"{i}) {iface} - {ip if ip else 'No IP'}")
    
    iface_choice = int(input("\nPilihan: ").strip()) - 1
    if iface_choice < 0 or iface_choice >= len(interfaces):
        print(f"{RED}Pilihan tidak valid!{RESET}")
        sys.exit(1)
    
    config['interface'] = interfaces[iface_choice]
    config['ip_address'] = get_ip_address(config['interface'])
    
    if not config['ip_address']:
        print(f"{RED}Interface {config['interface']} tidak memiliki alamat IP!{RESET}")
        sys.exit(1)
    
    print(f"\n{BLUE}🔐 KONFIGURASI CLOUDFLARE (Opsional){RESET}")
    print("="*50)
    if input("Gunakan Cloudflare? (y/n): ").lower() == 'y':
        config['cloudflare_api_key'] = input("Cloudflare API Key: ").strip()
        config['cloudflare_zone_id'] = input("Cloudflare Zone ID: ").strip()
    
    print(f"\n{MAGENTA}🚪 KONFIGURASI PORT{RESET}")
    print("="*50)
    print("Port hopping membuat port server berubah secara acak")
    start = input("Port awal (default 30000): ").strip() or "30000"
    end = input("Port akhir (default 50000): ").strip() or "50000"
    config['mtd_port_range'] = [int(start), int(end)]
    
    interval = input("Interval perubahan port (detik, default 30): ").strip() or "30"
    config['port_hop_interval'] = int(interval)
    
    # Mode perlindungan tambahan
    print(f"\n{YELLOW}🛡️ MODE PERLINDUNGAN TAMBAHAN{RESET}")
    print("="*50)
    config['tcp_syn_cookies'] = input("Aktifkan TCP SYN Cookies? (y/n, default y): ").strip().lower() != 'n'
    config['icmp_block'] = input("Blokir semua ping (ICMP)? (y/n, default y): ").strip().lower() != 'n'
    
    # Threshold serangan
    print(f"\n{RED}🚨 THRESHOLD DETEKSI SERANGAN{RESET}")
    print("="*50)
    print("Atur batas deteksi serangan (permintaan/detik)")
    config['thresholds'] = {
        'syn': int(input("Threshold SYN flood (default 5000): ").strip() or "5000"),
        'udp': int(input("Threshold UDP flood (default 10000): ").strip() or "10000"),
        'icmp': int(input("Threshold ICMP flood (default 2000): ").strip() or "2000"),
        'http': int(input("Threshold HTTP flood (default 3000): ").strip() or "3000"),
        'slowloris': int(input("Threshold Slowloris (default 100): ").strip() or "100"),
    }
    
    return config

# ===== SISTEM PROTEKSI UTAMA =====
class ZioleDDOSShield:
    def __init__(self, config):
        self.config = config
        self.current_port = random.randint(*config['mtd_port_range'])
        self.last_port_change = time.time()
        self.protection_active = True
        self.blocked_ips = set()
        self.attack_history = deque(maxlen=100)
        self.traffic_history = deque(maxlen=60)
        self.start_time = time.time()
        print(f"{GREEN}[🛡️] Perlindungan aktif untuk {config['ip_address']} pada {config['interface']}{RESET}")

    def init_firewall(self):
        """Inisialisasi firewall dengan rules ketat"""
        print(f"{CYAN}[🔥] Menginisialisasi firewall...{RESET}")
        
        # Reset firewall
        run_command("iptables -F")
        run_command("iptables -X")
        run_command("iptables -t nat -F")
        
        # Default policy
        run_command("iptables -P INPUT DROP")
        run_command("iptables -P FORWARD DROP")
        run_command("iptables -P OUTPUT ACCEPT")
        
        # Allow localhost
        run_command("iptables -A INPUT -i lo -j ACCEPT")
        
        # Allow established connections
        run_command("iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT")
        
        # Dynamic port MTD
        self.update_port_redirect()
        
        # Rate limiting dasar
        run_command("iptables -A INPUT -p tcp --syn -m limit --limit 100/s --limit-burst 100 -j ACCEPT")
        run_command("iptables -A INPUT -p tcp --syn -j DROP")
        
        # Kernel hardening
        if self.config['tcp_syn_cookies']:
            run_command("sysctl -w net.ipv4.tcp_syncookies=1")
        if self.config['icmp_block']:
            run_command("iptables -A INPUT -p icmp -j DROP")
            run_command("sysctl -w net.ipv4.icmp_echo_ignore_all=1")
        
        # Advanced protection
        run_command("sysctl -w net.ipv4.tcp_max_syn_backlog=2048")
        run_command("sysctl -w net.core.somaxconn=1024")
        run_command("sysctl -w net.netfilter.nf_conntrack_max=1000000")
        
        print(f"{GREEN}[✅] Firewall diinisialisasi!{RESET}")
    
    def update_port_redirect(self):
        """Update redirect port di firewall"""
        run_command(f"iptables -t nat -A PREROUTING -i {self.config['interface']} -p tcp --dport 80 -j REDIRECT --to-port {self.current_port}")
        print(f"{CYAN}[🔄] Port 80 di-redirect ke: {self.current_port}{RESET}")
    
    def rotate_port(self):
        """Rotasi port secara berkala"""
        if time.time() - self.last_port_change > self.config['port_hop_interval']:
            # Hapus rules lama
            run_command("iptables -t nat -F PREROUTING")
            
            # Pilih port baru
            self.current_port = random.randint(*self.config['mtd_port_range'])
            self.last_port_change = time.time()
            
            # Tambahkan rule baru
            self.update_port_redirect()
            print(f"{MAGENTA}[🔄] PORT BERUBAH: {self.current_port}{RESET}")
    
    def get_traffic_stats(self):
        """Dapatkan statistik traffic jaringan (simulasi)"""
        # Simulasi traffic dengan kemungkinan serangan
        traffic = {
            'syn': random.randint(100, 5000),
            'udp': random.randint(50, 3000),
            'icmp': 0 if self.config['icmp_block'] else random.randint(20, 1000),
            'http': random.randint(200, 4000),
            'slowloris': random.randint(1, 200)
        }
        
        # 20% kemungkinan serangan
        if random.random() < 0.2:
            attack_type = random.choice(list(traffic.keys()))
            traffic[attack_type] *= random.randint(5, 20)
        
        return traffic
    
    def check_attacks(self, traffic):
        """Periksa apakah ada serangan berdasarkan traffic"""
        detected = False
        
        for attack_type, rate in traffic.items():
            threshold = self.config['thresholds'].get(attack_type, 1000)
            if rate > threshold:
                detected = True
                self.handle_attack(attack_type, rate)
                self.record_attack(attack_type, rate)
        
        return detected
    
    def record_attack(self, attack_type, rate):
        """Catat serangan dalam history"""
        timestamp = time.strftime("%H:%M:%S")
        self.attack_history.append({
            'time': timestamp,
            'type': attack_type,
            'rate': rate
        })
    
    def handle_attack(self, attack_type, rate):
        """Tangani serangan yang terdeteksi"""
        print(f"{RED}[🚨] SERANGAN {attack_type.upper()} TERDETEKSI! Rate: {rate}/s{RESET}")
        
        # 1. Blokir sementara traffic mencurigakan
        protocol = self.get_attack_protocol(attack_type)
        run_command(f"iptables -A INPUT -p {protocol} -m limit --limit 50/s -j ACCEPT")
        run_command(f"iptables -A INPUT -p {protocol} -j DROP")
        
        # 2. Notifikasi
        self.send_alert(f"Serangan {attack_type} terdeteksi - Rate {rate}/s")
        
        # 3. Aktifkan Cloudflare Under Attack Mode jika tersedia
        if self.config.get('cloudflare_api_key') and attack_type == 'http':
            self.enable_captcha()
        
        # 4. Dynamic threshold adjustment
        self.adjust_threshold(attack_type, rate)
    
    def get_attack_protocol(self, attack_type):
        """Dapatkan protokol berdasarkan jenis serangan"""
        protocol_map = {
            'syn': 'tcp',
            'http': 'tcp',
            'slowloris': 'tcp',
            'udp': 'udp',
            'icmp': 'icmp'
        }
        return protocol_map.get(attack_type, 'tcp')
    
    def adjust_threshold(self, attack_type, current_rate):
        """Sesuaikan threshold secara dinamis"""
        current_threshold = self.config['thresholds'][attack_type]
        new_threshold = int(current_threshold * 1.2)
        
        # Batasi peningkatan maksimal 200% dari traffic saat ini
        if new_threshold < current_rate * 2:
            self.config['thresholds'][attack_type] = new_threshold
            print(f"{YELLOW}[⚖️] Threshold {attack_type} ditingkatkan menjadi {new_threshold}{RESET}")
    
    def enable_captcha(self):
        """Aktifkan CAPTCHA melalui Cloudflare"""
        api_key = self.config.get('cloudflare_api_key', '')
        zone_id = self.config.get('cloudflare_zone_id', '')
        
        if api_key and zone_id:
            print(f"{YELLOW}[🔐] Mengaktifkan mode Under Attack di Cloudflare{RESET}")
            try:
                response = requests.patch(
                    f"https://api.cloudflare.com/client/v4/zones/{zone_id}/settings/security_level",
                    json={"value": "under_attack"},
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=5
                )
                if response.status_code == 200:
                    print(f"{GREEN}[✅] Cloudflare Under Attack Mode diaktifkan!{RESET}")
                else:
                    print(f"{RED}[⚠️] Error Cloudflare: {response.text}{RESET}")
            except Exception as e:
                print(f"{RED}[⚠️] Error Cloudflare: {e}{RESET}")
    
    def send_alert(self, message):
        """Kirim notifikasi (simulasi)"""
        print(f"{YELLOW}[📢] ALERT: {message}{RESET}")
        # Implementasi nyata: Kirim email/SMS/Telegram
    
    def show_status(self, traffic, attack_detected):
        """Tampilkan status sistem"""
        clear_screen()
        print(BANNER)
        
        # Waktu operasi
        uptime = time.time() - self.start_time
        hours, rem = divmod(uptime, 3600)
        minutes, seconds = divmod(rem, 60)
        uptime_str = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        
        print(f"{GREEN}🛡️ STATUS PERLINDUNGAN{RESET}")
        print("="*50)
        print(f"Protected IP     : {self.config['ip_address']}")
        print(f"Interface        : {self.config['interface']}")
        print(f"Current Port     : {self.current_port}")
        print(f"Next Port Change : {int(self.config['port_hop_interval'] - (time.time() - self.last_port_change))}s")
        print(f"Uptime           : {uptime_str}")
        print(f"Blocked IPs      : {len(self.blocked_ips)}")
        
        # Mode perlindungan
        print(f"\n{BLUE}🔒 MODE PERLINDUNGAN{RESET}")
        print("="*50)
        print(f"SYN Cookies      : {'Aktif' if self.config['tcp_syn_cookies'] else 'Nonaktif'}")
        print(f"ICMP Block       : {'Aktif' if self.config['icmp_block'] else 'Nonaktif'}")
        print(f"Port Hopping     : Aktif ({len(self.config['mtd_port_range']) * 1000} port)")
        
        # Statistik traffic
        print(f"\n{YELLOW}📊 TRAFFIC MONITOR{RESET}")
        print("="*50)
        for attack, rate in traffic.items():
            threshold = self.config['thresholds'].get(attack, 1000)
            status = f"{RED}ATTACK!{RESET}" if rate > threshold else f"{GREEN}Normal{RESET}"
            print(f"{attack.upper().ljust(10)}: {str(rate).ljust(8)}/s  [Threshold: {threshold}] - {status}")
        
        # History serangan
        if self.attack_history:
            print(f"\n{RED}🚨 HISTORY SERANGAN (5 Terakhir){RESET}")
            print("="*50)
            for attack in list(self.attack_history)[-5:]:
                print(f"{attack['time']} - {attack['type'].upper()}: {attack['rate']}/s")
        
        print(f"\n{BLUE}Tekan Ctrl+C untuk menghentikan perlindungan{RESET}")
    
    def start_protection(self):
        """Jalankan sistem perlindungan utama"""
        self.init_firewall()
        print(f"{GREEN}[🚀] Sistem perlindungan DDoS aktif!{RESET}")
        print(f"{YELLOW}[ℹ] Tekan Ctrl+C untuk berhenti{RESET}")
        
        try:
            while self.protection_active:
                self.rotate_port()
                
                # Dapatkan statistik traffic
                traffic = self.get_traffic_stats()
                
                # Periksa serangan
                attack_detected = self.check_attacks(traffic)
                
                # Tampilkan status
                self.show_status(traffic, attack_detected)
                
                # Tunggu hingga refresh berikutnya
                time.sleep(1)
                
        except KeyboardInterrupt:
            print(f"{YELLOW}\n[🛑] Menghentikan perlindungan...{RESET}")
            self.cleanup()
    
    def cleanup(self):
        """Bersihkan aturan firewall sebelum keluar"""
        print(f"{CYAN}[🧹] Membersihkan aturan firewall...{RESET}")
        run_command("iptables -F")
        run_command("iptables -X")
        run_command("iptables -t nat -F")
        run_command("iptables -P INPUT ACCEPT")
        run_command("iptables -P FORWARD ACCEPT")
        run_command("iptables -P OUTPUT ACCEPT")
        
        # Reset kernel parameters
        run_command("sysctl -w net.ipv4.tcp_syncookies=0")
        run_command("sysctl -w net.ipv4.icmp_echo_ignore_all=0")
        
        print(f"{GREEN}[✅] Sistem dihentikan dengan aman!{RESET}")

# ===== EKSEKUSI UTAMA =====
if __name__ == "__main__":
    if not is_root():
        print(f"{RED}ERROR: Skrip harus dijalankan sebagai root!{RESET}")
        print("Gunakan: sudo python3 anti_ddos_ziole.py")
        sys.exit(1)
    
    # Dapatkan konfigurasi dari pengguna
    config = get_user_config()
    
    # Konfirmasi konfigurasi
    show_banner()
    print(f"\n{GREEN}⚙️ KONFIGURASI YANG DIPILIH{RESET}")
    print("="*50)
    print(f"Interface        : {config['interface']}")
    print(f"IP Address       : {config['ip_address']}")
    print(f"Port Range       : {config['mtd_port_range'][0]}-{config['mtd_port_range'][1]}")
    print(f"Port Hop Interval: {config['port_hop_interval']}s")
    print(f"SYN Cookies      : {'Aktif' if config['tcp_syn_cookies'] else 'Nonaktif'}")
    print(f"ICMP Block       : {'Aktif' if config['icmp_block'] else 'Nonaktif'}")
    print("\nThreshold Serangan:")
    for attack, threshold in config['thresholds'].items():
        print(f"- {attack.upper().ljust(10)}: {threshold}/s")
    
    if input("\nMulai perlindungan? (y/n): ").lower() != 'y':
        print(f"{RED}Operasi dibatalkan{RESET}")
        sys.exit(0)
    
    # Inisialisasi dan jalankan sistem proteksi
    shield = ZioleDDOSShield(config)
    shield.start_protection()