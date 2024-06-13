import indexer
import numpy as np

from document import Document
from dataclasses import dataclass


@dataclass
class RankingSignals:
    matching_terms: int
    title_similarity: float

    def score(self) -> float:
        return self.matching_terms * 0.5 + self.title_similarity


@dataclass
class RankedDocument:
    document: Document
    signals: RankingSignals


class Query:
    def __init__(self, query):
        self.terms = indexer.to_keyword_list(query)
        self.query_embedding = np.array(indexer.embed_string(query))

    def rank_document(self, document: Document) -> RankingSignals:
        matching_terms = 0
        for term in document.terms:
            if term in self.terms:
                matching_terms += 1
        title_similarity = 0.0
        if len(document.title_embedding) > 0:
            title_similarity = self.query_embedding.dot(
                document.title_embedding)
        return RankingSignals(matching_terms=matching_terms, title_similarity=title_similarity)

    def rank_all_documents(self, documents: list[Document]) -> list[RankedDocument]:
        ranked = []
        for document in documents:
            signals = self.rank_document(document)
            if signals.score() > 0.01:
                ranked.append(RankedDocument(
                    document=document, signals=signals))
        ranked.sort(key=lambda rd: rd.signals.score(), reverse=True)
        return ranked
