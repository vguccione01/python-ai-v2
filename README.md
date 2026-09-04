# LipariBank AI

## Quickstart

### Prerequisiti

- [`uv`](https://docs.astral.sh/uv/)
- Python 3.12 - installato con `uv`. `uv python install 3.12 `

Verifica che gli strumenti siano disponibili:

```bash
uv --version
```

### 2. Crea l’ambiente virtuale e installa le dipendenze

`uv` utilizza `pyproject.toml` e `uv.lock` per installare le dipendenze con versioni riproducibili:

```bash
uv sync
```

Per installare anche le dipendenze di sviluppo, come `pytest`, `ruff` e `mypy`:

```bash
uv sync --dev
```

### 3. Configura le variabili d’ambiente

Crea il file `.env` partendo dall’esempio:

```bash
cp .env.example .env
```

Imposta nel file `.env` i valori appropriati per il tuo ambiente. Sono obbligatorie queste variabili:

- `DATABASE_URL`
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `JWT_SECRET`

Il file `.env` contiene dati sensibili e non deve essere committato.

### 4. Avvia l’applicazione

Dalla directory principale del progetto:

```bash
uv run uvicorn lipari_bank_ai.main:app --reload
```

L’API sarà disponibile all’indirizzo <http://127.0.0.1:8000>.

### 5. Verifica il funzionamento

Controlla l’endpoint di health check:

```bash
curl http://127.0.0.1:8000/health
```

La risposta attesa è un JSON con `status` impostato a `UP`, ad esempio:

```json
{
  "status": "UP",
  "timestamp": "2026-01-01T00:00:00+00:00",
  "app_name": "LipariBank AI",
  "version": "1.0.0"
}
```

La documentazione interattiva è disponibile su <http://127.0.0.1:8000/docs>; lo schema OpenAPI è disponibile su <http://127.0.0.1:8000/openapi.json>.

## Comandi utili

Controlla lo stile e la qualità del codice:

```bash
uv run ruff check .
uv run mypy src
```

Per applicare automaticamente la formattazione con Ruff:

```bash
uv run ruff format .
```
