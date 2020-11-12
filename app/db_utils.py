import csv

from tqdm import tqdm

from app import db
from app.models import User, Post, Thread


def load_data_from_file(file_name):
    index = 0
    with open(file_name, 'r', encoding="utf8") as f:
        for row in tqdm(csv.reader(f)):
            try:
                if index > 0:
                    existing_user = User.query.filter_by(username=row[2]).first()
                    if existing_user is None:
                        user = User(id=row[8], username=row[2], email='abc' + str(index) + '@xyz.com')
                        user.set_password('abc12345')
                        db.session.add(user)
                        db.session.commit()
                    existing_post = Post.query.filter_by(id=row[5]).first()
                    if existing_post is None:
                        post = Post(id=row[5], body=row[3], user_id=row[8], thread_id=row[7], parent_ids=row[6],
                                    label=row[10])
                        db.session.add(post)
                        db.session.commit()
                    existing_thread = Thread.query.filter_by(id=row[7]).first()
                    if existing_thread is None:
                        thread = Thread(id=row[7], title=row[0])
                        db.session.add(thread)
                        db.session.commit()
            except Exception as e:
                print(e)
            finally:
                index += 1
