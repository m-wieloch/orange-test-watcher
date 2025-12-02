#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import requests
import json
from urllib.parse import urlparse
from zoneinfo import ZoneInfo
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Zmienne środowiskowe
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
PRODUCT_URL = os.environ.get("PRODUCT_URL")

def get_debug_info(driver, target_url):
    """Zbiera dane diagnostyczne do logów i Discorda."""
    try:
        current_h1 = driver.find_element(By.TAG_NAME, "h1").text
    except:
        current_h1 = "Brak nagłówka H1"

    return {
        "timestamp": datetime.now(ZoneInfo("Europe/Warsaw")).strftime('%Y-%m-%d %H:%M:%S'),
        "target_url_path": urlparse(target_url).path,
        "current_url": driver.current_url,
        "current_url_path": urlparse(driver.current_url).path,
        "page_title": driver.title,
        "h1_content": current_h1
    }

def is_valid_product_page(target_url, current_url):
    """
    Sprawdza, czy nadal jesteśmy na stronie produktu, porównując ścieżki URL.
    Nie wymaga wpisywania nazwy produktu na sztywno.
    """
    target_path = urlparse(target_url).path
    current_path = urlparse(current_url).path

    # Logika: Ścieżka docelowa powinna być zawarta w obecnej ścieżce.
    # Np. Target: /sklep/iphone-17
    #     Current: /sklep/iphone-17?variant=123 (OK)
    #     Current: /sklep/smartfony (BŁĄD - Redirect)
    
    # Usuwamy ewentualny trailing slash dla pewności
    return target_path.rstrip('/') in current_path.rstrip('/')

def send_discord_alert(debug_data):
    if not DISCORD_WEBHOOK_URL:
        print("LOG: Brak webhooka Discord!")
        return

    # Budujemy wiadomość z sekcją DEBUG
    embed_fields = [
        {"name": "Status", "value": "✅ Wykryto przycisk zakupu"},
        {"name": "Tytuł strony", "value": debug_data['page_title']},
        {"name": "Nagłówek H1", "value": debug_data['h1_content']},
        {"name": "Link bezpośredni", "value": debug_data['current_url']},
        {"name": "Czas (PL)", "value": debug_data['timestamp']}
    ]

    # Dodajemy sekcję techniczną dla Ciebie
    footer_text = f"Debug: Target Path: {debug_data['target_url_path']} | Current Path: {debug_data['current_url_path']}"

    data = {
        "content": "@everyone 🚨 **MOŻLIWY DROP!** (Weryfikacja URL pomyślna)",
        "embeds": [{
            "title": "Produkt dostępny!",
            "url": debug_data['current_url'],
            "color": 3066993, # Zielony
            "fields": embed_fields,
            "footer": {"text": footer_text}
        }]
    }
    
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=data)
        print("LOG: Powiadomienie wysłane pomyślnie.")
    except Exception as e:
        print(f"LOG: Błąd wysyłania do Discorda: {e}")

def init_driver():
    options = Options()
    options.add_argument("--headless") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    return driver

def check_availability():
    if not PRODUCT_URL:
        print("FATAL ERROR: Brak zmiennej PRODUCT_URL!")
        return

    print(f"LOG: Rozpoczynam sprawdzanie dla: {urlparse(PRODUCT_URL).path}")
    driver = init_driver()
    
    try:
        driver.get(PRODUCT_URL)
        time.sleep(5) # Czas na JS i przekierowania
        
        # Pobieramy pełne dane diagnostyczne
        debug_data = get_debug_info(driver, PRODUCT_URL)
        
        # 1. WERYFIKACJA URL (Bez hardcodowania)
        if not is_valid_product_page(PRODUCT_URL, driver.current_url):
            print("--- FALSE POSITIVE DETECTED (REDIRECT) ---")
            print(json.dumps(debug_data, indent=2, ensure_ascii=False))
            print("------------------------------------------")
            return

        # 2. Szukanie przycisku
        wait = WebDriverWait(driver, 15)
        buy_button = wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//button[contains(., 'do koszyka') or contains(., 'Do koszyka')]")
        ))
        
        if buy_button.is_enabled():
            print("LOG: SUKCES! Przycisk znaleziony i aktywny.")
            send_discord_alert(debug_data)
        else:
            print("LOG: Przycisk widoczny, ale nieaktywny (disabled).")
            
    except Exception as e:
        # Ten log w konsoli Actions pozwoli Ci zrozumieć, co poszło nie tak
        print(f"LOG: Produkt niedostępny lub błąd. Szczegóły: {str(e)[:100]}")
        # Jeśli chcesz, możesz tu odkomentować printowanie debug_data przy błędzie:
        # print("DEBUG STATE:", get_debug_info(driver, PRODUCT_URL))
        
    finally:
        driver.quit()

if __name__ == "__main__":
    check_availability()