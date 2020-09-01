import glob
import os

from tqdm import tqdm

from app import create_app, db, cli
from app.db_utils import load_users_and_posts, load_threads
from app.models import User, Post

app = create_app()
cli.register(app)

with app.app_context():
    if app.config['INIT_DB']:
        print('Loading data into database...')
        path = os.path.join(app.config['BASE_DIR'], "data/**/*.csv")
        for file_name in tqdm(glob.glob(path)):
            load_users_and_posts(file_name)
            load_threads(file_name)
        print('Data loaded successfully')


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}
