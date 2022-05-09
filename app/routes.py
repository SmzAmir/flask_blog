from flask import render_template, request, redirect, flash, url_for
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, PostForm
from app.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime


@app.before_request
def before_request():
    # user is already logged in:
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    else:
        pass


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    post_form = PostForm()
    if request.method == 'GET':
        # posts = Post.query.filter_by(author=current_user).all()
        page = request.args.get('page', default=1, type=int)
        posts = current_user.followed_posts().paginate(
            page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False
        )

        if posts.has_next:
            next_url = url_for('index', page=posts.next_num)
        else:
            next_url = None
        if posts.has_prev:
            previous_url = url_for('index', page=posts.prev_num)
        else:
            previous_url = None

        return render_template(template_name_or_list='index.html', title='Home', posts=posts.items, form=post_form,
                               next_url=next_url, previous_url=previous_url)

    elif request.method == 'POST':
        if post_form.validate_on_submit():
            post = Post(body=post_form.post.data, author=current_user)
            db.session.add(post)
            db.session.commit()
            flash('Your post is now live!', category='success')
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))


@app.route('/explore', methods=['GET', 'POST'])
@login_required
def explore():
    if request.method == 'GET':
        page = request.args.get('page', default=1, type=int)
        posts = current_user.followed_posts().paginate(
            page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False
        )

        if posts.has_next:
            next_url = url_for('index', page=posts.next_num)
        else:
            next_url = None
        if posts.has_prev:
            previous_url = url_for('index', page=posts.prev_num)
        else:
            previous_url = None

        return render_template(template_name_or_list='index.html', title='Home', posts=posts.items,
                               next_url=next_url, previous_url=previous_url)

    elif request.method == 'POST':
        return redirect(url_for('index'))

    else:
        return redirect(url_for('index'))


# Registration ---------------------------------------------------------------------------------------------------------
@app.route('/register', methods=['POST', 'GET'])
def registration():
    try:
        registration_form = RegistrationForm()

        # User login view:
        if request.method == 'GET':

            # user is already logged in:
            if current_user.is_authenticated:
                return redirect(location=url_for('index'))

            # user not logged in:
            else:
                return render_template(template_name_or_list='registration.html', title='Registration', form=registration_form)

        # User registration request:
        elif request.method == 'POST':

            # Valid registration:
            if registration_form.validate_on_submit():

                user = User(username=registration_form.username.data, email=registration_form.email.data)
                user.set_password(registration_form.password.data)
                db.session.add(user)
                db.session.commit()

                flash(message='Registration Successful!', category='success')
                return redirect(location=url_for('login'))

            # Failed registration:
            else:
                flash(message='Failed to register! Check for error messages!', category='danger')
                return redirect(location=url_for('registration', title='Registration', form=registration_form))

        # Invalid request:
        else:
            flash('Failed to register! Check for error messages!')
            return redirect(location=url_for('registration', title='Registration', form=registration_form))

    except Exception as e:
        print('Registeration Err:', e)


# Login ---------------------------------------------------------------------------------------------------------
@app.route('/login', methods=['POST', 'GET'])
def login():
    login_form = LoginForm()

    # User login view:
    if request.method == 'GET':

        # user is already logged in:
        if current_user.is_authenticated:
            flash(message='You have already logged in!', category='primary')
            return redirect(location=url_for('index'))

        # user not logged in:
        else:

            return render_template(template_name_or_list='login.html', title='Sign In', form=login_form)

    # User login submit:
    elif request.method == 'POST':

        # Valid login:
        if login_form.validate_on_submit():

            user = User.query.filter_by(username=login_form.username.data).first()

            # if user object does not exist or password is not correct
            if user is None or not user.check_password(login_form.password.data):
                flash(message='Invalid Username or password!', category='danger')
                return redirect(location=url_for('login'))

            # if user exists and password is correct
            else:
                # register the user in the session
                login_user(user=user, remember=login_form.remember_me.data)
                flash(message='Login Successful!', category='success')

                # if the user comes from an exiting page redirect the user to that page
                next_page = request.args.get('next')

                if not next_page or url_parse(next_page).netloc != '':
                    return redirect(location=url_for('index'))
                else:
                    return redirect(location=next_page)

        # Failed login:
        else:
            flash(message='Invalid Username or password!', category='danger')
            return redirect(url_for('login', title='Sign In', form=login_form))
    else:
        flash('Invalid Username or password!')
        return redirect(url_for('login', title='Sign In', form=login_form))


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(location=url_for('login'))


@app.route('/profile/<username>', methods=['GET'])
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    form = EmptyForm()
    # Check if the username belongs to the user
    if request.method == 'GET':

        page = request.args.get('page', default=1, type=int)
        posts = user.posts.order_by(Post.timestamp.desc()).paginate(
            page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False
        )

        if posts.has_next:
            next_url = url_for('index', page=posts.next_num)
        else:
            next_url = None
        if posts.has_prev:
            previous_url = url_for('index', page=posts.prev_num)
        else:
            previous_url = None

        return render_template(template_name_or_list='profile.html', title='Profile', user=user, posts=posts.items, form=form,
                               next_url=next_url, previous_url=previous_url)
    else:
        flash(message='Something went wrong!', category='danger')
        return redirect(location=url_for('index'))


@app.route('/profile/edit', methods=['POST', 'GET'])
@login_required
def edit_profile():
    edit_profile_form = EditProfileForm(original_username=current_user.username)
    # user is already logged in:
    if current_user.is_authenticated:

        # User edit profile view:
        if request.method == 'GET':

            # Set the current information on the form
            edit_profile_form.username.data = current_user.username
            edit_profile_form.about_me.data = current_user.about_me
            return render_template(template_name_or_list='edit_profile.html', title='Edit Profile', form=edit_profile_form)

        # User registration request:
        elif request.method == 'POST':

            # Valid registration:
            if edit_profile_form.validate_on_submit():
                current_user.username = edit_profile_form.username.data
                current_user.about_me = edit_profile_form.about_me.data
                db.session.commit()
                flash(message='Profile Updated Successfully!', category='success')
                return redirect(url_for('profile', username=current_user.username))

            # Failed registration:
            else:
                flash(message='Profile Update Failed!', category='danger')
                return redirect(url_for('edit_profile', title='Edit Profile', form=edit_profile_form))

    else:
        flash(message='You need to login first!', category='danger')
        return render_template(template_name_or_list='login.html')


@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    if request.method == 'POST':
        form = EmptyForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=username).first()
            if user is None:
                flash('User {} not found.'.format(username), category='danger')
                return redirect(url_for('index'))
            elif user == current_user:
                flash('You cannot follow yourself!', category='danger')
                return redirect(url_for('profile', username=username))
            else:
                current_user.follow(user)
                db.session.commit()
                flash('You are now following {}.'.format(username), category='success')
                return redirect(url_for('profile', username=username))
        else:
            flash(message='Something went wrong!', category='danger')
            return render_template(url_for('index'))
    else:
        flash(message='Something went wrong!', category='danger')
        return render_template(url_for('index'))


@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    if request.method == 'POST':
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username), category='danger')
            return redirect(url_for('index'))
        elif user == current_user:
            flash('You cannot unfollow yourself!', category='danger')
            return redirect(url_for('profile', username=username))
        else:
            current_user.unfollow(user)
            db.session.commit()
            flash('You are now unfollowing {}.'.format(username), category='success')
            return redirect(url_for('profile', username=username))
    else:
        flash(message='Something went wrong!', category='danger')
        return render_template(url_for('index'))






