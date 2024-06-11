import numpy as np
import redis

from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Optional

@dataclass_json
@dataclass
class Document:
    url: str
    title: str = ''
    date: str = ''

    def title_has_term(self, term: str) -> bool:
        return term in title

    def title_has_any_term(self, terms: list[str]) -> bool:
        for term in terms:
            if self.title_has_term(term):
                return True
        return False

class DocumentIndex:
    def __init__(self, redis_port: int):
        '''
        Initializes a new DocumentIndex.
        '''
        self.redis = redis.Redis(host='localhost', port=redis_port, db=0)

    def query(self, terms: list[str]) -> list[Document]:
        ret = []
        for url in self.all_urls():
            document = self.url_to_document(url)
            if document is None:
                continue
            if document.title_has_any_term(terms):
                ret.append(document)
        return ret

    def info(self):
        '''
        Returns a dictionary of Redis server information.
        '''
        return self.redis.info()

    def insert_or_update_document(self, document: Document):
        key = f'url:{document.url}'
        values = document.to_json()
        self.redis.set(key, values)

    def apply_document_update(self, update_fn):
        urls = self.all_urls()
        for document_key in urls:
            document_before = self.url_to_document(document_key)
            document_before_url = document_before.url
            if document_before is None:
                continue
            document_after = update_fn(document_before)
            if document_after.url != document_before_url:
                raise ValueError(f'URL has changed: {document_before_url} -> {document_after.url}')
            self.insert_or_update_document(document_after)

    def all_urls(self) -> list[bytes]:
        return self.redis.keys("url:*")

    def url_to_document(self, url: str|bytes) -> Optional[Document]:
        data = self.redis.get(url)
        if data is None:
            return None
        return Document.from_json(data)

    def delete_url(self, url: str|bytes):
        k = url
        if isinstance(url, str):
            k = f'url:{url}'
        self.redis.delete(k)

    def all_documents(self) -> list[Document]:
        docs = []
        for url in self.all_urls():
            doc = self.url_to_document(url)
            if doc is not None:
                docs.append(doc)
        return docs