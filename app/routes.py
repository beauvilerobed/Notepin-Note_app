from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm
from flask_login import current_user, login_user
from app.models import User
from flask_login import logout_user
from flask_login import login_required
from flask import request
from werkzeug.urls import url_parse
from app import db
from app.forms import RegistrationForm
from app.forms import PostForm
from app.forms import PostForm1
from app.models import Post

#//Post submission form 
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        #  Post/Redirect/Get pattern. It avoids inserting duplicate posts 
        #  when a user inadvertently refreshes the page after submitting 
        #  a web form.
        return redirect(url_for('index'))

    # #return value being a list with all the results.
    # posts = current_user.followed_posts().all()
    # return render_template('index.html', title='Home Page', form=form, posts=posts)

    # #add pagination to the home view
    # page = request.args.get('page', 1, type=int)
    # posts = current_user.followed_posts().paginate(
    #     page, app.config['POSTS_PER_PAGE'], False)
    # #next and previous page link
    # next_url = url_for('index', page=posts.next_num) \
    #     if posts.has_next else None
    # prev_url = url_for('index', page=posts.prev_num) \
    #     if posts.has_prev else None
    return render_template('index.html', title='Home', form=form)



#//end of submission form

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirct(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congradulation, you are now a registered user! Feel free to explore!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    #//Pagination in the user profile view function
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)
    #end of pagingation//

from datetime import datetime

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

from app.forms import EditProfileForm

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)#use fixed issue1 (found in forms.py)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

# #//follow and unfollow routes
# @app.route('/follow/<username>')
# @login_required
# def follow(username):
#     user = User.query.filter_by(username=username).first()
#     if user is None:
#         flash('User {} not found.'.format(username))
#         return redirect(url_for('index'))
#     if user == current_user:
#         flash('You cannot follow yourself!')
#         return redirect(url_for('user', username=username))
#     current_user.follow(user)
#     db.session.commit()
#     flash('You are following {}!'.format(username))
#     return redirect(url_for('user', username=username))


# @app.route('/unfollow/<username>')
# @login_required
# def unfollow(username):
#     user = User.query.filter_by(username=username).first()
#     if user is None:
#         flash('User {} not found.'.format(username))
#         return redirect(url_for('index'))
#     if user == current_user:
#         flash('You cannot unfollow yourself!')
#         return redirect(url_for('user', username=username))
#     current_user.unfollow(user)
#     db.session.commit()
#     flash('You are not following {}.'.format(username))
#     return redirect(url_for('user', username=username))
# #end of follow and unfollow routes//

# #//show global post stream from all users
# @app.route('/explore')
# @login_required
# def explore():
#     #add pagination to the explore page
#     page = request.args.get('page', 1, type=int)
#     posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, 
#         app.config['POSTS_PER_PAGE'], False)
#     #next and previous page link
#     next_url = url_for('explore', page=posts.next_num) \
#         if posts.has_next else None
#     prev_url = url_for('explore', page=posts.prev_num) \
#         if posts.has_prev else None
#     return render_template("index.html", title='Explore', 
#         posts=posts.items, next_url=next_url, prev_url=prev_url)
#     #end of addition
# #end of show//

# # //delete a post
# @app.route('/delete/<int:id>')
# def delete(id):
#     task_to_delete = Post.query.get_or_404(id)

#     try:
#         db.session.delete(task_to_delete)
#         db.session.commit()
#         return redirect('/')

#     except:
#         return 'There was a problem deleting that task'
# # end of delete//

@app.route('/delete/<int:id>/<username>')
@login_required
def delete(id, username):
    task_to_delete = Post.query.get_or_404(id)
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    else: 
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect(url_for('user', username=username))
#end of follow and unfollow routes//

@app.route('/update/<int:id>/<username>', methods=['GET', 'POST'])
def update(id, username):
    task = Post.query.get_or_404(id)

    if request.method == 'POST':
        task.body = request.form['content']

        try:
            db.session.commit()
            return redirect(url_for('user', username=username))
        except:
            return 'there was an issue updating your task'

    else:
        return render_template('update.html', task=task)

