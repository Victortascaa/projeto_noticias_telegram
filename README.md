# Sistema de Monitoramento de Notícias

<p align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/1200px-Python-logo-notext.svg.png" alt="Python Logo" width="150"/>
</p>

Um sistema automatizado de coleta e monitoramento de notícias desenvolvido para simplificar o acompanhamento de informações relevantes para rádios FM. Este projeto utiliza **web scraping**, **modularidade** e **integração com Telegram** para entregar notícias em tempo real.

---

## 📌 Índice

- [Funcionalidades](#funcionalidades)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Como Usar](#como-usar)
- [Contribuições](#contribuições)
- [Licença](#licença)

---

## 🚀 Funcionalidades

- Coleta automática de notícias de múltiplas fontes (ex.: G1, Prefeitura de Campinas).
- Sistema modular: cada fonte de notícias tem seu próprio coletor.
- Integração com Telegram para entrega das notícias formatadas em tempo real.
- Cache para evitar duplicação de notícias.
- Interface web simples para monitorar o status dos agentes em tempo real (usando Flask).
- Hospedagem em cloud (VPS) para garantir disponibilidade 24/7.

---

## 💻 Tecnologias Utilizadas

- **Python**: Linguagem principal.
- **BeautifulSoup**: Para web scraping.
- **Requests**: Para requisições HTTP.
- **Flask**: Para criar uma interface web de monitoramento.
- **Telegram Bot API**: Para envio de notícias ao grupo do Telegram.
- **Selenium**: Para lidar com sites dinâmicos (se necessário).
- **Virtualenv**: Para gerenciar dependências em ambiente virtual.
- **Systemd**: Para execução contínua na VPS.

---

### 🛠️ Instalação

#### Pré-requisitos

- Python 3.x instalado.
- Acesso a uma VPS ou servidor local.
- Um bot do Telegram configurado (obtenha o token no [BotFather](https://core.telegram.org/bots#botfather)).

#### Passo a Passo

1. Clone o repositório:
```bash
    git clone https://github.com/seu-usuario/nome-do-repositorio.git
    cd nome-do-repositorio
```
2. Crie e ative um ambiente virtual:
```
    python3 -m venv venv
    source venv/bin/activate
```
3. Instale as dependências:
```
    pip install -r requirements.txt
```
4. Configure as variáveis de ambiente:
   Crie um arquivo .env na raiz do projeto com as seguintes variáveis:
```
    TELEGRAM_BOT_TOKEN=SEU_TOKEN_DO_TELEGRAM
    TELEGRAM_CHAT_ID=ID_DO_GRUPO_OU_CANAL
```
Substitua os valores pelos dados do seu bot e grupo do Telegram.

🎯 Como Usar
1. Execute o script principal:
```
    python manager.py
```
2. Acesse a interface de monitoramento:
   Abra o navegador e acesse http://<IP_DA_VPS>:5000/status.
   
4. Receba notícias no Telegram:
  As notícias serão enviadas automaticamente ao grupo configurado.
```
Esse bloco contém todas as instruções necessárias para configurar e usar o projeto, desde a criação do ambiente virtual até a execução do sistema. Basta copiar e colar diretamente no seu `README.md`. Se precisar de mais ajustes ou quiser adicionar algo específico, estou à disposição! 😊
```
