from flask import Flask

app = Flask(__name__)

@app.route('/telegram')
def telegram():
    return 'telegram'

app.run('0.0.0.0', port=5555)