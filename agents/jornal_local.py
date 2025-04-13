import requests
from datetime import datetime
from bs4 import BeautifulSoup
import json
import os
import time
import hashlib

TELEGRAM_TOKEN = "xxxxxxxxx"
TELEGRAM_CHAT_ID = "xxxxxxxxx"

CACHE_FILE = "../news_cache.json"

class JornalLocalAgent:
    def __init__(self):
        self.cache = self._load_cache()
        self.name = "Jornal Local"
        self.url = "https://jornalocal.com.br/campinas/"
        self.selector = ".entry-title a"

    def _load_cache(self):
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    content = f.read()
                    if content.strip():
                        return set(json.loads(content))
            except json.JSONDecodeError:
                print("Erro ao decodificar o arquivo de cache. Criando um novo cache.")
        return set()

    def _save_cache(self):
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(list(self.cache), f, ensure_ascii=False, indent=4)

    def _compute_hash(self, title, link):
        value = (title + link).encode("utf-8")
        return hashlib.md5(value).hexdigest()

    def fetch_news(self):
        try:
            response = requests.get(self.url)
            soup = BeautifulSoup(response.text, "html.parser")
            posts = soup.select(self.selector)
            print(f"Títulos encontrados no scraping ({self.name}): {len(posts)}")
            news_list = []
            for post in posts:
                title_text = post.get_text(strip=True)
                link_tag = post.get("href")
                if not title_text or not link_tag:
                    continue
                if not link_tag.startswith("http"):
                    link_tag = self.url.rstrip("/") + link_tag
                news_item = {
                    "title": title_text,
                    "link": link_tag,
                    "source": self.name,
                    "date": datetime.now().strftime("%d/%m/%Y %H:%M")
                }
                news_hash = self._compute_hash(title_text, link_tag)
                if news_hash not in self.cache:
                    news_list.append(news_item)
                    self.cache.add(news_hash)
            return news_list
        except Exception as e:
            print(f"Erro no scraping ({self.name}): {str(e)}")
            return []

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
                requests.post(url, json=payload)
                print(f"Notícia enviada: {news['title']}")
            except Exception as e:
                print(f"Erro ao enviar: {str(e)}")

    def run(self):
        print(f"Iniciando busca por notícias do {self.name}...")
        news_list = self.fetch_news()
        if news_list:
            print(f"\n{len(news_list)} notícias novas encontradas!")
            self.send_telegram(news_list)
            self._save_cache()
        else:
            print(f"Nenhuma notícia nova detectada para {self.name}.")

def monitor():
    agent = JornalLocalAgent()
    while True:
        print("\nIniciando ciclo de monitoramento...")
        try:
            agent.run()
        except Exception as e:
            print(f"Erro durante a execução: {e}")
        print("Aguardando 5 minutos para o próximo ciclo...")
        time.sleep(300)

if __name__ == "__main__":
    monitor()