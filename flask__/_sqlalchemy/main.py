from flask import Flask, render_template

from data import db_session
from data.jobs import Jobs
from data.users import User

import datetime

db_session.global_init("db/mars_explorer.db")
db_sess = db_session.create_session()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'



@app.route("/")
def index():
    jobs = db_sess.query(Jobs).all()
    return render_template("works_log.html", works=jobs)


def main():
    app.run()


if __name__ == '__main__':
    main()
