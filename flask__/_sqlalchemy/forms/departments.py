from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, StringField, EmailField
from wtforms.validators import DataRequired, Regexp


class DepartmentsForm(FlaskForm):
    title = StringField('Department Title', validators=[DataRequired()])
    chief = IntegerField("Department Chief ID", validators=[DataRequired()])
    members = StringField("Members",
                          validators=[DataRequired(),
                                      Regexp(r'^\d+(?:, \d+)*$', message="Формат: '1, 2, 3' "
                                                                         "(обязателен пробел после запятой)")])
    email = EmailField('Department email', validators=[DataRequired()])
    submit = SubmitField('Submit')
