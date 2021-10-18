import os
from flask import Flask, redirect

def create_app(test_config=None):
    # create and configre the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'todolist.sqlite'),      
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        # testではない場合に、config.pyが存在すれば読み込む
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        # テストの設定を読み込む
        app.config.from_mapping(test_config)
    
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return ('Hello, World!')

    @app.route('/')
    def redirect_route():
        return redirect('authorize/login')

    from . import db
    db.init_app(app)

    #Blueprintの登録
    from . import authorize
    app.register_blueprint(authorize.bp) 

    from . import todo
    app.register_blueprint(todo.bp)
    #url_for('list') は '/todo/list' に変換される。loginビュー と logoutビュー
    app.add_url_rule('/todo/list', endpoint='list')

    return app