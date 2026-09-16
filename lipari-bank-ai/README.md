# LipariBank AI

Bootcamp Python AI Powered v1 — Lipari Consulting.

Sistema RAG che risponde a domande su regolamenti bancari usando embeddings locali (Ollama) e retrieval su PostgreSQL/pgvector.

## Architettura del flusso RAG

```
Documento (markdown)
      │
      ▼
chunk_text (lib/chunking.py)        ── suddivide per paragrafi "##" (chunk ~500 char, overlap 0)
      │
      ▼
EmbeddingClient (llm/embedding_client.py)  ── POST /api/embed di Ollama (nomic-embed-text, 768 dim)
      │
      ▼
document_chunks (PostgreSQL + pgvector)    ── Vector(768) con indice HNSW (cosine)
      │
      ▼
RetrievalService ── query embedding + top-k più simili (1 - (embedding <=> ...))
      │
      ▼
RAGService ── contesto → provider LLM → risposta con citazioni
```

## Embeddings con Ollama (gratuiti, locali)

L'integrazione usa **Ollama** invece di OpenAI per generare gli embeddings:

- Modello: `nomic-embed-text` → **768 dimensioni**
- Endpoint: `POST http://localhost:11434/api/embed` (body `{"model": ..., "input": [...]}`)
- Client: `EmbeddingClient` in `src/lipari_bank_ai/llm/embedding_client.py`, basato su `httpx`
- Nessuna chiave API o costo: il modello gira in locale

### Configurazione (.env)

```ini
EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_DIM=768
OLLAMA_URL=http://localhost:11434
```

### Prerequisiti Ollama

```bash
ollama pull nomic-embed-text   # ~274 MB
ollama list                    # verifica che il modello sia presente
curl http://localhost:11434/api/tags
```

### Cambiamenti rispetto alla versione OpenAI

| Aspetto | Prima | Dopo |
|---|---|---|
| Provider | OpenAI `text-embedding-3-small` | Ollama `nomic-embed-text` |
| Dimensioni embedding | 1536 | **768** |
| Dipendenza | `openai` | `httpx` (chiamata diretta a `/api/embed`) |
| Chiave API | richiesta | non richiesta |
| DB | `Vector(1536)` | `Vector(768)` (migration `b7e3d41f9a20`) |

## Chunking dei documenti

La funzione `chunk_text` (in `src/lipari_bank_ai/lib/chunking.py`) suddivide un documento in blocchi:

- `chunk_size=500` — lunghezza massima in caratteri per chunk
- `overlap=0` — usato in `IngestService` perché i documenti markdown sono già strutturati per paragrafi `##`
- I chunk vengono spezzati in corrispondenza del separatore `##` quando questo cade oltre la metà del chunk

`IngestService` (in `src/lipari_bank_ai/services/ingest_service.py`) importa `chunk_text` dal modulo `lib/chunking.py` per ogni documento, genera gli embeddings in batch e salva ogni chunk su `document_chunks`.

> Nota: nella migrazione a Ollama la tabella `document_chunks` viene svuotata (TRUNCATE) perché i vettori 1536-dim non sono compatibili con `vector(768)`. I documenti vanno quindi re-ingestiti.

## Setup

1. PostgreSQL con estensione pgvector in esecuzione.
2. Configura `.env` (vedi `.env.example`).
3. Installa le dipendenze:

```bash
uv sync
```

4. Applica le migration:

```bash
uv run alembic upgrade head
```

5. Avvia il server:

```bash
uv run uvicorn lipari_bank_ai.main:app --reload
```

## Ingestione dei documenti

Inserisci i file `.md` in `data/docs/` e lancia:

```bash
uv run python -m lipari_bank_ai.scripts.ingest_docs
```

Oppure via API:

```bash
curl -X POST localhost:8000/api/ai/documents/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "tariffe",
    "content": "## Commissioni bonifici\nIl bonifico SEPA istantaneo non prevede commissioni...",
    "metadata": {"title": "Tariffe"}
  }'
```

Risposta: `{"chunk_count": <n>, "embedding_dim": 768}`

## Domanda (retrieval)

```bash
curl -X POST localhost:8000/api/ai/advice \
  -H "Content-Type: application/json" \
  -d '{"question":"Quali commissioni per un bonifico SEPA istantaneo?"}'
```

Il flusso: embedding della domanda → ricerca top-k in pgvector → contesto passato al provider LLM (`DEFAULT_MODEL`, es. `opencode-big-pickle`) → risposta con citazioni dei documenti.