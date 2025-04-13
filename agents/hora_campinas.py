import requests
from datetime import datetime
from bs4 import BeautifulSoup
import json
import os
import time
import hashlib

TELEGRAM_TOKEN = "xxxxxx"
TELEGRAM_CHAT_ID = "xxxxxxxx"

CACHE_FILE = "../news_cache.json"

class HoraCampinasAgent:
    def __init__(self):
        self.cache = self._load_cache()
        self.name = "Hora Campinas"
        self.url = "https://horacampinas.com.br/ultimas-noticias/"

    def _load_cache(self):
        """Carrega o cache de notícias do arquivo JSON"""
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    content = f.read()
                    if content.strip():  # Verifica se o arquivo não está vazio
                        return set(json.loads(content))
            except json.JSONDecodeError:
                print("Erro ao decodificar o arquivo de cache. Criando um novo cache.")
        return set()

    def _save_cache(self):
        """Salva o cache de notícias no arquivo JSON"""
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(list(self.cache), f, ensure_ascii=False, indent=4)

    def _compute_hash(self, title, link):
        """Gera um hash consistente usando titulo e link"""
        value = (title + link).encode("utf-8")
        return hashlib.md5(value).hexdigest()

    def fetch_news(self):
        try:
            response = requests.get(self.url)
            soup = BeautifulSoup(response.text, "html.parser")
            articles = soup.select("article.jeg_post")
            print(f"Artigos encontrados no scraping ({self.name}): {len(articles)}")
            
            news_list = []
            for article in articles:
                title_tag = article.select_one("h3.jeg_post_title a")
                if not title_tag:
                    continue
                title = title_tag.get_text(strip=True)
                link = title_tag.get("href")
                
                summary_tag = article.select_one(".jeg_post_excerpt p")
                summary = summary_tag.get_text(strip=True) if summary_tag else "Sem resumo disponível."
                
                date_tag = article.select_one(".jeg_meta_date a")
                date_str = date_tag.get_text(strip=True) if date_tag else "Data não disponível."
                
                news_item = {
                    "title": title,
                    "link": link,
                    "summary": summary,
                    "date": date_str,
                    "source": self.name,
                }
                
                news_hash = self._compute_hash(title, link)
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
    agent = HoraCampinasAgent()
    while True:
        print("\nIniciando ciclo de monitoramento...")
        try:
            agent.run()
        except Exception as e:
            print(f"Erro durante a execução: {e}")
        print("Aguardando 5 minutos para o próximo ciclo...")
        time.sleep(300)  # Espera 5 minutos

if __name__ == "__main__":
    monitor()