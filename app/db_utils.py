import csv
import sys

from app import db
from app.models import User, Post, Thread

csv.field_size_limit(sys.maxsize)


def load_users_and_posts(file_name):
    index = 0
    with open(file_name, 'r', encoding="utf8") as f:
        for row in csv.reader(f):
            try:
                if index > 0:
                    existing_user = User.query.filter_by(username=row[2]).first()
                    if existing_user is None:
                        user = User(username=row[2], email='abc' + str(index) + '@xyz.com', id=row[8])
                        user.set_password('abc12345')
                        db.session.add(user)
                        db.session.commit()
                    existing_post = Post.query.filter_by(id=row[5]).first()
                    if existing_post is None:
                        post = Post(body=row[3], author=User.query.filter_by(username=row[2]).first(), id=row[5],
                                    thread_id=row[7], parent_ids=str([row[6]]), label=row[10])
                        db.session.add(post)
                        db.session.commit()
            except Exception as e:
                print(e)
            finally:
                index += 1


def load_threads(file_name):
    index = 0
    with open(file_name, 'r', encoding="utf8") as f:
        for row in csv.reader(f):
            try:
                if index > 0:
                    existing_thread = Thread.query.filter_by(id=row[7]).first()
                    if existing_thread is None:
                        all_posts = Post.query.filter_by(thread_id=row[7]).all()
                        thread = Thread(id=row[7], title=row[0], posts=all_posts)
                        db.session.add(thread)
                        db.session.commit()
            except Exception as e:
                print(e)
            finally:
                index += 1
