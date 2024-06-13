import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

from document import Document
from sentence_transformers import SentenceTransformer

sentence_embedder = SentenceTransformer(
    'sentence-transformers/all-MiniLM-L6-v2')


def embed_string(s: str) -> list[float]:
    return sentence_embedder.encode(s).tolist()


def index_document(document: Document):
    document.terms = to_keyword_list(document.title)
    document.title_embedding = embed_string(document.title)
    return document


lemmatizer = WordNetLemmatizer()
nltk.download('punkt')
nltk.download('wordnet')


def to_keyword_list(text: str) -> list[str]:
    tokens = word_tokenize(text)
    processed_tokens = [lemmatizer.lemmatize(
        token.lower()) for token in tokens]
    return list(set(processed_tokens))
