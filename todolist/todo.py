from flask import(
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from todolist.authorize import login_required
from todolist.db import get_db

import time
import datetime

bp = Blueprint('todo', __name__)


#ログインしたユーザーのアイテムのみ取得する
@bp.route('/todo/list', methods=('GET', 'POST'))
@login_required
def index():
    current_date = datetime.date.today()    #date型
    db = get_db()
    cur = db.cursor()

    # 今日の日付とdeadlineを比較して過ぎていれば judge_date=1 まだなら ０ を代入
    for row in db.execute('SELECT * from item'):
        #SELECT した deadline を deadline に代入
        deadline = datetime.datetime.strptime(row['deadline'], '%Y-%m-%d')  #datetime型
        deadline = deadline.date()  #date型
        #レコードのidを変数に格納
        row_id = row['id']

        #今日の日付とdeadlineを比較
        #　締め切り前　今日<=deadline なら judge_date に 0 を代入
        if current_date < deadline:
            db.execute('UPDATE item SET judge_date = 0'
            ' WHERE id = ?',
            (row_id,)
            )
        #　締め切りを過ぎてる　今日>deadline ならに １ を代入
        elif current_date > deadline:
            db.execute('UPDATE item SET judge_date = 1'
            ' WHERE id = ?',
            (row_id,)
            )
    
    db.commit()

    items = db.execute(
        'SELECT i.id, item_name, deadline, item_status, owner_id, username, created'
        ' FROM item i JOIN user u ON i.owner_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()

    return render_template('todo/list.html', items=items, c_time=current_date)


#アイテム新規登録 ページの処理
@bp.route('/add_item', methods=('GET', 'POST'))
@login_required
def add_item():
    if request.method == 'POST':
        item = request.form['item_name']
        deadline = request.form['deadline']
        error = None

        if not item:
            error = 'Item is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO item (item_name, deadline, owner_id, item_status)'
                ' VALUES (?, ?, ?, ?)',
                (item, deadline, g.user['id'], 0)
            )
            db.commit()
            return redirect(url_for('list'))

    return render_template('todo/add_item.html')


#get_itemを定義してedit_itemビューで使用する
def get_item(id, check_author=True):
    item = get_db().execute(
        'SELECT i.id, item_name, deadline, created, owner_id, username'
        ' FROM item i JOIN user u ON i.owner_id = u.id'
        ' WHERE i.id = ?',
        (id,)
    ).fetchone()

    if item is None:
        abort(404, f"Item id {id} doesn't exist.")
    if check_author and item['owner_id'] != g.user['id']:
        abort(403)
    
    return item

#このビューを呼び出すには引数 id が必要　例：/1/update
@bp.route('/<int:id>/edit_item', methods=('GET', 'POST'))
@login_required
def update(id):
    item = get_item(id)

    if request.method == 'POST':
        item = request.form['item_name']
        deadline = request.form['deadline']
        status = request.form['item_status']

        error = None

        if not item:
            error = 'Item is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE item SET item_name = ?, deadline = ?, item_status = ?'
                ' WHERE id = ?',
                (item, deadline, status, id)
            )
            db.commit()
            return redirect(url_for('list'))

    return render_template('todo/edit_item.html', item=item)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_item(id)
    db = get_db()
    db.execute('DELETE FROM item WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('list'))
