from dotenv import load_dotenv
import os
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OllamaEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms import Ollama





#load api key
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

#1. Load documents
loader = TextLoader("sample.txt")
documents = loader.load()

#2. Split into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
texts = text_splitter.split_documents(documents)

# 2. Convert chunks to Vectors
embeddings = OllamaEmbeddings(model="mistral:7b")
vectorstore = Chroma.from_documents(texts, embeddings)

# 4. Create QA chain with Retreival
retriever = vectorstore.as_retriever()
qa_chain = RetrievalQA.from_chain_type(
    llm=Ollama(model="mistral:7b"),
    retriever=retriever
)

# 5. Ask a question
while True:
    query = input("Ask something about the document(write 'exit' to quit):")
    if(query.lower() == 'exit'):
        break
    answer = qa_chain.run(query)
    print("/n<-----Answer------->:\n ", answer)
    print("--------------------------------/n")


