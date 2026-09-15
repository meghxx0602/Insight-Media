import hashlib

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


CHROMA_DIR = "vectore_db" #Dir inorder to save stuff, vector embeddings banke yaha locally save hongi 
EMBEDDING_MODEL = "all-MiniLM-L6-v2" #Model


def get_embeddings(): #Transcript -> uski embeddings
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"} #keywords args -> inorder to run embedding model in the device
    )


def get_collection_name(transcript: str) -> str:
    transcript_id = hashlib.md5(
        transcript.encode("utf-8")
    ).hexdigest()[:12]

    return f"meeting_{transcript_id}"


def build_vector_store(transcript: str) -> Chroma: #Transcript -> vectors -> storing in DB
    print("Building vector store...")

    collection_name = get_collection_name(transcript) #Making of the splitter

    splitter = RecursiveCharacterTextSplitter( 
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = splitter.split_text(transcript) #Splitting transcript in chunks

    docs = [ #Doc mai chunks ka page content bhjna, wrap krna basically in docs
        Document(
            page_content=chunk,
            metadata={"chunk_index": i}
        )
        for i, chunk in enumerate(chunks) #Chunks converted into docs
    ]

    embeddings = get_embeddings() #Call the embedding func

    vector_store = Chroma.from_documents( #Creating the vector store and Docs jismai chunks ka page doc hai -> convert to embeddings
        documents=docs,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=CHROMA_DIR #saving embeddings here
    )

    print("Vector store ready.")

    return vector_store #Return the store with vectors init


def load_vector_store(transcript: str) -> Chroma: #To load the vector store, inorder to nikalo stuff needed this just gives the location of the store
    embeddings = get_embeddings()

    collection_name = get_collection_name(transcript)

    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR
    )

    return vector_store


def get_retriever(vector_store: Chroma, k: int = 4): #Nikalo the stuff by using load vector db and then retrieve the info you need.
    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}
    )