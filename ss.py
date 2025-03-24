import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import socks
import socket
from bs4 import BeautifulSoup
import random
import time

def get_free_proxies():
    """Получает список свежих прокси с проверенных сайтов"""
    print("\n[+] Получаем свежие прокси...")
    
    proxy_sources = [
        "https://www.sslproxies.org/",
        "https://free-proxy-list.net/",
        "https://hidemy.name/ru/proxy-list/"
    ]
    
    proxies = []
    
    for url in proxy_sources:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            if "sslproxies" in url or "free-proxy-list" in url:
                table = soup.find('table', {'id': 'proxylisttable'})
                for row in table.tbody.find_all('tr'):
                    cols = row.find_all('td')
                    if cols[4].text.strip() == 'elite proxy':
                        proxies.append({
                            'ip': cols[0].text.strip(),
                            'port': cols[1].text.strip(),
                            'type': 'https' if 'yes' in cols[6].text.strip().lower() else 'http'
                        })
            
            elif "hidemy.name" in url:
                table = soup.find('table')
                for row in table.find_all('tr')[1:]:
                    cols = row.find_all('td')
                    proxies.append({
                        'ip': cols[0].text.strip(),
                        'port': cols[1].text.strip(),
                        'type': cols[4].text.strip().lower()
                    })
            
            print(f"[+] Найдено {len(proxies)} прокси с {url}")
            
        except Exception as e:
            print(f"[-] Ошибка при парсинге {url}: {e}")
            continue
    
    return proxies

def test_proxy(proxy, test_url="https://www.google.com", timeout=5):
    """Проверяет работоспособность прокси"""
    try:
        proxies = {
            "http": f"{proxy['type']}://{proxy['ip']}:{proxy['port']}",
            "https": f"{proxy['type']}://{proxy['ip']}:{proxy['port']}"
        }
        response = requests.get(test_url, proxies=proxies, timeout=timeout)
        if response.status_code == 200:
            return True
    except:
        return False
    return False

def setup_proxy(proxy):
    """Настраивает прокси для всех соединений"""
    proxy_type_map = {
        'http': socks.HTTP,
        'https': socks.HTTP,
        'socks4': socks.SOCKS4,
        'socks5': socks.SOCKS5
    }
    
    proxy_type = proxy_type_map.get(proxy['type'].lower(), socks.SOCKS5)
    
    try:
        socks.set_default_proxy(
            proxy_type=proxy_type,
            addr=proxy['ip'],
            port=int(proxy['port'])
        )
        socket.socket = socks.socksocket
        return True
    except Exception as e:
        print(f"[-] Ошибка настройки прокси: {e}")
        return False

def send_email(sender_email, sender_password, recipient_email, subject, message):
    """Отправляет письмо через Gmail"""
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        
        return True, "Письмо успешно отправлено!"
    
    except Exception as e:
        return False, f"Ошибка при отправке письма: {e}"

def main():
    print("=== Gmail Sender with Auto Proxy ===")
    print("Автоматически находит и проверяет прокси перед отправкой\n")
    
    # Получаем список прокси
    proxies = get_free_proxies()
    if not proxies:
        print("[-] Не удалось получить прокси. Попробуйте позже.")
        return
    
    # Вводим данные для письма
    print("\n[+] Введите данные для отправки:")
    sender_email = input("Ваш Gmail: ").strip()
    sender_password = input("Пароль/App Password: ").strip()
    recipient_email = input("Получатель: ").strip()
    subject = input("Тема: ").strip()
    print("Текст письма (Ctrl+D для завершения):")
    message = []
    while True:
        try:
            line = input()
            message.append(line)
        except EOFError:
            break
    message = "\n".join(message)
    
    # Пытаемся отправить через случайные прокси, пока не получится
    max_attempts = 5
    for attempt in range(1, max_attempts + 1):
        print(f"\n[+] Попытка {attempt}/{max_attempts}")
        
        # Выбираем случайный прокси
        proxy = random.choice(proxies)
        print(f"Выбран прокси: {proxy['ip']}:{proxy['port']} ({proxy['type']})")
        
        # Проверяем прокси
        if not test_proxy(proxy):
            print("[-] Прокси не работает, пробуем другой...")
            proxies.remove(proxy)
            if not proxies:
                print("[-] Закончились рабочие прокси")
                return
            continue
        
        # Настраиваем прокси
        if not setup_proxy(proxy):
            continue
        
        # Пытаемся отправить письмо
        success, result = send_email(
            sender_email, sender_password, 
            recipient_email, subject, message
        )
        
        print(result)
        if success:
            break
        
        # Если не получилось, ждем перед следующей попыткой
        if attempt < max_attempts:
            print(f"Ждем 5 секунд перед следующей попыткой...")
            time.sleep(5)

if __name__ == "__main__":
    main()
