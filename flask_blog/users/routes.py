from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from flask_blog import db, bcrypt
from flask_blog.models import User, Post
from flask_blog.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                   RequestResetForm, ResetPasswordForm)
from flask_blog.users.utils import save_picture, send_reset_email

users = Blueprint('users', __name__)

# register user should allow user to register for an account
# if there is a user logged in already, it should return to home page
@users.route("/register", methods=['GET', 'POST'])
def register():
    # check if there's a user logged in already
    # return to the home page if there is, else continue
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    # grab our registration form
    form = RegistrationForm()

    # check that our form is valid after it is submitted
    # make sure that we only save the hashed pw
    # redirect user to the login page for them to log in after successful registration
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created {form.username.data}!', 'success')
        return redirect(url_for('users.login'))
    return render_template("register.html", title = "Register", form = form)


# log in page should allow existing users to log in
# if the user is already logged in we should redirect them to the home page
@users.route("/login", methods=['GET', 'POST'])
def login():
    # check whether there already is a logged in user
    # if there is, go home, else continue
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    # make sure we grab the log in form
    form = LoginForm()

    # check that the form is valid when the submit button is hit
    if form.validate_on_submit():
        # if the email isn't in the database the user doesn't exist
        user = User.query.filter_by(email=form.email.data).first()

        # if the user exists, the hashed passwords need to match
        # if the user doesn't exist, tell them that their account was not found
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(url_for(next_page)) if next_page else redirect(url_for('main.home'))
        else:
            flash('Account not found', 'danger')
    return render_template("login.html", title = "Log In", form = form)

# logout is handled by flask #litty #easymoney
@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

# allows updating the account username and email
# the user must be logged in for this to be accessible
@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    # grab the update account form
    form = UpdateAccountForm()

    # check to make sure fields are valid and save to db
    # on loading the page, populate the fields with the current data
    if form.validate_on_submit():
        # if there was a picture uploaded, call our save_picture function
        if form.picture.data:
            picture_fn = save_picture(form.picture.data)
            current_user.image = picture_fn
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account information has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image = url_for('static', filename='headshots/' + current_user.image)
    return render_template("account.html", title = "Account", image = image, form = form)

# loads all the posts belonging to a single user with pagination
@users.route("/user/<string:username>/posts")
def user_posts(username):
    # we gotta know which page we're on, and we start on 1 by default
    page = request.args.get('page', 1, type=int)

    # make sure the user exists
    user = User.query.filter_by(username=username).first_or_404()

    # load the posts with up to 5 posts per page
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template("user_posts.html", posts = posts, user = user)

# request a password reset
@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    # if the user is logged in then there's no need for a password reset
    # redirect them to the home page
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    # grab the form we want to show
    form = RequestResetForm()
    
    # grab our user by email
    # send them an email
    # redirect them to login
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been sent with instructions to reset password", "info")
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form = form)

# actually reset the password
@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    # check if the user is logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    # verify the token
    # if the token is invalid/expired redirect them to another password reset
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_pw
        db.session.commit()
        flash(f'Your password has been updated {form.username.data}!', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_password.html', title='Reset Password', form = form)