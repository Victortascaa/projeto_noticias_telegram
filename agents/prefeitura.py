from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os
import time
import requests
import hashlib

TELEGRAM_TOKEN = "xxxxxxx"
TELEGRAM_CHAT_ID = "xxxxxxx"

CACHE_FILE = "../news_cache.json"

class PrefeituraCampinasAgent:
    def __init__(self):
        self.cache = self._load_cache()
        self.name = "Prefeitura de Campinas"
        self.url = "https://campinas.sp.gov.br/mais-noticias/"
    
    def _load_cache(self):
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    content = f.read()
                    if content.strip():
                        return set(json.loads(content))
            except json.JSONDecodeError:
                print("Erro no cache. Criando novo arquivo...")
        return set()

    def _save_cache(self):
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(list(self.cache), f, ensure_ascii=False, indent=4)

    def _compute_hash(self, text):
        value = text.encode("utf-8")
        return hashlib.md5(value).hexdigest()

    def fetch_news(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(self.url)
        
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.mt-5.divisor.ng-star-inserted"))
            )
            
            news_blocks = driver.find_elements(By.CSS_SELECTOR, "li.mt-5.divisor.ng-star-inserted")
            print(f"Notícias encontradas no scraping ({self.name}): {len(news_blocks)}")
            
            news_list = []
            for block in news_blocks:
                try:
                    title = block.find_element(By.TAG_NAME, "p").text
                    link = block.find_element(By.TAG_NAME, "a").get_attribute("href")
                    date = block.find_element(By.CSS_SELECTOR, "span.block.color-helper").text
                    news_item = {
                        "title": title,
                        "link": link,
                        "source": self.name,
                        "date": date
                    }
                    news_hash = self._compute_hash(title + link)
                    if news_hash not in self.cache:
                        news_list.append(news_item)
                        self.cache.add(news_hash)
                except Exception as e:
                    print(f"Erro ao extrair notícia: {str(e)}")
            return news_list
        finally:
            driver.quit()

    def send_telegram(self, news_list):
        if not news_list:
            print(f"Nenhuma notícia nova encontrada para {self.name}.")
            return
        
        for news in news_list:
            message = (
                f"📌 <b>{news['title']}</b>\n"
                f"📅 Data: {news['date']}\n"
                f"🔗 Link: {news['link']}\n"
                f"📢 Fonte: {news['source']}"
            )
            
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "HTML"
            }
            
            try:
                response = requests.post(url, json=payload)
                if response.status_code == 200:
                    print(f"Notícia enviada: {news['title']}")
                else:
                    print(f"Falha ao enviar notícia: {response.text}")
            except Exception as e:
                print(f"Erro ao enviar: {str(e)}")
            
            time.sleep(5)

    def run(self):
        print(f"Iniciando busca por notícias do {self.name}...")
        news_list = self.fetch_news()
        
        if news_list:
            print(f"\n{len(news_list)} notícias novas encontradas!")
            self.send_telegram(news_list)
            self._save_cache()
        else:
            print(f"Nenhuma notícia nova detectada para {self.name}.")

if __name__ == "__main__":
    agent = PrefeituraCampinasAgent()
    agent.run()