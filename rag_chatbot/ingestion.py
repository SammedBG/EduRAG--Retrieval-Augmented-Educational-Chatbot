import os
from PyPDF2 import PdfReader

def load_pdfs(folder_path):
    documents = []
    for file in os.listdir(folder_path):
        if file.endswith(".pdf"):
            path = os.path.join(folder_path, file)
            pdf = PdfReader(path)
            text = ""
            for page in pdf.pages:
                if page.extract_text():
                    text += page.extract_text()
            documents.append({"file": file, "text": text})
    return documents

def load_txt(folder_path):
    documents = []
    for file in os.listdir(folder_path):
        if file.endswith(".txt"):
            path = os.path.join(folder_path, file)
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            documents.append({"file": file, "text": text})
    return documents

def load_documents():
    notes = load_pdfs("data/course_notes") + load_txt("data/course_notes")
    papers = load_pdfs("data/past_papers") + load_txt("data/past_papers")
    return notes + papers

if __name__ == "__main__":
    docs = load_documents()
    print(f"Loaded {len(docs)} documents.")
 