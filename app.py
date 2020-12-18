from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import RegisterUserForm, LoginForm, FeedbackForm
from secrets import SECRET_KEY
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flask_feedback_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
toolbar = DebugToolbarExtension(app)


@app.route('/')
def go_to_register():
    return redirect('/register')

@app.route('/register')
def show_register_form():
    form = RegisterUserForm()
    return render_template('register.html', form=form)

@app.route('/register', methods=['POST'])
def register_user():
    form = RegisterUserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first = form.first_name.data
        last = form.last_name.data

        new_user = User.register(username, password, email, first, last)

        db.session.add(new_user)

        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken. Please choose another')
            return render_template('register.html', form=form)

        session['user'] = new_user.username
        flash('Your Account Was Created Successfully!', 'success')
        return redirect(f'/users/{new_user.username}')

    return render_template('register.html', form=form)

@app.route('/login')
def show_login_form():
    form = LoginForm()
    return render_template('login.html', form=form)

@app.route('/login', methods=['POST'])
def Login_user():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            flash(f"Welcome Back, {user.username}!", "primary")
            session['user'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invaild username/password.']

    return render_template('login.html', form=form)

@app.route('/users/<username>')
def secret_page(username):
    if "user" not in session:
        flash('Please login first!', 'danger')
        return redirect('/')
    
    user = User.query.get(f'{username}')
    
    return render_template('user_info.html', user=user)

@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    """Delete user."""
    user = User.query.get(f'{username}')
    if user.username == session['user']:
        db.session.delete(user)
        db.session.commit()
        flash("User deleted!", "info")
        return redirect('/')
    flash("You do not have permission to do that!", "danger")
    return redirect(f'/users/{username}')

@app.route('/users/<username>/feedback/add')
def add_feedback_form(username):
    """Form for user to add feedback."""
    user = User.query.get(f'{username}')
    form = FeedbackForm()

    return render_template('feedback_form.html', form=form)

@app.route('/users/<username>/feedback/add', methods=['POST'])
def submit_feedback(username):
    """Handle and add feedback."""
    user = User.query.get(f'{username}')
    form = FeedbackForm()
    if user.username == session['user']:
        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data
            new_fb = Feedback(title=title, content=content, author=session['user'])
            db.session.add(new_fb)
            db.session.commit()
            flash('Feedback Created!', 'success')
            return redirect(f'/users/{username}')

    return render_template('feedback_form.html', form=form)

@app.route('/feedback/<int:feedback_id>/update')
def update_feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)
    form = FeedbackForm()
    return render_template('edit_feedback.html', feedback=feedback, form=form)

@app.route('/logout')
def logout_user():
    session.pop('user')
    flash('Goodbye, come back again!', 'info')
    return redirect('/')