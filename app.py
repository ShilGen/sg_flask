from flask import Flask
from flask import session, request, redirect, render_template, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.csrf import CSRFProtect, CSRFError


app = Flask(__name__)
# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['TESTING'] = True
csrf = CSRFProtect(app)

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    submit = SubmitField("Login")

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('csrf_error.html', reason=e.description), 400


@app.route("/")
def index():
    if "username" in session:
        return f'Logged in as {session["username"]}  <br><a href="/logout">go to</a>'
    return 'You are not logged <br><a href="/login">go to</a>'


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session["username"] = request.form["username"]
        return redirect(url_for("index"))
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    # remove the username from the session if it's there
    session.pop("username", None)
    return redirect(url_for("index"))
