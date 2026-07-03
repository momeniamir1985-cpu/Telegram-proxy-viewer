import requests
import re
import time
import random
import os
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor

HTTP_FILE = 'http_proxies.txt'
SOCKS4_FILE = 'socks4_proxies.txt'
SOCKS5_FILE = 'socks5_proxies.txt'

def load_proxies_from_file(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

def save_proxies_to_file(proxies, filename):
    with open(filename, 'w') as f:
        for proxy in proxies:
            f.write(proxy + '\n')
    print(f"✅ {len(proxies)} پروکسی در {filename} ذخیره شد.")

def scrape_clean_proxies():
    sources = {
        'http': [
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
        ],
        'socks4': [
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4&timeout=10000&country=all"
        ],
        'socks5': [
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=10000&country=all"
        ]
    }
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'}
    extracted_data = {'http': [], 'socks4': [], 'socks5': []}
    proxy_pattern = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}:[0-9]{2,5}\b')

    for protocol, urls in sources.items():
        for url in urls:
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    found_proxies = proxy_pattern.findall(response.text)
                    extracted_data[protocol].extend(found_proxies)
            except requests.RequestException as e:
                print(f"آدرس {url} در دسترس نبود. خطا: {e}")
                
        extracted_data[protocol] = list(set(extracted_data[protocol]))
        print(f"پروتکل {protocol}: تعداد {len(extracted_data[protocol])} پروکسی یافت شد.")
        
    return extracted_data

def verify_network_node(proxy, protocol):
    proxies = {
        'http': f'{protocol}://{proxy}',
        'https': f'{protocol}://{proxy}'
    }
    try:
        response = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=5)
        if response.status_code == 200:
            return proxy, True
    except:
        pass
    return proxy, False

def parallel_checker(proxy_list, protocol, max_threads=50):
    working_proxies = []
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(verify_network_node, p, protocol) for p in proxy_list]
        for future in futures:
            proxy, is_working = future.result()
            if is_working:
                working_proxies.append(proxy)
    return working_proxies

def test_and_view(proxy, post_url, proxy_type='http'):
    try:
        if proxy_type == 'http':
            proxies = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
        elif proxy_type == 'socks4':
            proxies = {
                'http': f'socks4://{proxy}',
                'https': f'socks4://{proxy}'
            }
        else:
            proxies = {
                'http': f'socks5://{proxy}',
                'https': f'socks5://{proxy}'
            }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
        
        response = requests.get(post_url, proxies=proxies, headers=headers, timeout=20)
        
        if response.status_code == 200:
            print(f"✅ بازدید موفق با {proxy_type} proxy: {proxy}")
            return True
        else:
            print(f"❌ وضعیت {response.status_code} برای {proxy}")
            return False
            
    except Exception as e:
        return False

def main():
    print("🚀 اسکریپت آموزشی افزایش بازدید تلگرام با پروکسی")
    print("=" * 60)
    
    post_url = input("لینک پست تلگرام را وارد کنید (مثال: https://t.me/channelname/123): ").strip()
    
    if not post_url.startswith('http'):
        post_url = 'https://' + post_url
    
    parsed = urlparse(post_url)
    if 't.me' not in parsed.netloc:
        print("⚠️ لینک معتبر تلگرام وارد کنید!")
        return
    
    print(f"🎯 هدف: {post_url}")
    print("🔄 شروع جمع‌آوری و تست پروکسی‌ها...\n")
    
    visit_count = 0
    iteration = 0
    
    while True:
        iteration += 1
        print(f"\n🔄 چرخه {iteration} - جمع‌آوری پروکسی‌های جدید...")
        
        proxies_data = scrape_clean_proxies()
        
        save_proxies_to_file(proxies_data['http'], HTTP_FILE)
        save_proxies_to_file(proxies_data['socks4'], SOCKS4_FILE)
        save_proxies_to_file(proxies_data['socks5'], SOCKS5_FILE)
        
        http_proxies = load_proxies_from_file(HTTP_FILE)
        socks4_proxies = load_proxies_from_file(SOCKS4_FILE)
        socks5_proxies = load_proxies_from_file(SOCKS5_FILE)
        
        total_proxies = len(http_proxies) + len(socks4_proxies) + len(socks5_proxies)
        print(f"📊 کل پروکسی‌ها: {total_proxies} (HTTP: {len(http_proxies)}, SOCKS4: {len(socks4_proxies)}, SOCKS5: {len(socks5_proxies)})")
        
        print("🔍 شروع تست و بازدید با روش موازی...")
        
        if http_proxies:
            print("🔄 تست پروکسی‌های HTTP...")
            working_http = parallel_checker(http_proxies[:500], 'http')
            print(f"✅ {len(working_http)} پروکسی HTTP معتبر یافت شد.")
            
            for proxy in working_http:
                if test_and_view(proxy, post_url, 'http'):
                    visit_count += 1
                time.sleep(random.uniform(0.5, 1.5))
        
        if socks4_proxies:
            print("🔄 تست پروکسی‌های SOCKS4...")
            working_socks4 = parallel_checker(socks4_proxies[:300], 'socks4')
            print(f"✅ {len(working_socks4)} پروکسی SOCKS4 معتبر یافت شد.")
            
            for proxy in working_socks4:
                if test_and_view(proxy, post_url, 'socks4'):
                    visit_count += 1
                time.sleep(random.uniform(1, 2.5))
        
        if socks5_proxies:
            print("🔄 تست پروکسی‌های SOCKS5...")
            working_socks5 = parallel_checker(socks5_proxies[:300], 'socks5')
            print(f"✅ {len(working_socks5)} پروکسی SOCKS5 معتبر یافت شد.")
            
            for proxy in working_socks5:
                if test_and_view(proxy, post_url, 'socks5'):
                    visit_count += 1
                time.sleep(random.uniform(1, 2.5))
        
        print(f"\n📈 بازدیدهای موفق تا حالا: {visit_count}")
        print("⏳ استراحت ۳۰ ثانیه قبل از چرخه بعدی...\n")
        time.sleep(30)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 اسکریپت متوقف شد. بازدیدها: ", visit_count)
    except Exception as e:
        print(f"خطای کلی: {e}")