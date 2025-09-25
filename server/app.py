import os, certifi
import uuid
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv



from langchain.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from server.cache import CacheManager
from server.settings import Settings
from fastapi.staticfiles import StaticFiles
from server.safty import check_safety

# Load environment variables
load_dotenv()
settings = Settings()

# Force Python & requests to use certifi certificates
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
os.environ["CHROMA_TELEMETRY_ENABLED"] = "false"
# Initialize app
app = FastAPI()

# Path where your docs are stored
FILES_DIR = os.path.join(os.getcwd(), "data")

# Mount static files
app.mount("/files", StaticFiles(directory=FILES_DIR), name="files")

# Allow frontend JS to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Initialize cache (Redis if available, else in-memory)
cache = CacheManager(redis_url=settings.REDIS_URL)

# Initialize embeddings (HuggingFace = free, local)
# embeddings = HuggingFaceEmbeddings(
#     model_name="sentence-transformers/all-MiniLM-L6-v2",
#     api_key=os.getenv("HUGGINGFACEHUB_API_TOKEN")
#     )
embeddings = HuggingFaceEmbeddings(
    model_name="./models/all-MiniLM-L6-v2",  # use local path
    model_kwargs={"device": "cpu"}
)

# Load vector DB
#vectordb = Chroma(persist_directory=settings.CHROMA_DIR, embedding_function=embeddings)

vectordb = Chroma(
    persist_directory=settings.CHROMA_DIR,
    embedding_function=embeddings
)


retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": 4})

# Gemini stays for answering
llm = ChatGoogleGenerativeAI(model=settings.GEMINI_MODEL,temperature=0,
                             google_api_key=settings.GOOGLE_API_KEY,
                             convert_system_message_to_human=True) 

# Build retrieval chain
prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a helpful assistant working for Fractal. Use the provided context to answer the user’s question. "
     "If unsure, say you don’t know. Always mention sources when available.\n\n"
     "If answer is out of context, start your answer with sorry.\n\n"
     "Context:\n{context}"),
    ("human", "{input}")
])

doc_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, doc_chain)

    
# --------------------------
# API Routes
# --------------------------
@app.get("/status")
def status():
    return {"ingesting": "OK"}

PHRASES = ["not sure", "sorry", "need a question"]  # change as needed

def contains_phrases(answer: str, phrases: list[str]) -> bool:
    """Return True if ANY of the phrases are present in the answer."""
    answer_low = answer.lower()
    return any(phrase.lower() in answer_low for phrase in phrases)

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_input = data.get("message", "").strip()
    session_id = data.get("session_id") or str(uuid.uuid4())

    if not user_input:
        return JSONResponse({"answer": "Please ask a valid question.", "sources": [], "session_id": session_id})

    reply = check_safety(user_input)
    
    if reply:
        return JSONResponse({
            "answer": reply,
            "sources": [],
            "session_id": session_id
        })
    else :

        # 1. Check Q/A cache
        cached_answer = cache.get_answer(user_input)
        
        if cached_answer:
            return JSONResponse({
                "answer": cached_answer["answer"],
                "sources": cached_answer["sources"],
                "session_id": session_id
            })
        else :
            # 2. Add user message to history
            cache.add_to_history(session_id, "user", user_input)
            history = cache.get_history(session_id)

            # 3. Run retrieval + LLM
            result = rag_chain.invoke({"input": user_input})
            answer = result.get("answer", "I’m not sure.")
            context = result.get("context", [])

            # 1) Retrieve with thresholding
            
            # Collect sources
            sources = []
            seen = set()
            
            # Check if required phrases exist
            phrases_present = contains_phrases(answer, PHRASES)
            
            if not phrases_present:
                for doc in context:
                    path = doc.metadata.get("source")
                    if path and path not in sources:
                        filename = os.path.basename(path)
                        if filename and filename not in seen:
                            seen.add(filename)
                            sources.append(f"/files/{filename}")
            else:
                sources = []
            
            
                    
            # 4. Save assistant reply + cache Q/A
            cache.add_to_history(session_id, "assistant", answer, sources)
            cache.set_answer(user_input, answer, sources)

            return JSONResponse({
                "answer": answer,
                "sources": sources,
                "session_id": session_id
            })


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    # Save uploaded file into data/ folder
    save_path = os.path.join("data", file.filename)
    with open(save_path, "wb") as f:
        f.write(await file.read())

    return {"message": f"File {file.filename} uploaded successfully. Run ingest.py to update the database."}


@app.get("/health")
async def health():
    return {"status": "ok"}

# Serve static frontend
app.mount("/", StaticFiles(directory="web", html=True), name="web")