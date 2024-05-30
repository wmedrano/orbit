import os
from quart import Quart

app = Quart(__name__)

@app.route('/')
async def index():
    return '<h1>Orbit</h1>'

def main():
    port = int(os.getenv('ORBIT_PORT', '8000'))
    app.run(port=port)

if __name__ == '__main__':
    main()
