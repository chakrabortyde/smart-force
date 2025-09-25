import os,certifi
import sys
import pathlib

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredPowerPointLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

from langchain_huggingface import HuggingFaceEmbeddings


# Ensure project root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
os.environ["CHROMA_TELEMETRY_ENABLED"] = "false"
os.environ["HF_HOME"] = "./hf_cache"
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
# Ensure project root is in sys.path
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from server.settings import Settings

settings = Settings()
# Initialize HuggingFace embeddings
# embeddings = HuggingFaceInferenceAPIEmbeddings(
#     model_name="sentence-transformers/paraphrase-MiniLM-L12-v2",
#     api_key=settings.HUGGINGFACEHUB_API_TOKEN
#     )
embeddings = HuggingFaceEmbeddings(
    model_name="./models/all-MiniLM-L6-v2",  # use local path
    model_kwargs={"device": "cpu"}
)

DATA_DIR = BASE_DIR /"data"
CHROMA_DIR = settings.CHROMA_DIR


def load_documents():
    docs = []
    for file in os.listdir(DATA_DIR):
        path = os.path.join(DATA_DIR, file)
        
        if file.endswith(".pdf"):
            loader = PyPDFLoader(path)
        elif file.endswith(".docx"):
            loader = Docx2txtLoader(path)
        elif file.endswith(".pptx"):
            loader = UnstructuredPowerPointLoader(path)
        else:
            continue

        loaded = loader.load()
        for d in loaded:
            d.metadata["source"] = file   # ✅ store file path
        
        docs.extend(loader.load())
    return docs


def main():
    print("Loading documents...")
    documents = load_documents()

    print("Splitting documents...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    
    chunks = splitter.split_documents(documents)
    print("chunk length == ",len(chunks))
    try:
        vec = embeddings.embed_query(chunks[0].page_content[:200])
        print(f"[DEBUG] First embedding length: {len(vec)}")
    except Exception as e:
        print("[ERROR] Failed to embed sample chunk:", e)
    # print("embedding length == ",len(embeddings.embed_query(chunks[0].page_content[:200])))
    print("Saving to Chroma...")
    vectordb = Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory=CHROMA_DIR)
   
    #vectordb.persist()
    print("✅ Ingestion complete! Data saved to", CHROMA_DIR)


if __name__ == "__main__":
    main()



