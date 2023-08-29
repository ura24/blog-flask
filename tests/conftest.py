import os
import tempfile

import pytest

from flaskr import create_app
from flaskr.db import get_db, init_db

# テスト用のデータを読み込む
with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')

# Flaskアプリケーションをセットアップするためのフィクスチャ
@pytest.fixture
def app():
    # 一時データベースファイルを作成
    db_fd, db_path = tempfile.mkstemp()

    # テスト用のFlaskアプリケーションを作成
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path
    })

    # アプリケーションコンテキスト内でデータベースの初期化とデータ投入を行う
    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    # テスト終了時に一時ファイルをクローズして削除
    yield app

    os.close(db_fd)
    os.unlink(db_path)

# テストクライアントを提供するためのフィクスチャ
@pytest.fixture
def client(app):
    return app.test_client()

# テストコマンドランナーを提供するためのフィクスチャ
@pytest.fixture
def runner(app):
    return app.test_cli_runner()

class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')

@pytest.fixture
def auth(client):
    return AuthActions(client)
