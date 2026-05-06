from flask import Flask
from models import db, User, Task, BLOCKS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///arete.sqlite'
db.init_app(app)


@app.route("/")
def test():
    return "YANDEX"

def main():
    app.run(host="127.0.0.1", port=8080, debug=True)


if __name__ == '__main__':
    main()