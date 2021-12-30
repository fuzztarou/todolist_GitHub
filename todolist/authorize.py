import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

#Blueprintの実装
bp = Blueprint('authorize', __name__, url_prefix='/authorize')

#以下にてBlueprintのViewを作成していく

#url_prefix='/authorize'なので/authorize/registerへのリクエストに戻り値を返す
#登録画面ではGETもPOSTもあり得るので、methodsにはタプルで'GET', 'POST'を設定
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        
        #検証に問題なければINSERT文を発行
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            #エラーがあった場合の処理
            except db.IntegrityError:
                error = f"User {username} is already registered."
            #エラーがなければ authorizeモジュール の loginメソッド へリダイレクト
            else:
                return redirect(url_for("authorize.login"))
        #動的にエラーメッセージを表示
        flash(error)
    #リクエストがGETの場合は authorize/register.html を返すだけ 
    return render_template('authorize/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        #fetchone は結果を1行返す。結果がない場合は None が返ってくる。
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        #userが一致しない    
        if user is None:
            error = '登録されていないユーザー名です'
        #passwordが一致しない
        elif not check_password_hash(user['password'], password):
            error = 'パスワードが間違っています'
        #エラーが無ければセッションをクリアしてからセッションにidを格納
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('list'))

        flash(error)

    return render_template('authorize/login.html')

#user_idが存在する場合はDBからユーザー情報を取得し、存在しない場合はNoneを設定する。
#@bp.before_app_requestで登録されたメソッドはビューメソッド（@bp.routeで登録されたメソッド）
#よりも先に実行されるようになる。
#ここで作成した g.user はログイン状態の確認に使用する。
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

#logoutメソッドはセッションをクリアして、indexメソッドへリダイレクトする。
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('authorize.login'))

#記事の投稿や削除のビューメソッドの前にユーザーがログイン状態であるかを確認する。
#ログイン状態でなければログイン画面にリダイレクトする。 
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('authorize.login'))
        
        return view(**kwargs)

    return wrapped_view





































