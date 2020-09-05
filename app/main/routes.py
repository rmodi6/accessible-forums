import ast
from datetime import datetime

from flask import render_template, flash, redirect, url_for, request, g
from flask_babel import _, get_locale
from flask_login import current_user, login_required

from app import db
from app.main import bp
from app.main.forms import EditProfileForm, EmptyForm, PostForm, SearchForm
from app.models import User, Post, Thread


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('main.index'))
    posts = current_user.followed_posts()
    return render_template('index.html', title=_('Home'), form=form, posts=posts)


@bp.route('/explore')
@login_required
def explore():
    posts = Post.query.order_by(Post.timestamp.desc())
    return render_template('index.html', title=_('Explore'), posts=posts)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.timestamp.desc())
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts, form=form)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'),
                           form=form)


@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash(_('You cannot follow yourself!'))
            return redirect(url_for('main.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(_('You are following %(username)s!', username=username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash(_('You cannot unfollow yourself!'))
            return redirect(url_for('main.user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(_('You are not following %(username)s.', username=username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    threads, total = Thread.search(g.search_form.q.data)
    return render_template('search.html', title=_('Forum threads that match your search'), threads=threads)


@bp.route('/searchPosts/<threadId>')
@login_required
def searchPosts(threadId):
    thread_title = Thread.query.filter_by(id=threadId).first().title
    posts, total = Post.search(threadId)
    title = 'Thread : ' + thread_title
    return render_template('searchPosts.html', title=_(title), posts=posts)


@bp.route('/parentPosts/<id>')
@login_required
def parentPosts(id):
    parent_ids = Post.query.filter_by(id=id).first().parent_ids
    parent_ids_list = ast.literal_eval(parent_ids)
    posts = []
    for p_ids in parent_ids_list:
        posts.append(Post.query.filter_by(id=p_ids).first())
    return render_template('searchPosts.html', title=_('Parent Posts'), posts=posts)


@bp.route('/childPosts/<postId>')
@login_required
def childPosts(postId):
    parent_post = Post.query.filter_by(id=postId).first()
    posts, total = Post.search(postId)
    return render_template('searchChildPosts.html', title=_('Search'), posts=posts, parentPost=[parent_post])


@bp.route('/help')
def help():
    return render_template('help.html', title=_('Help'))
