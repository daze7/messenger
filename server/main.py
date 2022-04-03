import os, sqlite3

from flask import Flask

app = Flask(__name__)

data = {
    'structure': ['user_id', 'user_info']
}



@app.route("/help")
def help():
    return 'Помощь', data['structure']


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)