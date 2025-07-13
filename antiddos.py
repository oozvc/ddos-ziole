#!/usr/bin/env python3
"""
██████╗ ██╗  ██╗██╗███╗   ███╗ █████╗ ███╗   ██╗████████╗ █████╗ ██████╗  ██████╗ 
██╔══██╗██║  ██║██║████╗ ████║██╔══██╗████╗  ██║╚══██╔══╝██╔══██╗██╔══██╗██╔═══██╗
██████╔╝███████║██║██╔████╔██║███████║██╔██╗ ██║   ██║   ███████║██████╔╝██║   ██║
██╔═══╝ ██╔══██║██║██║╚██╔╝██║██╔══██║██║╚██╗██║   ██║   ██╔══██║██╔══██╗██║   ██║
██║     ██║  ██║██║██║ ╚═╝ ██║██║  ██║██║ ╚████║   ██║   ██║  ██║██║  ██║╚██████╔╝
╚═╝     ╚═╝  ╚═╝╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ 
"""
import os
import sys
import time
import random
import secrets
import subprocess
import requests

# ===== KONSTANTA WARNA =====
RED = "\033[91m"
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
RESET = "\033[0m"
BANNER = f"""
{CYAN}
╔╦╗┬ ┬┌─┐┌┬┐┌─┐┌─┐┌─┐┬─┐  ╔╗ ┬ ┬┌─┐┬ ┬┌─┐┬─┐┌┬┐
 ║ ├─┤├┤  │ ├┤ └─┐├┤ ├┬┘  ╠╩╗└┬┘├─┘│ │├┤ ├┬┘ │ 
 ╩ ┴ ┴└─┘ ┴ └─┘└─┘└─┘┴└─  ╚═╝ ┴ ┴  └─┘└─┘┴└─ ┴ 
Bhimantara Cyber Defense System v9.0
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

# ===== SISTEM KONFIGURASI INTERAKTIF =====
def get_user_config():
    """Dapatkan konfigurasi langsung dari pengguna"""
    show_banner()
    config = {}
    
    print(f"{GREEN}⚙️ KONFIGURASI DASAR{RESET}")
    print("="*50)
    config['protected_ip'] = input("Masukkan IP server yang dilindungi: ").strip()
    
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
    
    print(f"\n{RED}🚨 THRESHOLD DETEKSI SERANGAN{RESET}")
    print("="*50)
    print("Atur batas deteksi serangan (permintaan/detik)")
    config['thresholds'] = {
        'syn': int(input("Threshold SYN flood (default 5000): ").strip() or "5000"),
        'udp': int(input("Threshold UDP flood (default 10000): ").strip() or "10000"),
        'icmp': int(input("Threshold ICMP flood (default 2000): ").strip() or "2000"),
        'http': int(input("Threshold HTTP flood (default 3000): ").strip() or "3000"),
    }
    
    return config

# ===== SISTEM PROTEKSI UTAMA =====
class BhimantaraShield:
    def __init__(self, config):
        self.config = config
        self.current_port = random.randint(*config['mtd_port_range'])
        self.last_port_change = time.time()
        self.protection_active = True
        self.blocked_ips = set()
        print(f"{GREEN}[🛡️] Perlindungan aktif untuk IP: {config['protected_ip']}{RESET}")

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
        run_command("iptables -A INPUT -p tcp --syn -m limit --limit 1/s --limit-burst 3 -j ACCEPT")
        run_command("iptables -A INPUT -p tcp --syn -j DROP")
        
        # Kernel hardening
        run_command("sysctl -w net.ipv4.tcp_syncookies=1")
        run_command("sysctl -w net.ipv4.icmp_echo_ignore_all=1")
        
        print(f"{GREEN}[✅] Firewall diinisialisasi!{RESET}")
    
    def update_port_redirect(self):
        """Update redirect port di firewall"""
        run_command(f"iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port {self.current_port}")
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
        # Dalam implementasi nyata, ini akan menggunakan packet capture
        return {
            'syn': random.randint(100, 5000),
            'udp': random.randint(50, 3000),
            'icmp': random.randint(20, 1000),
            'http': random.randint(200, 4000)
        }
    
    def check_attacks(self, traffic):
        """Periksa apakah ada serangan berdasarkan traffic"""
        for attack_type, rate in traffic.items():
            threshold = self.config['thresholds'].get(attack_type, 1000)
            if rate > threshold:
                self.handle_attack(attack_type, rate)
                return True
        return False
    
    def handle_attack(self, attack_type, rate):
        """Tangani serangan yang terdeteksi"""
        print(f"{RED}[🚨] SERANGAN {attack_type.upper()} TERDETEKSI! Rate: {rate}/s{RESET}")
        
        # 1. Blokir sementara traffic mencurigakan
        protocol = 'tcp' if attack_type in ['syn', 'http'] else 'udp'
        run_command(f"iptables -A INPUT -p {protocol} -m limit --limit 10/s -j ACCEPT")
        run_command(f"iptables -A INPUT -p {protocol} -j DROP")
        
        # 2. Notifikasi
        self.send_alert(f"Serangan {attack_type} terdeteksi - Rate {rate}/s")
        
        # 3. Aktifkan Cloudflare Under Attack Mode jika tersedia
        if self.config.get('cloudflare_api_key') and attack_type == 'http':
            self.enable_captcha()
    
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
    
    def show_status(self, traffic):
        """Tampilkan status sistem"""
        clear_screen()
        print(BANNER)
        print(f"{GREEN}🛡️ STATUS PERLINDUNGAN{RESET}")
        print("="*50)
        print(f"Protected IP     : {self.config['protected_ip']}")
        print(f"Current Port     : {self.current_port}")
        print(f"Next Port Change : {int(self.config['port_hop_interval'] - (time.time() - self.last_port_change))}s")
        print(f"Blocked IPs      : {len(self.blocked_ips)}")
        print("\n" + f"{YELLOW}📊 TRAFFIC MONITOR{RESET}")
        print("="*50)
        for attack, rate in traffic.items():
            threshold = self.config['thresholds'].get(attack, 1000)
            status = f"{RED}ATTACK!{RESET}" if rate > threshold else f"{GREEN}Normal{RESET}"
            print(f"{attack.upper().ljust(8)}: {str(rate).ljust(8)}/s  [Threshold: {threshold}] - {status}")
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
                self.show_status(traffic)
                
                # Tunggu hingga refresh berikutnya
                time.sleep(2)
                
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
        print(f"{GREEN}[✅] Sistem dihentikan dengan aman!{RESET}")

# ===== EKSEKUSI UTAMA =====
if __name__ == "__main__":
    if not is_root():
        print(f"{RED}ERROR: Skrip harus dijalankan sebagai root!{RESET}")
        print("Gunakan: sudo python3 bhimantara_antiddos.py")
        sys.exit(1)
    
    # Dapatkan konfigurasi dari pengguna
    config = get_user_config()
    
    # Konfirmasi konfigurasi
    clear_screen()
    print(BANNER)
    print(f"\n{GREEN}⚙️ KONFIGURASI YANG DIPILIH{RESET}")
    print("="*50)
    print(f"Protected IP    : {config['protected_ip']}")
    print(f"Port Range      : {config['mtd_port_range'][0]}-{config['mtd_port_range'][1]}")
    print(f"Port Hop Interval: {config['port_hop_interval']}s")
    print(f"SYN Threshold   : {config['thresholds']['syn']}/s")
    print(f"UDP Threshold   : {config['thresholds']['udp']}/s")
    print(f"ICMP Threshold  : {config['thresholds']['icmp']}/s")
    print(f"HTTP Threshold  : {config['thresholds']['http']}/s")
    
    if input("\nMulai perlindungan? (y/n): ").lower() != 'y':
        print(f"{RED}Operasi dibatalkan{RESET}")
        sys.exit(0)
    
    # Inisialisasi dan jalankan sistem proteksi
    shield = BhimantaraShield(config)
    shield.start_protection()