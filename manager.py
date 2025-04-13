import os
import json
import time
import logging
from datetime import datetime
from agents.g1_agent import G1Agent
from agents.hora_campinas import HoraCampinasAgent
from agents.prefeitura import PrefeituraCampinasAgent
from agents.sampi import SampiCampinasAgent
from agents.jornal_local import JornalLocalAgent
from telegram import Bot # type: ignore

CACHE_FILE = "news_cache.json"
LOG_FILE = "logs.json"
TELEGRAM_BOT_TOKEN = "xxxxxxxxxx"
TELEGRAM_CHAT_ID = "xxxxxxxx"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                if content.strip():
                    return set(json.loads(content))
        except json.JSONDecodeError:
            logging.error("Erro ao decodificar o arquivo de cache. Criando um novo cache.")
    return set()

def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(list(cache), f, ensure_ascii=False, indent=4)

def update_logs(agent_name, news_sent):
    logs = {}
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            logs = {}
    logs[agent_name] = {
        "news_sent": news_sent,
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=4)

def send_to_telegram(news):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    message = (
        f"📰 *Nova notícia encontrada!*\n\n"
        f"📌 *Título:* {news['title']}\n"
        f"🔗 *Link:* [Clique aqui]({news['link']})\n"
        f"📅 *Data:* {news.get('date', 'Não informada')}\n"
        f"📸 *Imagem:* {news.get('image', 'Sem imagem')}"
    )
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="Markdown")

def monitor():
    global_cache = load_cache()
    agents = [
        G1Agent(),
        HoraCampinasAgent(),
        PrefeituraCampinasAgent(),
        SampiCampinasAgent(),
        JornalLocalAgent()
    ]
    while True:
        logging.info("Iniciando ciclo de monitoramento...")
        for agent in agents:
            try:
                logging.info(f"Iniciando agente {agent.name}...")
                news_list = agent.run()
                if not isinstance(news_list, list):
                    logging.error(f"Erro: O agente {agent.name} retornou um valor inválido: {news_list}")
                    continue
                new_news = []
                for news in news_list:
                    news_hash = hash(news["title"] + news["link"])
                    if news_hash not in global_cache:
                        new_news.append(news)
                        global_cache.add(news_hash)
                if new_news:
                    logging.info(f"Agente {agent.name} encontrou {len(new_news)} notícias novas.")
                    for news in new_news:
                        logging.info(f"Notícia encontrada: {news['title']}")
                        send_to_telegram(news)
                        time.sleep(5)
                    save_cache(global_cache)
                    update_logs(agent.name, len(new_news))
                else:
                    logging.info(f"Agente {agent.name} não encontrou novas notícias.")
            except Exception as e:
                logging.error(f"Erro ao executar o agente {agent.name}: {str(e)}")
        logging.info("Aguardando 5 minutos para o próximo ciclo...")
        time.sleep(300)

if __name__ == "__main__":
    monitor()