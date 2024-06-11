import os
import time
import scraper.hackernews
import redis
import document

from quart import Quart
from document import DocumentIndex

app = Quart(__name__)
all_documents = DocumentIndex(redis_port=6379)

for document in all_documents.all_documents():
    print(document)

@app.route('/')
async def home():
    return f'''
<h1>Search</h1>
<form action="/search" method="get">
  <input type="text" name="q">
  <input type="submit" value="Search">
</form>

<h1>Links</h1>
<a href="/status">Status</a>
    '''

@app.route('/status')
async def status():
    redis_info = all_documents.info()
    return {'redis': redis_info}

@app.route('/search')
async def search():
    return 'todo'

def main():
    port = int(os.getenv('PAPER_PETE_PORT', '8001'))
    app.run(port=port)

if __name__ == '__main__':
    main()
