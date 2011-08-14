from tipfy.ext.wtforms import Form, fields, validators

REQUIRED = validators.required()


#===============================================================================
class LoginForm(Form):
    username = fields.TextField('Username', validators=[REQUIRED])
    password = fields.PasswordField('Password', validators=[REQUIRED])
    remember = fields.BooleanField('Keep me signed in')


#===============================================================================
class SignupForm(Form):
    nickname = fields.TextField('Nickname', validators=[REQUIRED])


#===============================================================================
class RegistrationForm(Form):
    username = fields.TextField('Username', validators=[REQUIRED])
    password = fields.PasswordField('Password', validators=[REQUIRED])
    password_confirm = fields.PasswordField('Confirm the password', validators=[REQUIRED])
