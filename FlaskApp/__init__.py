from flask import Flask, render_template, flash, request, url_for, redirect, session

from content_management import Content

from wtforms import Form, BooleanField, TextField, PasswordField, validators
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
import gc, os
from dbconnect import connection

from functools import wraps

import traceback
import logging
from logging.handlers import RotatingFileHandler

from flask_mail import Mail, Message
from flask import send_file, send_from_directory, jsonify
import pygal

logger = logging.getLogger(__name__)
file_handler = RotatingFileHandler("/var/www/FlaskApp/FlaskApp/flask.log", maxBytes=100 * 1024 * 1024, backupCount=5)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


TOPIC_DICT= Content()

app = Flask(__name__, instance_path = '/var/www/FlaskApp/FlaskApp/protected')

app.config.update(
    DEBUG=True,
    #EMAIL SETTINGS
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='zhonghua00700@gmail.com',
    MAIL_PASSWORD='zhong00700**'
    )
mail = Mail(app)


@app.route('/send-mail/')
def send_mail():
    try:
        msg = Message("Send Mail",
                      sender ="zhonghua00700@gmail.com",
                      recipients=["yaozhonghui@secoo.com"])
        msg.body = "Yo!\nHave you heard the good word of Python?"
        mail.send(msg)
        return 'Mail sent!'
    except Exception as e:
        return str(e)

@app.route('/file-downloads/')
def file_downloads():
    try:
        return render_template('download.html')
    except Exception as e:
        return str(e)

@app.route('/return-files/')
def return_files():
    try:
        return send_file('/var/www/FlaskApp/FlaskApp/static/images/index.png', attachment_filename='index.png')
    except Exception as e:
        return str(e)

def special_requirement(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        try:
            if  'lord' == session['username']:
                return f(*args, **kwargs)
            else:
                return"You have no authority to access!"
        except Exception as e:
            flash("please login first!")
            return redirect(url_for('dashboard'))
    return wrap


@app.route('/secret/<path:filename>')
@special_requirement
def protected(filename):
    try:
        return send_from_directory(os.path.join(app.instance_path,''), filename)
    except Exception as e:
        return redirect(url_for('homepage'))

@app.route('/interactive/')
def interacive():
    try:
        return render_template('interactive.html')
    except Exception as e:
        return str(e)

@app.route('/background_process')
def background_process():
    try:
        lang = request.args.get('proglang')
        if str(lang).lower() == 'python':
            return jsonify(result='You are wise!')
        else:
            return jsonify(result='Try again!')
    except Exception, e:
        return(str(e))


@app.route('/pygal/')
def pygalexample():
    try:
        graph = pygal.Line()
        graph.title = '% Change Coolness of programming languages over time.'
        graph.x_labels = ['2011','2012','2013','2014','2015','2016']
        graph.add('Python',  [15, 31, 89, 200, 356, 900])
        graph.add('Java',    [15, 45, 76, 80,  91,  95])
        graph.add('C++',     [5,  51, 54, 102, 150, 201])
        graph.add('All others combined!',  [5, 15, 21, 55, 92, 105])
        graph_data=graph.render_data_uri()  # Return `data:image/svg+xml;charset=utf-8;base64,...`
        return render_template("graphing.html", graph_data=graph_data)
    except Exception, e:
        return(str(e))

@app.route('/<path:urlpath>', methods=['GET', 'POST'])
@app.route('/')
def homepage(urlpath='/'):
    return render_template("main.html")
    #return "hello world"


@app.route('/dashboard/')
def dashboard():
    flash("welcome!")
    return render_template("dashboard.html", TOPIC_DICT = TOPIC_DICT)
    

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

@app.route('/slashboard/')
def slashboard():
    try:
        return render_template("dashboard.html", TOPIC_DICT = TOPIC)
    except Exception as e:
        return render_template("500.html", error=e)

@app.route('/message/')
def message():
    try:
        replies = {'Jack': 'Cool post',
                   'June': '+1',}
        return render_template("message.html", replies = replies)
    except Exception, e:
        return(str(e))

    

@app.route('/jinja/')
def jinjaexample():
    try:
        gc.collect()
        data = [15, '15', 'Python is good', 'Paython, Java, PHP, SQL, C++', '<p><strong>Hey there!</strong></p>']
        return render_template("jinja.html", data = data)
    except Exception, e:
        return(str(e))

@app.route('/converters/')
@app.route('/converters/<int:page>')
def converter(page=1):
    try:
        gc.collect()
        return render_template("converter.html", page = page)
    except Exception, e:
        return(str(e))

    

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first!")
            return redirect(url_for('homepage'))
    return wrap

@app.route('/logout/')
@login_required
def logout():
    session.clear()
    flash("You have been logged out!")
    gc.collect()
    return redirect(url_for('dashboard'))


@app.route('/login/', methods=['GET', 'POST'])
def login_page():
    error = None
    try:
        c, conn = connection()
        if request.method == "POST":
            logger.info(thwart(request.form['username']))
            
            data = c.execute("SELECT * FROM users WHERE username = (%s)",
                             (thwart(request.form['username']),))
            if int(data) == 0:
                error = "No such user!"
                return render_template("login.html", error = error)
            data = c.fetchone()[2]
                
            if sha256_crypt.verify(request.form['password'], data):
                session['logged_in'] = True
                session['username'] = request.form['username']

                flash("You are now logged in")
                return redirect(url_for("dashboard"))
            else:
                error = "Invalid credentials, try again."
        
        gc.collect()

        return render_template("login.html", error = error)
            
    except Exception as e:
        flash(e)
        return render_template("login.html", error = error)        


class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=25)])
    email = TextField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the TOS', [validators.Required()])



@app.route('/register/', methods=["GET","POST"])
def register_page():
    try:
        form = RegistrationForm(request.form)

        if request.method == "POST" and form.validate():
            username  = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt((str(form.password.data)))
            c, conn = connection()

            x = c.execute("SELECT * FROM users WHERE username = (%s)",
                          (thwart(username),))

            if int(x) > 0:
                flash("That username is already taken, please choose another")
                return render_template('register.html', form=form)

            else:
                c.execute("INSERT INTO users (username, password, email, tracking) VALUES (%s, %s, %s, %s)",
                          (thwart(username), thwart(password), thwart(email), thwart("/dashboard/")))
                logger.info('excuted...')
                conn.commit()
                flash("Thanks for registering!")
                c.close()
                conn.close()
                gc.collect()

                session['logged_in'] = True
                session['username'] = username

                return redirect(url_for('dashboard'))

        return render_template("register.html", form=form)

    except Exception as e:
        return(traceback.format_exc())
		
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)


