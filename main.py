import glob
import os

import click
from tqdm import tqdm

from app import create_app, db, cli
from app.db_utils import load_users_and_posts, load_threads
from app.models import User, Post

app = create_app()
cli.register(app)


@app.cli.command("db-load")
def load_db():
    """Load existing data into database."""
    click.echo('Loading data into database...')
    file_names = []
    root = os.path.join(app.config['BASE_DIR'], "data")
    for path, subdirs, files in os.walk(root):
        for name in files:
            file_name = os.path.join(path, name)
            if file_name.endswith(".csv"):
                file_names.append(file_name)
    for file_name in tqdm(file_names):
        load_users_and_posts(file_name)
        load_threads(file_name)
    click.echo('Data loaded successfully')


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}
