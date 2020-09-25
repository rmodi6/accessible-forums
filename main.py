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
    path = os.path.join(app.config['BASE_DIR'], "data/**/*.csv")
    for file_name in tqdm(glob.glob(path)):
        load_users_and_posts(file_name)
        load_threads(file_name)
    click.echo('Data loaded successfully')


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}
