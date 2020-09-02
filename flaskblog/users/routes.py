from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog import db
from hashlib import md5
from flaskblog.models import User, Post
from flaskblog.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                   RequestResetForm, ResetPasswordForm)
from flaskblog.users.utils import save_picture, send_email

users = Blueprint('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def register():
  if current_user.is_authenticated:
    return redirect(url_for('main.home'))
  form = RegistrationForm()
  if form.validate_on_submit():
    hashed_password = md5(form.password.data.encode()).hexdigest()
    user = User(username=form.username.data, email=form.email.data, password=hashed_password)
    db.session.add(user)
    db.session.commit()
    flash(f"Account created for {form.username.data} !!", 'success')
    return redirect(url_for('users.login'))
  return render_template('register.html', title="Register", form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
    return redirect(url_for('main.home'))
  form = LoginForm()
  if form.validate_on_submit():
    user = User.query.filter_by(email=form.email.data).first()
    if not user:
      flash(f"Login Failed! Please check Username or Password", 'danger')
      return redirect(url_for('users.login'))
    isMatching = user.password == md5(form.password.data.encode()).hexdigest()
    if user and isMatching:
      login_user(user, remember=form.remeber.data)
      guess_page = request.args.get('next')
      if guess_page:
        return redirect(guess_page)
      else:
        return redirect(url_for('main.home'))
    else:
      flash(f"Login Failed! Please check Username or Password", 'danger')

  return render_template('login.html', title="Login", form=form)


@users.route('/logout')
def logout():
  logout_user()
  return redirect(url_for('main.home'))


@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
  form = UpdateAccountForm()

  if form.validate_on_submit():
    if form.picture.data:
      old_pic = current_user.image_file
      profile_path = save_picture(form.picture.data)
      if old_pic != 'default.jpg':
        os.remove(os.path.join(app.root_path,'static/icon',old_pic))
      print(profile_path)
      current_user.image_file = profile_path
    current_user.username = form.username.data
    current_user.email = form.email.data
    db.session.commit()
    flash(f"Account has been updated sucessfully..!!", 'success')
    return redirect(url_for('users.account'))
  elif request.method == 'GET':
    form.username.data = current_user.username
    form.email.data = current_user.email
  image_file = url_for('static', filename='icon/' + current_user.image_file)
  return render_template('account.html', title="My Account", image_file=image_file, form=form)


@users.route('/user/<string:username>')
def user_post(username):
  page = request.args.get('page', 1, type=int)
  user = User.query.filter_by(username=username).first_or_404()
  posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(per_page=5)
  return render_template('user_post.html', posts=posts, user=user)


@users.route('/reset_password/', methods=['GET', 'POST'])
def reset_request():
  if current_user.is_authenticated:
    return redirect(url_for('main.home'))
  form = RequestResetForm()
  if form.validate_on_submit():
    user = User.query.filter_by(email=form.email.data).first()
    send_email(user)
    flash(f"An email has been sent with instructions to reset your password.", 'info')
    return redirect(url_for('users.login'))
  return render_template('reset_request.html', title="Reset password request", form=form, legend='Request for reset password')


@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
  if current_user.is_authenticated:
    return redirect(url_for('main.home'))
  user = User.verify_reset_token(token)
  if not user:
    flash(f"That is an invalid or expire token", 'warning')
    return redirect(url_for('users.reset_password'))
  form = ResetPasswordForm()
  if form.validate_on_submit():
    hashed_password = md5(form.password.data.encode()).hexdigest()
    user.password = hashed_password
    db.session.commit()
    flash(f"Your password has been updated", 'success')
    return redirect(url_for('users.login'))
  return render_template('reset_token.html', title="Reset Password", form=form, legend='Reset Your Password')
