import requests
from datetime import datetime
from bs4 import BeautifulSoup
import feedparser
import json
import os
import time
import hashlib

TELEGRAM_TOKEN = "xxxxxxxxxx"
TELEGRAM_CHAT_ID = "xxxxxxx"

CACHE_FILE = "../news_cache.json"

class G1Agent:
    def __init__(self):
        self.cache = self._load_cache()
        self.news_sources = [
            {
                "name": "G1 Campinas (RSS)",
                "url": "https://g1.globo.com/rss/globo/campinas/",
                "type": "rss"
            },
            {
                "name": "G1 Nacional (RSS)",
                "url": "https://g1.globo.com/rss/globo/",
                "type": "rss"
            },
            {
                "name": "G1 Campinas (Site)",
                "url": "https://g1.globo.com/sp/campinas-regiao/",
                "type": "scraping",
                "selector": ".feed-post-body"
            }
        ]

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
        all_news = []
        today = datetime.now().date()
        for source in self.news_sources:
            print(f"\nVerificando fonte: {source['name']}")
            if source["type"] == "rss":
                all_news += self._fetch_rss(source, today)
            elif source["type"] == "scraping":
                all_news += self._fetch_scraping(source, today)
        return all_news

    def _fetch_rss(self, source, today):
        try:
            feed = feedparser.parse(source["url"])
            print(f"Entradas encontradas no RSS ({source['name']}): {len(feed.entries)}")
            news_list = []
            for entry in feed.entries:
                pub_date = self._parse_date(entry.get("published", ""))
                if pub_date.date() != today:
                    print(f"Notícia ignorada (data inválida): {entry.title}")
                    continue
                news_item = {
                    "title": entry.title,
                    "link": entry.link,
                    "source": source["name"],
                    "date": pub_date.strftime("%d/%m/%Y %H:%M")
                }
                news_hash = self._compute_hash(news_item["title"], news_item["link"])
                if news_hash not in self.cache:
                    news_list.append(news_item)
                    self.cache.add(news_hash)
            return news_list
        except Exception as e:
            print(f"Erro no RSS ({source['name']}): {str(e)}")
            return []

    def _fetch_scraping(self, source, today):
        try:
            response = requests.get(source["url"])
            soup = BeautifulSoup(response.text, "html.parser")
            posts = soup.select(source["selector"])
            news_list = []
            for post in posts:
                title_tag = post.select_one(".feed-post-body-title")
                time_tag = post.select_one(".feed-post-datetime")
                if not title_tag or not time_tag:
                    continue
                title = title_tag.get_text(strip=True)
                link = post.select_one("a")["href"]
                pub_date_str = time_tag.get_text(strip=True)
                pub_date = self._parse_date(pub_date_str)
                if "hora" in pub_date_str.lower() or pub_date.date() == today:
                    news_item = {
                        "title": title,
                        "link": link,
                        "source": source["name"],
                        "date": pub_date.strftime("%d/%m/%Y %H:%M")
                    }
                    news_hash = self._compute_hash(title, link)
                    if news_hash not in self.cache:
                        news_list.append(news_item)
                        self.cache.add(news_hash)
            return news_list
        except Exception as e:
            print(f"Erro no scraping ({source['name']}): {str(e)}")
            return []

    def _parse_date(self, date_str):
        try:
            formats = [
                "%a, %d %b %Y %H:%M:%S %z",
                "%d/%m/%Y %Hh%M",
                "%Hh%M"
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except:
                    continue
            return datetime.now()
        except:
            return datetime.now()

    def send_telegram(self, news_list):
        if not news_list:
            print("Nenhuma notícia nova encontrada.")
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
        print("Iniciando busca por notícias do G1...")
        news_list = self.fetch_news()
        if news_list:
            print(f"\n{len(news_list)} notícias novas encontradas!")
            self.send_telegram(news_list)
            self._save_cache()
        else:
            print("Nenhuma notícia nova detectada.")

def monitor():
    agent = G1Agent()
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