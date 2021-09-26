from flask import Flask, render_template, redirect, url_for
from flask_cors import CORS, cross_origin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_admin import Admin
from flask_bootstrap import Bootstrap
from flask_admin.contrib.sqla import ModelView
from flask_login import UserMixin, LoginManager, current_user, login_user, login_required, logout_user

from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps

app = Flask(__name__, template_folder='templates')
cors = CORS(app)

#app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:Postgres2021@rnd-db.co9wfgdmnkpb.eu-west-3.rds.amazonaws.com/rnd_db"

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:Postgres2021@rnd-db.co9wfgdmnkpb.eu-west-3.rds.amazonaws.com/rnd-v01"
#app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:Postgres2021@rnd-db.co9wfgdmnkpb.eu-west-3.rds.amazonaws.com/rnd"
#app.config['SQLALCHEMY_DATABASE_URI'] ="postgresql://postgres:barca821997@localhost:5432/postgres"
#app.config['SQLALCHEMY_DATABASE_URI'] ="postgresql://postgres:barca821997@localhost:5432/rnd"

#app.config['SQLALCHEMY_DATABASE_URI'] ="postgresql://rnd:rnd@172.17.0.2:5432/postgres"


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisissecret'
app.config['CORS_HEADERS'] = 'Content-Type'
db = SQLAlchemy(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)
admin = Admin(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
Bootstrap(app)

class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=4, max=80)])
    remember = BooleanField('remember me')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(phone_number=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data) and user.admin:
                login_user(user, remember=form.remember.data)
                return redirect(url_for('admin.index'))

        return '<h1>Invalid username or password</h1>'
        #return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

from .models import (User, Wilaya, Commune, GlobalResult, Candidate, Partie, CandidateResult, PartieResult)

admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Wilaya, db.session))
admin.add_view(MyModelView(Commune, db.session))
admin.add_view(MyModelView(GlobalResult, db.session))
admin.add_view(MyModelView(Candidate, db.session))
admin.add_view(MyModelView(Partie, db.session))
admin.add_view(MyModelView(CandidateResult, db.session))
admin.add_view(MyModelView(PartieResult, db.session))

from .commune.routes import communes
from .reporter.routes import reporters
from .wilaya.routes import wilayas
from .user.routes import users
from .candidate.routes import candidates
from .partie.routes import parties
from .statistic.routes import statistics
from .national_result.routes import national
from .reporter_wilaya.routes import wilaya_reporter


app.register_blueprint(communes)
app.register_blueprint(reporters)
app.register_blueprint(wilayas)
app.register_blueprint(users)
app.register_blueprint(candidates)
app.register_blueprint(parties)
app.register_blueprint(statistics)
app.register_blueprint(national)
app.register_blueprint(wilaya_reporter)





