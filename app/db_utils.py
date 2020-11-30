import ast
import csv
import ctypes as ct
from datetime import datetime

from tqdm import tqdm

from app import db
from app.models import User, Post, Thread, parent_child_post

# csv field limit error fix: https://stackoverflow.com/questions/15063936/csv-error-field-larger-than-field-limit-131072
csv.field_size_limit(int(ct.c_ulong(-1).value // 2))
BATCH_SIZE = 10000


def load_data_from_file(file_name):
    index = 0
    with open(file_name, 'r', encoding="utf8") as f:
        user_ids, post_ids, thread_ids = set(), set(), set()
        for row in tqdm(csv.reader(f)):
            try:
                if index > 0:
                    [thread, date_time, author, post, parent_posts, post_id, default_parent_id, thread_id, author_id,
                     origin_id, label, parent_ids] = row
                    date_time = datetime.fromisoformat(date_time)
                    if not parent_ids.lstrip().startswith('['):
                        parent_ids = '["' + parent_ids + '"]'
                    if author_id not in user_ids:
                        user = User(id=author_id, username=author, email='abc@xyz.com')
                        user.set_password('abc123')
                        db.session.add(user)
                        user_ids.add(author_id)
                    if post_id not in post_ids:
                        post = Post(id=post_id, body=post, timestamp=date_time, user_id=author_id, thread_id=thread_id,
                                    parent_ids=parent_ids, label=label)
                        db.session.add(post)
                        post_ids.add(post_id)
                    if thread_id not in thread_ids:
                        thread = Thread(id=thread_id, title=thread)
                        db.session.add(thread)
                        thread_ids.add(thread_id)
                    if '-1' not in parent_ids:
                        for parent_id in ast.literal_eval(parent_ids):
                            db.engine.execute(parent_child_post.insert().values(parent_id=parent_id, child_id=post_id))

                    if index % BATCH_SIZE == 0:
                        db.session.commit()

            except Exception as e:
                print(e)
            finally:
                index += 1

        db.session.commit()
