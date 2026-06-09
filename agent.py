import os
import ollama
from config import OLLAMA_MODEL
from rag import carica_ricette, cerca

# Storico conversazioni: { chat_id: [ {role, content}, ... ] }
_storico: dict[int, list[dict]] = {}
MAX_MESSAGGI = 10

SYSTEM_PROMPT = """Sei PasticcereBot, un assistente esperto di pasticceria.
Rispondi sempre in italiano, con un tono cordiale e preciso.
Usa SOLO le informazioni fornite nel contesto per rispondere alle domande sulle ricette.
Se la risposta non è nel contesto, rispondi esattamente: "Non ho questa ricetta nel mio archivio." e non aggiungere altro.
Ricorda il contesto della conversazione: se l'utente dice "e quella al cioccolato?" si riferisce all'argomento precedente."""


def reset_memoria(chat_id: int) -> None:
    _storico[chat_id] = []


def _prepara_messaggi(domanda: str, chat_id: int) -> list[dict]:
    """Costruisce la lista messaggi per Ollama (RAG + storico)."""
    chunks = carica_ricette()
    contesto = cerca(domanda, chunks)

    # Se non trova nulla, riprova con le ultime domande dello storico
    if not contesto and chat_id in _storico:
        messaggi_precedenti = [
            m["content"] for m in _storico[chat_id] if m["role"] == "user"
        ][-3:]
        query_estesa = " ".join(messaggi_precedenti + [domanda])
        contesto = cerca(query_estesa, chunks)

    if contesto:
        testo_contesto = "\n\n---\n\n".join(
            f"[Ricetta: {os.path.splitext(c['file'])[0].replace('_', ' ').upper()}]\n{c['testo']}"
            for c in contesto
        )
        messaggio_utente = (
            f"Rispondi usando SOLO le informazioni qui sotto.\n\n"
            f"{testo_contesto}\n\n"
            f"Domanda dell'utente: {domanda}"
        )
    else:
        messaggio_utente = domanda

    if chat_id not in _storico:
        _storico[chat_id] = []

    storico = _storico[chat_id]

    # Nello storico salviamo solo la domanda originale (non il contesto RAG)
    # Il contesto RAG viene aggiunto solo nel messaggio corrente
    storico_con_domanda = storico + [{"role": "user", "content": messaggio_utente}]

    if len(storico_con_domanda) > MAX_MESSAGGI * 2:
        storico_con_domanda = storico_con_domanda[-(MAX_MESSAGGI * 2):]

    # Salva nello storico solo la domanda pulita
    storico.append({"role": "user", "content": domanda})
    if len(storico) > MAX_MESSAGGI * 2:
        _storico[chat_id] = storico[-(MAX_MESSAGGI * 2):]

    return [{"role": "system", "content": SYSTEM_PROMPT}] + storico_con_domanda


def _salva_risposta(chat_id: int, testo: str) -> None:
    """Salva la risposta del bot nello storico."""
    if chat_id in _storico:
        _storico[chat_id].append({"role": "assistant", "content": testo})


def rispondi(domanda: str, chat_id: int) -> str:
    """Risposta completa (non streaming)."""
    messaggi = _prepara_messaggi(domanda, chat_id)
    try:
        risposta = ollama.chat(model=OLLAMA_MODEL, messages=messaggi)
        testo = risposta["message"]["content"]
    except ollama.ResponseError as e:
        if "model" in str(e).lower():
            testo = f"Modello '{OLLAMA_MODEL}' non trovato.\nEsegui: ollama pull {OLLAMA_MODEL}"
        else:
            testo = f"Errore Ollama: {e}"
    except Exception as e:
        if "connect" in str(e).lower():
            testo = "Ollama non e' raggiungibile.\nAssicurati che sia avviato con: ollama serve"
        else:
            testo = f"Errore imprevisto: {e}"
    _salva_risposta(chat_id, testo)
    return testo


def rispondi_stream(domanda: str, chat_id: int):
    """Generatore: restituisce token per token la risposta di Ollama."""
    messaggi = _prepara_messaggi(domanda, chat_id)
    testo_completo = ""
    try:
        stream = ollama.chat(model=OLLAMA_MODEL, messages=messaggi, stream=True)
        for chunk in stream:
            token = chunk["message"]["content"]
            testo_completo += token
            yield token
    except ollama.ResponseError as e:
        msg = f"Modello '{OLLAMA_MODEL}' non trovato.\nEsegui: ollama pull {OLLAMA_MODEL}" \
            if "model" in str(e).lower() else f"Errore Ollama: {e}"
        testo_completo = msg
        yield msg
    except Exception as e:
        msg = "Ollama non e' raggiungibile.\nAssicurati che sia avviato con: ollama serve" \
            if "connect" in str(e).lower() else f"Errore imprevisto: {e}"
        testo_completo = msg
        yield msg
    finally:
        _salva_risposta(chat_id, testo_completo)
