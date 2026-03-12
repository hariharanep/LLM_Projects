from langchain_classic import hub
from langchain_ollama import OllamaLLM
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

llm = OllamaLLM(model="llama3")

vector_store = Chroma(
    persist_directory="./chroma_db",
    embedding_function=OllamaEmbeddings(model="nomic-embed-text")
)

retriever = vector_store.as_retriever()

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


rag_prompt = hub.pull("rlm/rag-prompt")
qa_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | rag_prompt
    | llm
    | StrOutputParser()
)

while True:
    question = input("Question: ")
    if question.lower() == "exit":
        break
    answer = qa_chain.invoke(question)

    print(f"\nAnswer: {answer}\n")
