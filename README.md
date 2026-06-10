# PasticcereBot

Bot Telegram per ricette di pasticceria con LLM locale. Tutto gira sul tuo PC: nessun dato inviato a cloud, nessuna API key, nessun costo.

---

## Come funziona

L'utente manda un messaggio su Telegram. Il bot:

1. **Cerca** tra 55 ricette in testo semplice quale è rilevante (sistema RAG custom)
2. **Costruisce** il prompt inserendo il testo della ricetta come contesto
3. **Chiede** a Ollama (LLM locale) di rispondere usando solo quel contesto
4. **Streamma** la risposta token per token, aggiornando il messaggio in tempo reale

Se la ricetta non è nel dataset, risponde esattamente: *"Non ho questa ricetta nel mio archivio."*

---

## Comandi Telegram

| Comando | Descrizione |
|---|---|
| `/start` | Messaggio di benvenuto e lista comandi |
| `/lista` | Tutte le 55 ricette disponibili |
| `/cerca <ingrediente>` | Ricette che contengono quell'ingrediente |
| `/reset` | Cancella la memoria della chat corrente |

---

## Architettura

```
Utente (Telegram)
       │
       ▼
    bot.py          <- riceve il messaggio, gestisce lo streaming
       │
       ▼
   agent.py         <- gestisce la memoria per chat_id
       │
       ├──> rag.py  <- cerca nel dataset la ricetta rilevante
       │       │
       │       └──> data/ricette/*.txt   (55 file di testo)
       │
       └──> Ollama  <- genera la risposta in locale (llama3.2:1b)
```

---

## Stack

| Componente | Tecnologia |
|---|---|
| Linguaggio | Python 3.11+ |
| LLM | [Ollama](https://ollama.com) — `llama3.2:1b` (gira in locale) |
| Interfaccia | [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) 21.x |
| RAG | Implementazione custom — nessuna dipendenza esterna |
| Hosting | PC locale (il bot gira finché il PC è acceso) |

---

## Requisiti

- Python 3.11+
- [Ollama](https://ollama.com) installato e in esecuzione
- Un bot Telegram (creato con [@BotFather](https://t.me/botfather))

---

## Installazione

```bash
# 1. Clona il repository
git clone https://github.com/mariateesa/pasticcerebot.git
cd pasticcerebot

# 2. Installa le dipendenze
python -m pip install -r requirements.txt

# 3. Crea il file .env
cp .env.example .env
# Apri .env e inserisci il tuo TELEGRAM_TOKEN

# 4. Scarica il modello Ollama
ollama pull llama3.2:1b

# 5. Avvia il bot
python bot.py
```

### File .env

```env
TELEGRAM_TOKEN=il_tuo_token_telegram
```

---

## Struttura del progetto

```
pasticcerebot/
├── bot.py            # Entry point — gestisce i comandi Telegram e lo streaming
├── agent.py          # Logica agente — memoria, RAG, costruzione prompt, chiamata Ollama
├── rag.py            # Motore di ricerca — TF, coseno, match per nome
├── config.py         # Configurazione centralizzata (model, TOP_K, percorsi)
├── requirements.txt
├── .env.example
└── data/
    └── ricette/      # 55 file .txt con le ricette
        ├── tiramisu.txt
        ├── panna_cotta.txt
        ├── pastiera.txt
        └── ...
```

---

## Test

Il progetto include 38 test automatici divisi in due file.

```bash
# Esegui tutti i test
python -m pytest test_rag.py test_agent.py -v

# Solo il motore di ricerca
python -m pytest test_rag.py -v

# Solo la logica dell'agente
python -m pytest test_agent.py -v
```

**`test_rag.py`** (27 test) — verifica il motore RAG:
- Caricamento corretto di tutti i file
- Calcolo TF e similarità coseno
- Ricerca per nome ricetta e per ingrediente
- Priorità del match per nome sul coseno
- Casi limite (query vuota, query irrilevante)

**`test_agent.py`** (11 test) — verifica la logica dell'agente senza avviare Ollama:
- Isolamento della memoria per chat_id
- Reset della conversazione
- Struttura dei messaggi inviati all'LLM
- Iniezione del contesto RAG nel prompt
- Gestione della storia multi-turno

---

## Aggiungere ricette

Crea un file `.txt` in `data/ricette/` con il nome della ricetta usando underscore al posto degli spazi (es. `creme_caramel.txt`). Il bot la rileva automaticamente al prossimo messaggio, senza riavvio.

---

## Versione cloud (Groq + Railway)

Esiste anche una versione che gira 24/7 su cloud, senza bisogno del PC acceso, usando Groq API come LLM e Railway come hosting:  
-> [github.com/mariateesa/pasticcerebot-pro](https://github.com/mariateesa/pasticcerebot-pro)
