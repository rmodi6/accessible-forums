import csv

from tqdm import tqdm

from app import db
from app.models import User, Post, Thread

BATCH_SIZE = 100


def load_data_from_file(file_name):
    index = 0
    with open(file_name, 'r', encoding="utf8") as f:
        user_ids, post_ids, thread_ids = set(), set(), set()
        for row in tqdm(csv.reader(f)):
            try:
                if index > 0:
                    thread, date_time, author, post, parent_posts, post_id, parent_id, thread_id, author_id, origin_id, label = row
                    if author not in user_ids:
                        user = User(id=author_id, username=author, email='abc@xyz.com')
                        user.set_password('abc123')
                        db.session.add(user)
                        user_ids.add(author)
                    if post_id not in post_ids:
                        post = Post(id=post_id, body=post, user_id=author_id, thread_id=thread_id, parent_ids=parent_id,
                                    label=label)
                        db.session.add(post)
                        post_ids.add(post_id)
                    if thread_id not in thread_ids:
                        thread = Thread(id=row[7], title=row[0])
                        db.session.add(thread)
                        thread_ids.add(thread_id)

                    if index % BATCH_SIZE == 0:
                        db.session.commit()

            except Exception as e:
                print(e)
            finally:
                index += 1

        db.session.commit()
