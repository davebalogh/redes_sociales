import os
from project import app

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5555))
    app.run('0.0.0.0', port=port)