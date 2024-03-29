import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

"""
gはリクエスト米に生成されるユニークなオブジェクト
同じリクエスト内では使い回す。
sqlite3.Rowは行を辞書型のように返して、列名で指定できるようにする
"""
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

#init-dbでinit_db_commandを呼び出す独自のflaskrコマンドを作成
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")

#これをアプリに登録
def init_app(app):
    app.teardown_appcontext(close_db)    #レスポンスを返した後に()内の関数を呼び出す
    app.cli.add_command(init_db_command) #flaskコマンドから呼び出せるようにする

