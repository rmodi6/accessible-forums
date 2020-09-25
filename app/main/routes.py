import ast
from datetime import datetime

from flask import render_template, flash, redirect, url_for, request, g, current_app
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
    if current_app.elasticsearch and current_app.elasticsearch.ping():
        # If elasticsearch is running use elasticsearch query with fuzzy match
        threads, total = Thread.search(g.search_form.q.data)
    else:
        # Else use db query with exact match
        threads = Thread.query.filter(Thread.title.like("%{}%".format(g.search_form.q.data))).all()
    return render_template('search.html', threads=threads)


@bp.route('/thread/<thread_id>')
@login_required
def thread(thread_id):
    _thread = Thread.query.filter_by(id=thread_id).first()
    return render_template('thread.html', title=_('Posts in this thread'), posts=_thread.posts)


@bp.route('/tree/<thread_id>')
@login_required
def tree_view(thread_id):
    _thread = Thread.query.filter_by(id=thread_id).first()
    return render_template('tree_view.html', thread=_thread)


@bp.route('/post/<post_id>')
@login_required
def post(post_id):
    _post = Post.query.filter_by(id=post_id).first()
    child_posts = _post.get_children()
    return render_template('post.html', title=_('Search'), child_posts=child_posts, post=_post)


@bp.route('/post/parents/<post_id>')
@login_required
def parent_posts(post_id):
    parent_ids = Post.query.filter_by(id=post_id).first().parent_ids
    parent_ids = ast.literal_eval(parent_ids)
    _parent_posts = Post.query.filter(Post.id.in_(parent_ids)).all()
    return render_template('thread.html', title=_('Parent Posts'), posts=_parent_posts)


@bp.route('/post/siblings/<post_id>')
@login_required
def sibling_posts(post_id):
    _sibling_posts = Post.query.filter_by(id=post_id).first().get_siblings()
    return render_template('thread.html', title=_('Sibling Posts'), posts=_sibling_posts)


@bp.route('/help')
def help():
    return render_template('help.html', title=_('Help'))
