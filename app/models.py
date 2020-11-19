from datetime import datetime
from hashlib import md5
from typing import List

from flask_login import UserMixin
from sqlalchemy import Enum
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login
from app.enums import Label
from app.search import add_to_index, remove_from_index, query_index


class SearchableMixin(object):
    @classmethod
    def search(cls, expression):
        ids, total = query_index(cls.__tablename__, expression)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)

followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(UserMixin, db.Model):
    id = db.Column(db.String, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())


@login.user_loader
def load_user(id):
    return User.query.get(id)


class Post(SearchableMixin, db.Model):
    __searchable__ = ['body']
    id = db.Column(db.String, primary_key=True)
    body = db.Column(db.String(140))
    label = db.Column(Enum(Label))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.String, db.ForeignKey('user.id'))
    thread_id = db.Column(db.String, db.ForeignKey('thread.id'))
    parent_ids = db.Column(db.String(140), index=True)

    def __repr__(self):
        return '<Post {}>'.format(self.body)

    def has_parent(self):
        return '-1' not in self.parent_ids

    def get_parent(self):
        return Post.query.filter(Post.id == self.parent_ids).first() if self.has_parent() else None

    def has_children(self, level=-1):
        return len(self.get_children(level)) > 0

    def get_children(self, level=-1):
        if level == 1:
            # if this is the first post in the thread, include orphan posts in children
            return Post.query.filter(
                (Post.parent_ids == self.id) |
                (
                        (Post.id != self.id) &
                        (Post.thread_id == self.thread_id) &
                        (Post.parent_ids.like("%-1"))
                )
            ).all()
        else:
            # else only include children posts
            return Post.query.filter_by(parent_ids=self.id).all()

    def get_siblings(self):
        siblings = Post.query.filter_by(parent_ids=self.parent_ids).all()
        return list(siblings)

    def is_question_post(self):
        return self.label in Label.question_types()

    def get_verb(self):
        return 'asked' if self.is_question_post() else 'said'

    def display_body(self, maxlen=None):
        if maxlen and len(self.body) > maxlen:
            return self.body[:maxlen] + '...'
        return self.body if self.body.rstrip().endswith(('.', '!', '?')) else self.body + '.'

    def get_tree(self):
        node = TreeNode(val=self)
        for child in self.get_children():
            child_node = child.get_subtree()
            node.children.append(child_node)
        parent = self.get_parent()
        while parent:
            parent_node = TreeNode(val=parent, children=[node])
            node = parent_node
            parent = node.val.get_parent()
        return node

    def get_subtree(self):
        node = TreeNode(val=self)
        for child in self.get_children():
            child_node = child.get_subtree()
            node.children.append(child_node)
        return node


class Thread(SearchableMixin, db.Model):
    __searchable__ = ['title']
    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String(140))
    posts: List[Post] = db.relationship('Post', backref='thread', lazy='dynamic')

    def __repr__(self):
        return '<Thread {}>'.format(self.title)

    def get_question_posts(self):
        question_posts = [post for post in self.posts if post.is_question_post()]
        if len(question_posts) == 0:
            question_posts.append(self.posts[0])
        return question_posts

    def display_title(self):
        return self.title if self.title.rstrip().endswith(('.', '!', '?')) else self.title + '.'

    def get_tree(self):
        return self.posts[0].get_subtree()


class TreeNode:
    """
        Helper class to generate a tree node
    """

    def __init__(self, val=None, children=None):
        if children is None:
            children = []
        self.val = val
        self.children = children
