import sqlite3

import click
from flask import current_app, g


# SQLiteデータベースへの接続を取得
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

# データベース接続を閉じる
def close_db(e=None):
    db = g.pop('db', None)
    
    if db is not None:
        db.close()

# データベースを初期化
def init_db():
    db = get_db()
    
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf-8'))

# コマンドラインから実行可能なコマンド 'init-db' を作成
@click.command('init-db')
def init_db_connect():
    init_db()
    click.echo('Initialized the database.')

# Flaskアプリケーションに関連する初期化
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_connect)
