from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user, login_required, logout_user

from data import db_session
from data.jobs import Jobs
from data.users import User
from forms.registration import RegisterForm
from forms.login import LoginForm
from forms.jobs import JobsForm

db_session.global_init("db/mars_explorer.db")
db_sess = db_session.create_session()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@app.route("/")
def index():
    jobs = db_sess.query(Jobs).all()
    return render_template("works_log.html", title='Works Log', works=jobs)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Registration',
                                   form=form,
                                   message="Passwords don't match")
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


@login_manager.user_loader
def load_user(user_id):
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Authorization', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/addjob', methods=['GET', 'POST'])
def add_job():
    form = JobsForm()
    if form.validate_on_submit():
        if invalid_user_ids([form.team_lead.data]):
            return render_template('job_add.html',
                                   title='Adding a job',
                                   form=form,
                                   message=f"User with ID {form.team_lead.data} not found")

        collaborators_ids = [int(x) for x in form.collaborators.data.split(', ')]
        invalid_ids = invalid_user_ids(collaborators_ids)

        if invalid_ids:
            return render_template('job_add.html',
                                   title='Adding a job',
                                   form=form,
                                   message=f"Users with IDs {', '.join(invalid_ids)} not found")
        work = Jobs(
            team_leader=form.team_lead.data,
            job=form.title.data,
            work_size=form.work_size.data,
            collaborators=form.collaborators.data,
            is_finished=form.finished.data,
        )
        db_sess.add(work)
        db_sess.commit()
        return redirect("/")
    return render_template('job_add.html', title='Adding a job', form=form)


def invalid_user_ids(ids):
    invalid = [str(id1) for id1 in ids if not db_sess.query(User).get(id1)]
    return invalid if invalid else None


def main():
    app.run()


if __name__ == '__main__':
    main()
