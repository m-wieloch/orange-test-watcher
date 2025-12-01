#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from zoneinfo import ZoneInfo

# --- KONFIGURACJA ---

# Pobieramy produkt z bezpiecznych ustawień GitHuba (Secrets)
PRODUCT_URL = os.environ.get("PRODUCT_URL")

# Pobieramy webhook z bezpiecznych ustawień GitHuba (Secrets)
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def send_discord_alert():
    if not DISCORD_WEBHOOK_URL:
        print("Brak skonfigurowanego Webhooka!")
        return

    data = {
        "content": "@everyone 🚨 **PRODUKT DOSTĘPNY W ORANGE!** 🚨",
        "embeds": [{
            "title": "Kliknij, aby kupić!",
            "url": PRODUCT_URL,
            "color": 3066993,
            "fields": [
                {"name": "Status", "value": "Przycisk 'Do koszyka' wykryty."},
                {"name": "Czas (UTC)", "value": datetime.now(ZoneInfo("Europe/Warsaw")).strftime('%H:%M:%S')}
            ]
        }]
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=data)
        print("Powiadomienie wysłane.")
    except Exception as e:
        print(f"Błąd Discorda: {e}")

def init_driver():
    options = Options()
    # Te opcje są KRYTYCZNE dla GitHub Actions:
    options.add_argument("--headless") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    return driver

def check_availability():
    print("Uruchamiam sprawdzanie...")
    driver = init_driver()
    found = False
    
    try:
        driver.get(PRODUCT_URL)
        wait = WebDriverWait(driver, 20)
        
        # Szukamy przycisku
        buy_button = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//*[contains(text(), 'do koszyka') or contains(text(), 'Do koszyka')]")
        ))
        
        if buy_button.is_enabled():
            print("!!! SUKCES - PRZYCISK DOSTĘPNY !!!")
            found = True
        else:
            print("Przycisk jest, ale nieaktywny.")
            
    except Exception as e:
        print(f"Nie znaleziono przycisku. ({str(e)[:50]}...)")
    finally:
        driver.quit()

    if found:
        send_discord_alert()

if __name__ == "__main__":
    check_availability()