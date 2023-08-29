import os

from flask import Flask

from . import auth, blog, db


def create_app(test_config=None):
    # Flaskインスタンスを作成
    app = Flask(__name__, instance_relative_config=True)

    # appが使用する標準設定
    app.config.from_mapping(
        SECRET_KEY = "dev",
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite')
    )

    # config.pyがある場合、標準設定を上書き
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # app.instance_pathが確実に存在するようにする
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/hello")
    def hello():
        return "Hello, world!"
    
    db.init_app(app)
    
    app.register_blueprint(auth.bp)

    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')
    
    return app
