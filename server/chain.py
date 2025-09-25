from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage

def get_embeddings(api_key: str, embedding_model: str):
    # LangChain reads GOOGLE_API_KEY from env; explicit pass for clarity
    return GoogleGenerativeAIEmbeddings(model=embedding_model, google_api_key=api_key)

def get_llm(api_key: str, model: str):
    return ChatGoogleGenerativeAI(model=model, google_api_key=api_key, temperature=0.2)

def get_vectorstore(embeddings, persist_directory: str, collection_name: str = "docs"):
    return Chroma(embedding_function=embeddings, persist_directory=persist_directory, collection_name=collection_name)

def chunk_docs(docs: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=150)
    return splitter.split_documents(docs)

# Build a retrieval RAG chain with chat history awareness
def build_rag_chain(llm, retriever):
    system_prompt = (
        "You are a helpful RAG assistant. Use ONLY the provided context to answer. "
        "If the answer is not in the context, say you don't know. "
        "Be concise (max ~6 sentences)."
    )

    # The {context} variable will be filled with retrieved docs by the combine chain
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt + "\n\nContext:\n{context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}")
    ])

    doc_chain = create_stuff_documents_chain(llm, prompt)
    rag = create_retrieval_chain(retriever, doc_chain)
    return rag

def to_langchain_history(history_items: List[Dict[str, str]]) -> List[BaseMessage]:
    msgs: List[BaseMessage] = []
    for item in history_items[-20:]:  # up to last 10 turns
        role = item.get("role")
        content = item.get("content", "")
        if role == "user":
            msgs.append(HumanMessage(content=content))
        elif role == "assistant":
            msgs.append(AIMessage(content=content))
    return msgs
