import os
import time
import scraper.hackernews
import redis
import document
import urllib.parse

from quart import Quart, request
from document import DocumentIndex

app = Quart(__name__)
all_documents = DocumentIndex(redis_port=6379)

search_bar = '''
<h1>Search</h1>
<form action="/search" method="get">
  <input type="text" name="q">
  <input type="submit" value="Search">
</form>
'''


@app.route('/')
async def home():
    return f'''
{search_bar}

<h1>Links</h1>
<form action="/scrape" method="post">
    <button type="submit">Scrape</button>
</form>
<form action="/reindex" method="post">
    <button type="reindex">Reindex</button>
</form>
<div><a href="/index">Index</a></div>
<div><a href="/status">Status</a></div>
    '''


@app.route('/status')
async def status():
    redis_info = all_documents.info()
    return {'redis': redis_info}


@app.route('/search')
async def search():
    query = request.args.get('q', default='')
    query_terms = set(query.lower().strip().split())

    def predicate(document: document.Document) -> int:
        matching_terms = 0
        for term in document.terms:
            if term in query_terms:
                matching_terms += 1
        return matching_terms

    def document_to_html(document: document.Document) -> str:
        return f'<div><a href="{document.url}">{document.title}</a></div>'
    documents = all_documents.ranked_documents(predicate)
    return f'{search_bar}{"\n".join(map(document_to_html, documents))}'


@app.route('/index')
async def index():
    item = request.args.get('item')
    if item is None:
        return [
            {'id': str(url),
             'index_details': f'/index?item={urllib.parse.quote_from_bytes(url)}'}
            for url in all_documents.all_urls()
        ]
    return all_documents.url_to_document(item).to_dict()


@app.route('/scrape', methods=['POST'])
async def scrape():
    added = 0
    for url in scraper.hackernews.top_stories():
        if all_documents.url_to_document(url) is not None:
            continue
        post = await scraper.hackernews.Post.from_url(url)
        document = post.to_document()
        all_documents.insert_or_update_document(document)
        added += 1
    return f'''
<p>Scrape complete. {added} new documents scraped.</p>
<a href="./">Home</a>
'''


@app.route('/reindex', methods=['POST'])
async def reindex():
    def index_document(document: document.Document):
        document.terms = list(set(document.title.lower().strip().split()))
        return document
    all_documents.apply_document_update(index_document)
    return f'''
<p>Reindex complete.</p>
<a href="./">Home</a>
'''


def main():
    port = int(os.getenv('ORBIT_PORT', '8000'))
    app.run(port=port)


if __name__ == '__main__':
    main()
