# RAG Chatbot (Gemini + LangChain + Chroma + Redis)

A production-ready, local-first Retrieval-Augmented Generation (RAG) chatbot that:
- Reads **PDF**, **Word (.docx)**, and **PowerPoint (.pptx)** files
- Stores embeddings in **ChromaDB** (persisted on disk)
- Uses **Gemini** via `langchain-google-genai` for both chat and embeddings
- Caches responses and session history in **Redis**
- **Remembers the last 10 turns** per session
- Returns **file paths** for sources used in the answer
- Includes a minimal **HTML/CSS/JS** frontend
- Separate **ingestion script** (`ingest/ingest.py`) to (re)build the vector store

---

## 1) Quickstart

**Prereqs**
- Python 3.10+
- Redis running locally (e.g., via Docker):  
  ```bash
  docker run --name rag-redis -d -p 6379:6379 redis:7
  ```

**Setup**
```bash
git clone <this-zip-extracted-folder>  # or unzip
cd rag-gemini-chroma-redis
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# edit .env and set GOOGLE_API_KEY and other values if needed
```

**Add documents**
- Put your `.pdf`, `.docx`, `.pptx` files into the `data/` folder

**Ingest to Chroma**
```bash
python ingest/ingest.py --data_dir ./data
```

**Run the API + UI**
```bash
uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload
```
- Open: http://localhost:8000  (the UI is served by FastAPI)

---

## 2) How it works

- **Ingestion** (`ingest/ingest.py`):
  - Loads PDF/DOCX/PPTX and extracts text
  - Splits text into chunks and creates embeddings with Gemini (`EMBEDDING_MODEL`)
  - Upserts to **ChromaDB** persisted at `CHROMA_DIR`
  - Sets a Redis flag while ingestion is running so the app can serve cached answers

- **Server** (`server/app.py`):
  - FastAPI backend that exposes:
    - `POST /chat` — chat with memory (last 10 turns) and source file paths
    - `POST /upload` — optional: upload files and trigger ingestion
    - `GET /status` — ingestion status
  - Uses **history-aware RAG**: chat history improves retrieval
  - Answers always include **Sources** (unique file paths used)

- **Cache & Memory**:
  - **Redis LLM cache** to speed repeated prompts
  - **QA cache** (exact-match question → answer JSON) during ingestion
  - **Session memory** (last 10 turns) stored in Redis

---

## 3) Environment variables (.env)

| Key               | Description | Default |
|-------------------|-------------|---------|
| `GOOGLE_API_KEY`  | Gemini API key | — |
| `GEMINI_MODEL`    | Chat model id | `gemini-2.0-flash` |
| `EMBEDDING_MODEL` | Embedding model id | `gemini-embedding-001` |
| `CHROMA_DIR`      | Chroma persist dir | `./chromadb` |
| `REDIS_URL`       | Redis connection url | `redis://localhost:6379/0` |
| `HOST`            | API host | `0.0.0.0` |
| `PORT`            | API port | `8000` |

---

## 4) API

**POST /chat**  
Request:
```json
{ "message": "What is the refund policy?", "session_id": "optional-client-id" }
```
Response:
```json
{
  "answer": "...",
  "sources": [{"path": "data/policies/refund_policy.pdf"}],
  "from_cache": false,
  "ingesting": false,
  "session_id": "abc123"
}
```

**POST /upload** (optional convenience)  
- Multiform: `files[]` field for one or many of .pdf/.docx/.pptx  
- Server saves to `data/` then runs ingestion.

---

## 5) Notes
- Supported file types: `.pdf`, `.docx`, `.pptx` (you can add more in `server/loaders.py`)
- If no relevant docs are found, the bot will say so rather than hallucinate.
- You can safely re-run ingestion; documents will be re-embedded & upserted.
- You can change models in `.env` without changing code.

---

## 6) Troubleshooting
- **405 Method Not Allowed**: Make sure you're POST-ing JSON to `/chat`.
- **CORS issues**: The UI served by FastAPI avoids CORS. If you host elsewhere, enable CORS in `server/app.py`.
- **Redis not running**: Start Redis (see above) and check `REDIS_URL` in `.env`.
- **Gemini quota / key**: Verify `GOOGLE_API_KEY` and model ids in `.env`.

