import requests
from bs4 import BeautifulSoup
import json
import os
import time
import hashlib

TELEGRAM_TOKEN = "xxxxxxx"
TELEGRAM_CHAT_ID = "xxxxxxx"

CACHE_FILE = "../news_cache_sampi.json"

class SampiCampinasAgent:
    def __init__(self):
        self.cache = self._load_cache()
        self.name = "SAMPI Campinas"
        self.url = "https://sampi.net.br/campinas"
    
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
    
    def _compute_hash(self, text):
        value = text.encode("utf-8")
        return hashlib.md5(value).hexdigest()
    
    def fetch_news(self):
        try:
            response = requests.get(self.url)
            soup = BeautifulSoup(response.text, "html.parser")
            news_blocks = soup.select(".container .row a.hoverActive")
            print(f"Notícias encontradas no scraping ({self.name}): {len(news_blocks)}")
            
            news_list = []
            for block in news_blocks:
                try:
                    # Extrair título
                    title_tag = block.find("h3")
                    title = title_tag.get_text(strip=True) if title_tag else "Título não encontrado"
                    
                    # Extrair link
                    link = block.get("href", "Link não encontrado")
                    
                    # Extrair categoria
                    category_tag = block.find("span")
                    category = category_tag.get_text(strip=True) if category_tag else "Categoria não encontrada"
                    
                    # Criar item de notícia (imagem removida)
                    news_item = {
                        "title": title,
                        "link": link,
                        "source": self.name,
                        "category": category
                    }
                    
                    # Verifica duplicação usando hash consistente
                    news_hash = self._compute_hash(title + link)
                    if news_hash not in self.cache:
                        news_list.append(news_item)
                        self.cache.add(news_hash)
                
                except Exception as e:
                    print(f"Erro ao extrair notícia: {str(e)}")
            
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
                f"📢 Categoria: {news['category']}\n"
                f"🔗 Link: {news['link']}\n"
                f"💬 Fonte: {news['source']}"
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
            
            # Temporizador: delay de 5 segundos entre envios
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

def monitor():
    agent = SampiCampinasAgent()
    
    while True:
        agent.run()
        print("\nAguardando 5 minutos para o próximo ciclo...")
        time.sleep(300)

if __name__ == "__main__":
    monitor()