from flask import Flask, render_template, redirect, request, abort, make_response, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy import or_

from data import db_session, jobs_api
from data.category import HazardCategory
from data.departments import Department
from data.jobs import Jobs
from data.users import User
from forms.departments import DepartmentsForm
from forms.jobs import JobsForm
from forms.login import LoginForm
from forms.registration import RegisterForm

db_session.global_init("db/mars_explorer.db")
db_sess = db_session.create_session()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


@app.route("/")
def index():
    jobs = db_sess.query(Jobs).order_by(Jobs.id).all()
    numbered_jobs = list(enumerate(jobs, start=1))
    return render_template("works_log.html", title='Works Log', works=numbered_jobs)


@app.route("/departments")
def departments():
    deps = db_sess.query(Department).order_by(Department.id).all()
    numbered_deps = list(enumerate(deps, start=1))
    return render_template("departments.html", title='List of Departments', deps=numbered_deps)


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
    form.hazard_category.choices = [
                                       (0, 'No category')] + [
                                       (c.id, f"{c.name} (Level {c.level})")
                                       for c in db_sess.query(HazardCategory).order_by(HazardCategory.level)
                                   ]
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
        hazard_category = None
        if form.hazard_category.data != 0:
            hazard_category = db_sess.get(HazardCategory, form.hazard_category.data)
        work = Jobs(
            team_leader=form.team_lead.data,
            job=form.title.data,
            work_size=form.work_size.data,
            collaborators=form.collaborators.data,
            is_finished=form.finished.data,
            hazard_category=hazard_category
        )

        db_sess.add(work)
        db_sess.commit()
        return redirect("/")
    return render_template('job_add.html', title='Adding a job', form=form)


def invalid_user_ids(ids):
    invalid = [str(id1) for id1 in ids if not db_sess.query(User).get(id1)]
    return invalid if invalid else None


@app.route('/editjob/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_job(id):
    form = JobsForm()
    if request.method == "GET":
        job = db_sess.query(Jobs).filter(
            Jobs.id == id,
            or_(
                Jobs.user == current_user,
                current_user.id == 1
            )
        ).first()
        if job:
            form.title.data = job.job
            form.team_lead.data = job.team_leader
            form.work_size.data = job.work_size
            form.collaborators.data = job.collaborators
            form.finished.data = job.is_finished
        else:
            abort(404)
    if form.validate_on_submit():
        job = db_sess.query(Jobs).filter(
            Jobs.id == id,
            or_(
                Jobs.user == current_user,
                current_user.id == 1
            )
        ).first()
        if job:
            job.job = form.title.data
            job.team_leader = form.team_lead.data
            job.work_size = form.work_size.data
            job.collaborators = form.collaborators.data
            job.is_finished = form.finished.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('job_add.html',
                           title='Editing a job',
                           form=form
                           )


@app.route('/deletejob/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_job(id):
    job = db_sess.query(Jobs).filter(
        Jobs.id == id,
        or_(
            Jobs.user == current_user,
            current_user.id == 1
        )
    ).first()
    if job:
        db_sess.delete(job)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/adddepartment', methods=['GET', 'POST'])
def add_department():
    form = DepartmentsForm()
    if form.validate_on_submit():
        if invalid_user_ids([form.chief.data]):
            return render_template('department_add.html',
                                   title='Adding a department',
                                   form=form,
                                   message=f"User with ID {form.chief.data} not found")

        members_ids = [int(x) for x in form.members.data.split(', ')]
        invalid_ids = invalid_user_ids(members_ids)

        if invalid_ids:
            return render_template('department_add.html',
                                   title='Adding a department',
                                   form=form,
                                   message=f"Users with IDs {', '.join(invalid_ids)} not found")
        dep = Department(
            chief=form.chief.data,
            title=form.title.data,
            members=form.members.data,
            email=form.email.data,
        )
        db_sess.add(dep)
        db_sess.commit()
        return redirect("/departments")
    return render_template('department_add.html', title='Adding a department', form=form)


@app.route('/editdepartment/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_department(id):
    form = DepartmentsForm()
    if request.method == "GET":
        department = db_sess.query(Department).filter(
            Department.id == id,
            or_(
                Department.chief == current_user.id,
                current_user.id == 1,
            )
        ).first()
        if department:
            form.title.data = department.title
            form.chief.data = department.chief
            form.members.data = department.members
            form.email.data = department.email
        else:
            abort(404)
    if form.validate_on_submit():
        department = db_sess.query(Department).filter(
            Department.id == id,
            or_(
                Department.chief == current_user.id,
                current_user.id == 1,
            )
        ).first()
        if department:
            department.title = form.title.data
            department.chief = form.chief.data
            department.members = form.members.data
            department.email = form.email.data
            db_sess.commit()
            return redirect('/departments')
        else:
            abort(404)
    return render_template('department_add.html', title='Editing a department', form=form)


@app.route('/deletedepartment/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_department(id):
    department = db_sess.query(Department).filter(
        Department.id == id,
        or_(
            Department.chief == current_user.id,
            current_user.id == 1,
        )
    ).first()
    if department:
        db_sess.delete(department)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/departments')


def main():
    app.register_blueprint(jobs_api.blueprint)
    app.run()


if __name__ == '__main__':
    main()
