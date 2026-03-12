from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

loader = DirectoryLoader("./Books", glob="**/*.docx")
books = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
all_splits = text_splitter.split_documents(books)

vectorstore = Chroma.from_documents(
    documents=all_splits,
    embedding=OllamaEmbeddings(model="nomic-embed-text"),
    persist_directory="./chroma_db",
)

question = "Who is James?"
docs = vectorstore.similarity_search(question)
print(docs)