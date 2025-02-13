from flask import Flask , render_template,session,redirect,url_for,flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired
from flask_moment import Moment
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message
from threading import Thread

import os


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
moment = Moment(app)
migrate = Migrate(app, db)

 
app.config['SECRET_KEY'] = 'hard to guess'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir,'data.sqlite')
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_SUBJECT_PREFIX'] = '[FLASK_APP]'
app.config['FLASK_MAIL_SENDER'] = 'ADMIN <webdev.205120072@gmail.com>'
app.config['ADMIN'] = os.environ.get('ADMIN')


mail = Mail(app)

def send_async_email(app,msg):
    with app.app_context():
        mail.send(msg)

def send_mail(to,subject,template,**kwargs):
    msg=Message(app.config['MAIL_SUBJECT_PREFIX']+subject,sender=app.config['FLASK_MAIL_SENDER'],recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email,args=[app,msg])
    thr.start()
    return thr
    #mail.send(msg)


'''class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),unique=True)
    users = db.relationship('User',backref='role',lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name'''


class User(db.Model):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key =True)
    username = db.Column(db.String(64),unique=True,index=True)
    #role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


class NameForm(FlaskForm):
    name = StringField('What is your name??' , validators=[DataRequired()])
    submit = SubmitField('submit')

@app.route('/',methods=['GET' , 'POST'])
#@app.route('/')
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known']=False
            if app.config['ADMIN']:
                send_mail(app.config['ADMIN'],'New User','mail/new_user',user=user)
        else:
            session['known'] = True
        session['name']=form.name.data        
        form.name.data = ''
        flash('Thanks for submitting data!!')
        return redirect(url_for('index'))
    #return '<h1>Hello Everyone!!!</h1>'
    return render_template('index.html',name=session.get('name') , form=form, known=session.get('known',False))

@app.route('/user/<name>')

def user(name):
    l=[]
    for i in range (10):
        l.append(i)
    var={
        'name':name,
        'list':l
        }
    return '<h1>Hello , {} !!</h1>'.format(name)
    name={'name':name}
    return render_template('user.html' , context=var, name=name)


@app.errorhandler(404)
def page_not_found(e):
        return render_template('404.html') , 404

@app.errorhandler(500)
def internal_server_error(e):
        return render_template('500.html') , 500

@app.shell_context_processor
def make_shell_context():
    return dict(db=db,User=User,Role=Role)