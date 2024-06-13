import os
import time
import scraper.hackernews
import redis
import document
import ranking
import urllib.parse

from quart import Quart, request
from document import DocumentIndex
from indexer import index_document

app = Quart(__name__)
all_documents = DocumentIndex(redis_port=6379)

search_bar = '''
<div><a href="/">Home</a></div>
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
    <button type="submit">Scrape New Posts</button>
</form>
<form action="/reindex" method="post">
    <button type="reindex">Reindex</button>
</form>
<div><a href="/index">Index</a></div>
<div><a href="/redis-status">Redis Status</a></div>
    '''


@app.route('/redis-status')
async def redis_status():
    return all_documents.info()


@app.route('/search')
async def search():
    query = ranking.Query(request.args.get('q', default=''))
    ranked_documents = query.rank_all_documents(all_documents.all_documents())

    def document_to_html(rd: ranking.RankedDocument) -> str:
        return f'<div><a href="{rd.document.url}">{rd.document.title}</a>{str(rd.signals)}</div>'
    return f'{search_bar}{"\n".join(map(document_to_html, ranked_documents))}'


@app.route('/index')
async def index():
    item = request.args.get('item')
    if item is None:
        documents = all_documents.all_documents()
        return [d.to_dict() for d in documents]
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
{search_bar}
<p>Scrape complete. {added} new document(s) scraped.</p>
<a href="./">Home</a>
'''


@app.route('/reindex', methods=['POST'])
async def reindex():
    start = time.time()
    documents_indexed = all_documents.apply_document_update(index_document)
    end = time.time()
    duration = end - start
    return f'''
{search_bar}
<p>Reindex completed in {duration:.1f} seconds at a rate of {documents_indexed / duration:.1f} documents per second.</p>
<a href="/">Home</a>
'''


def main():
    port = int(os.getenv('ORBIT_PORT', '8000'))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
