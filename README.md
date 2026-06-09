# PasticcereBot

Bot Telegram con AI locale (Ollama) per ricette di pasticceria.
Risponde a domande sulle ricette usando un sistema RAG su file di testo locali.

## Funzionalità

- Risponde a domande su oltre 50 ricette di pasticceria
- Memoria della conversazione per domande di follow-up
- Streaming della risposta in tempo reale
- `/lista` — tutte le ricette disponibili
- `/cerca <ingrediente>` — ricette per ingrediente
- `/reset` — cancella la memoria della chat
- Notifica Telegram quando il bot si spegne
- Tutto gira in locale, nessun dato inviato a cloud

## Requisiti

- Python 3.10+
- [Ollama](https://ollama.ai) installato e in esecuzione
- Un bot Telegram (creato con [@BotFather](https://t.me/botfather))

## Installazione

1. Clona il repository
   ```bash
   git clone https://github.com/tuo-username/pasticcerebot.git
   cd pasticcerebot
   ```

2. Installa le dipendenze
   ```bash
   python -m pip install -r requirements.txt
   ```

3. Configura il token Telegram
   ```bash
   cp .env.example .env
   # modifica .env e inserisci il tuo token
   ```

4. Scarica il modello Ollama
   ```bash
   ollama pull llama3.2
   ```

5. Avvia Ollama
   ```bash
   ollama serve
   ```

6. Avvia il bot
   ```bash
   python bot.py
   ```

## Struttura del progetto

```
├── bot.py           # Entry point — gestisce i messaggi Telegram
├── agent.py         # Logica agente — RAG + Ollama + memoria
├── rag.py           # Ricerca nei file di testo
├── config.py        # Configurazione
├── data/
│   └── ricette/     # File .txt con le ricette (aggiungine quanti vuoi)
├── .env.example     # Template configurazione
└── requirements.txt
```

## Aggiungere ricette

Basta creare un nuovo file `.txt` in `data/ricette/` con il nome della ricetta
(es. `torta_cioccolato.txt`). Il bot la riconosce automaticamente senza riavvio.

## Tecnologie

- [python-telegram-bot](https://python-telegram-bot.org/)
- [Ollama](https://ollama.ai)
- RAG con similarità coseno (senza database vettoriali)
