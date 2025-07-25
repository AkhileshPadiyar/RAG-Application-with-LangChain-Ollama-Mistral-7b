import tkinter as tk
from tkinter import scrolledtext
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OllamaEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms import Ollama
import threading
import time

# Load and prepare the QA chain (do this once at startup)
loader = TextLoader("sample.txt")
documents = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
texts = text_splitter.split_documents(documents)
embeddings = OllamaEmbeddings(model="mistral:7b")
vectorstore = Chroma.from_documents(texts, embeddings)
retriever = vectorstore.as_retriever()
qa_chain = RetrievalQA.from_chain_type(
    llm=Ollama(model="mistral:7b"),
    retriever=retriever
)

def ask_question():
    query = question_entry.get()
    if not query.strip():
        return
    # Show loader and disable input
    answer_box.config(state='normal')
    answer_box.insert(tk.END, f"Q: {query}\n")
    answer_box.insert(tk.END, "Processing...\n")
    answer_box.see(tk.END)
    answer_box.config(state='disabled')
    question_entry.config(state='disabled')
    ask_button.config(state='disabled')
    # Start background thread for LLM call
    threading.Thread(target=process_query, args=(query,)).start()

def process_query(query):
    answer = qa_chain.run(query)
    # Remove loader and stream answer
    root.after(0, lambda: display_streaming_answer(query, answer))

def display_streaming_answer(query, answer):
    # Remove "Processing..." line
    answer_box.config(state='normal')
    content = answer_box.get("1.0", tk.END)
    lines = content.splitlines()
    if lines and lines[-1] == "Processing...":
        lines = lines[:-1]
    answer_box.delete("1.0", tk.END)
    answer_box.insert(tk.END, "\n".join(lines) + "\n")
    # Stream answer word by word
    words = answer.split()
    def stream(i=0):
        if i < len(words):
            answer_box.insert(tk.END, words[i] + " ")
            answer_box.see(tk.END)
            answer_box.update()
            root.after(50, stream, i+1)  # 50ms per word
        else:
            answer_box.insert(tk.END, "\n" + "-"*40 + "\n")
            answer_box.config(state='disabled')
            question_entry.config(state='normal')
            ask_button.config(state='normal')
            question_entry.delete(0, tk.END)
            question_entry.focus()
    stream()

# Set up the GUI
root = tk.Tk()
root.title("LangChain QA App (Ollama)")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

question_label = tk.Label(frame, text="Ask something about the document:")
question_label.pack(anchor='w')

question_entry = tk.Entry(frame, width=60)
question_entry.pack(fill='x', pady=5)
question_entry.focus()

ask_button = tk.Button(frame, text="Ask", command=ask_question)
ask_button.pack(pady=5)

answer_box = scrolledtext.ScrolledText(frame, width=70, height=20, state='disabled', wrap=tk.WORD)
answer_box.pack(pady=5)

root.mainloop() 