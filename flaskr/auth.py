import functools

from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        
        # ユーザ名とパスワードの入力チェック
        if not username:
            error = 'Username is required'
        elif not password:
            error = 'Password is required'
        
        # エラーがない場合、データベースにユーザを追加
        if error is None:
            try:
                db.execute(
                    'INSERT INTO user(username, password) VALUES(?, ?)',
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                # 重複エラーが発生した場合
                error = f"User {username} is already registered."
            else:
                # ユーザが正常に追加された場合、ログインページにリダイレクト
                return redirect(url_for('auth.login'))
            
        # エラーメッセージをフラッシュ
        flash(error)
    
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        
        # ユーザ情報の取得
        user = db.execute(
            'SELECT id, username, password FROM user WHERE username = ?', (username)
        ).fetchone()
        
        # ユーザの存在とパスワードの一致を確認
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        
        # エラーがない場合、セッションにユーザIDを格納してリダイレクト
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        
        # エラーメッセージをフラッシュ
        flash(error)
    
    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    # セッションからユーザIDを取得
    user_id = session.get('user_id')

    # ユーザIDが存在しない場合、gオブジェクトにユーザ情報を設定しない
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT id, username, password FROM user WHERE id = ?', (user_id)
        ).fetchone()

@bp.route('/logout')
def logout():
    # セッションをクリアしてログアウト
    session.clear()
    return redirect(url_for('index'))

# ログインが必要なビューを保護するデコレータ関数
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        # ユーザがログインしていない場合、ログインページにリダイレクト
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    
    return wrapped_view
