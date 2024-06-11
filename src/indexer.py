from document import Document
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def index_document(document: Document):
   document.terms = list(set(document.title.lower().strip().split()))
   document.title_embedding = model.encode(document.title).tolist()
   return document
