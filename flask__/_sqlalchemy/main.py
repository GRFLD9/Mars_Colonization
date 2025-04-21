from flask import Flask, render_template, redirect

from data import db_session
from data.departments import Department
from data.jobs import Jobs
from data.users import User
from forms.user import RegisterForm

db_session.global_init("db/mars_explorer.db")
db_sess = db_session.create_session()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

department = db_sess.query(Department).filter(Department.id == 1).first()
users = db_sess.query(User).filter(User.id.in_(str(department.members).split(', '))).all()
for user in set(users):
    user_works = db_sess.query(Jobs).filter(
        (Jobs.collaborators.contains(str(user.id))) | (Jobs.team_leader == user.id)).all()
    s = 0
    for work in user_works:
        tdlt = (work.end_date - work.start_date)
        s += tdlt.total_seconds() / 3600
    if s > 25:
        print(user.surname, user.name)


@app.route("/")
def index():
    jobs = db_sess.query(Jobs).all()
    return render_template("works_log.html", works=jobs)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Registration',
                                   form=form,
                                   message="Passwords don't match")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Registration',
                                   form=form,
                                   message="This email is already registered")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            address=form.address.data,
            email=form.email.data,
            age=form.age.data,
            position=form.position.data,
            speciality=form.speciality.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Registration', form=form)


def main():
    app.run()


if __name__ == '__main__':
    main()
