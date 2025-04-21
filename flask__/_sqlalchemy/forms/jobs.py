from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField, IntegerField, StringField
from wtforms.validators import DataRequired, Regexp


class JobsForm(FlaskForm):
    title = StringField('Job Title', validators=[DataRequired()])
    team_lead = IntegerField("Team Leader ID", validators=[DataRequired()])
    work_size = IntegerField("Work Size", validators=[DataRequired()])
    collaborators = StringField("Collaborators",
                                validators=[DataRequired(),
                                            Regexp(r'^\d+(?:, \d+)*$', message="Формат: '1, 2, 3' "
                                                                               "(обязателен пробел после запятой)")])
    finished = BooleanField("Is Job Finished?")
    submit = SubmitField('Submit')
